import re
import email
import email.policy
import dns.resolver
import requests
from email.header import decode_header
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

URGENCY_WORDS = [
    'urgent', 'immediately', 'action required', 'account suspended', 'verify now',
    'limited time', 'expires', 'warning', 'critical', 'important notice',
    'act now', 'final notice', 'last chance', 'confirm identity', 'unusual activity'
]

SUSPICIOUS_ATTACHMENT_EXTS = [
    '.exe', '.bat', '.cmd', '.scr', '.pif', '.vbs', '.js', '.jar',
    '.ps1', '.reg', '.msi', '.com', '.hta', '.wsf', '.lnk'
]


def analyze_email_text(raw_email: str) -> dict:
    result = {
        'threat_score': 0,
        'risk_level': 'safe',
        'sender_analysis': {},
        'header_analysis': {},
        'auth_checks': {},
        'content_analysis': {},
        'attachments': [],
        'links': [],
        'findings': [],
        'recommendations': []
    }

    try:
        msg = email.message_from_string(raw_email, policy=email.policy.default)
    except Exception as e:
        result['findings'].append(f'Failed to parse email: {e}')
        return result

    # 1. Sender Analysis
    sender = msg.get('From', '')
    reply_to = msg.get('Reply-To', '')
    result['sender_analysis'] = _analyze_sender(sender, reply_to)

    if result['sender_analysis'].get('mismatch'):
        result['threat_score'] += 30
        result['findings'].append('Reply-To address differs from sender — common phishing trick.')
    if result['sender_analysis'].get('free_email_impersonation'):
        result['threat_score'] += 25
        result['findings'].append('Sender uses free email to impersonate a company.')

    # 2. Header Analysis
    result['header_analysis'] = _analyze_headers(msg)
    if result['header_analysis'].get('received_count', 0) > 10:
        result['threat_score'] += 10
        result['findings'].append('Email passed through many servers — may indicate spoofing relay.')

    # 3. SPF / DKIM / DMARC checks
    sender_domain = _extract_domain(sender)
    result['auth_checks'] = _check_email_auth(sender_domain)

    if not result['auth_checks']['spf']['pass']:
        result['threat_score'] += 20
        result['findings'].append(f"SPF check failed for domain '{sender_domain}'.")
    if not result['auth_checks']['dkim']['pass']:
        result['threat_score'] += 20
        result['findings'].append(f"DKIM check failed for domain '{sender_domain}'.")
    if not result['auth_checks']['dmarc']['exists']:
        result['threat_score'] += 15
        result['findings'].append(f"No DMARC record found for '{sender_domain}'.")

    # 4. Content Analysis
    body = _get_email_body(msg)
    result['content_analysis'] = _analyze_content(body)

    if result['content_analysis']['urgency_score'] >= 3:
        result['threat_score'] += 20
        result['findings'].append(f"High urgency language detected: {', '.join(result['content_analysis']['urgency_words'][:3])}")
    elif result['content_analysis']['urgency_score'] >= 1:
        result['threat_score'] += 10

    if result['content_analysis']['has_credential_request']:
        result['threat_score'] += 25
        result['findings'].append('Email requests credentials, passwords, or personal information.')

    # 5. Links Analysis
    result['links'] = _extract_links(body, raw_email)
    suspicious_links = [l for l in result['links'] if l.get('suspicious')]
    if suspicious_links:
        result['threat_score'] += min(len(suspicious_links) * 15, 30)
        result['findings'].append(f'{len(suspicious_links)} suspicious link(s) detected in email body.')

    # 6. Attachments
    result['attachments'] = _analyze_attachments(msg)
    dangerous_attachments = [a for a in result['attachments'] if a.get('dangerous')]
    if dangerous_attachments:
        result['threat_score'] += 40
        result['findings'].append(f"Dangerous attachment detected: {', '.join(a['name'] for a in dangerous_attachments)}")

    # Cap and classify
    result['threat_score'] = min(result['threat_score'], 100)
    if result['threat_score'] >= 65:
        result['risk_level'] = 'dangerous'
        result['recommendations'].append('Do NOT click any links or open attachments.')
        result['recommendations'].append('Report as phishing to your email provider.')
        result['recommendations'].append('Delete this email immediately.')
    elif result['threat_score'] >= 35:
        result['risk_level'] = 'suspicious'
        result['recommendations'].append('Be cautious — verify the sender through official channels.')
        result['recommendations'].append('Do not provide personal information.')
    else:
        result['risk_level'] = 'safe'
        result['recommendations'].append('Email appears legitimate. Always stay vigilant.')

    return result


def _analyze_sender(sender: str, reply_to: str) -> dict:
    info = {'raw': sender, 'reply_to': reply_to, 'mismatch': False, 'free_email_impersonation': False}
    sender_domain = _extract_domain(sender)
    reply_domain = _extract_domain(reply_to) if reply_to else ''
    free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'protonmail.com']
    company_keywords = ['bank', 'paypal', 'amazon', 'apple', 'microsoft', 'google', 'netflix', 'support', 'noreply', 'security']

    if reply_to and reply_domain and sender_domain != reply_domain:
        info['mismatch'] = True

    if sender_domain in free_domains:
        display_name = sender.lower()
        if any(kw in display_name for kw in company_keywords):
            info['free_email_impersonation'] = True

    info['domain'] = sender_domain
    return info


def _extract_domain(email_str: str) -> str:
    match = re.search(r'@([\w.-]+)', email_str)
    return match.group(1).lower() if match else ''


def _analyze_headers(msg) -> dict:
    received = msg.get_all('Received', [])
    x_mailer = msg.get('X-Mailer', '')
    x_spam = msg.get('X-Spam-Status', '')
    return {
        'received_count': len(received),
        'x_mailer': x_mailer,
        'x_spam_status': x_spam,
        'has_message_id': bool(msg.get('Message-ID')),
        'has_date': bool(msg.get('Date')),
    }


def _check_email_auth(domain: str) -> dict:
    result = {
        'spf': {'pass': False, 'record': None},
        'dkim': {'pass': False, 'record': None},
        'dmarc': {'exists': False, 'record': None}
    }
    if not domain:
        return result

    # SPF
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if txt.startswith('v=spf1'):
                result['spf']['pass'] = True
                result['spf']['record'] = txt[:200]
                break
    except Exception:
        pass

    # DMARC
    try:
        answers = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if txt.startswith('v=DMARC1'):
                result['dmarc']['exists'] = True
                result['dmarc']['record'] = txt[:200]
                break
    except Exception:
        pass

    # DKIM (check common selector)
    try:
        answers = dns.resolver.resolve(f'default._domainkey.{domain}', 'TXT')
        for rdata in answers:
            result['dkim']['pass'] = True
            result['dkim']['record'] = rdata.to_text()[:200]
            break
    except Exception:
        pass

    return result


def _get_email_body(msg) -> str:
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype in ('text/plain', 'text/html'):
                try:
                    body += part.get_payload(decode=True).decode(errors='replace')
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors='replace')
        except Exception:
            body = str(msg.get_payload())
    return body


def _analyze_content(body: str) -> dict:
    body_lower = body.lower()
    found_urgency = [w for w in URGENCY_WORDS if w in body_lower]
    has_credential = any(phrase in body_lower for phrase in [
        'enter your password', 'verify your account', 'click here to login',
        'confirm your details', 'update your information', 'provide your credentials'
    ])
    return {
        'urgency_score': len(found_urgency),
        'urgency_words': found_urgency,
        'has_credential_request': has_credential,
        'word_count': len(body.split()),
    }


def _extract_links(body: str, raw_email: str) -> list:
    links = []
    soup = BeautifulSoup(body, 'html.parser')
    seen = set()
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        display = tag.get_text(strip=True)
        if href in seen:
            continue
        seen.add(href)
        suspicious = False
        reasons = []
        if href.startswith('http') and display and display.startswith('http'):
            if href != display:
                suspicious = True
                reasons.append('URL mismatch with display text')
        if any(s in href for s in ['bit.ly', 'tinyurl', 'goo.gl']):
            suspicious = True
            reasons.append('Short URL')
        links.append({'url': href[:300], 'display': display[:100], 'suspicious': suspicious, 'reasons': reasons})
    return links


def _analyze_attachments(msg) -> list:
    attachments = []
    for part in msg.walk():
        disposition = str(part.get('Content-Disposition', ''))
        if 'attachment' in disposition:
            filename = part.get_filename() or 'unknown'
            ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            dangerous = ext in SUSPICIOUS_ATTACHMENT_EXTS
            attachments.append({
                'name': filename,
                'extension': ext,
                'content_type': part.get_content_type(),
                'dangerous': dangerous
            })
    return attachments
