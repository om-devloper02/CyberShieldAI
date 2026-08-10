import re
import ssl
import socket
import hashlib
import requests
import whois
import tldextract
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

SUSPICIOUS_KEYWORDS = [
    'login', 'signin', 'verify', 'account', 'secure', 'update', 'confirm',
    'banking', 'paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
    'password', 'credential', 'wallet', 'bitcoin', 'crypto', 'prize', 'winner',
    'urgent', 'suspended', 'blocked', 'limited', 'alert', 'notification'
]

SHORT_URL_DOMAINS = [
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'buff.ly',
    'adf.ly', 'shorte.st', 'is.gd', 'cli.gs', 'yfrog.com', 'migre.me',
    'ff.im', 'tiny.cc', 'url4.eu', 'tr.im', 'twit.ac', 'su.pr', 'twurl.nl'
]

KNOWN_BRANDS = [
    'paypal', 'amazon', 'google', 'facebook', 'apple', 'microsoft',
    'netflix', 'instagram', 'twitter', 'linkedin', 'ebay', 'bank',
    'chase', 'citibank', 'wellsfargo', 'hdfc', 'icici', 'sbi'
]


def analyze_url(url: str, google_api_key: str = '') -> dict:
    result = {
        'url': url,
        'risk_score': 0,
        'risk_level': 'safe',
        'checks': {},
        'findings': [],
        'recommendations': []
    }

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
        result['url'] = url

    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace('www.', '')
    ext = tldextract.extract(url)

    # 1. HTTPS Check
    https_check = url.startswith('https://')
    result['checks']['https'] = https_check
    if not https_check:
        result['risk_score'] += 20
        result['findings'].append('No HTTPS encryption — data transmitted in plain text.')
        result['recommendations'].append('Only use websites with HTTPS.')

    # 2. SSL Certificate
    ssl_info = _check_ssl(domain)
    result['checks']['ssl'] = ssl_info
    if not ssl_info.get('valid'):
        result['risk_score'] += 25
        result['findings'].append(f"SSL certificate issue: {ssl_info.get('error', 'unknown')}")

    # 3. Domain Age
    domain_info = _check_domain_age(domain)
    result['checks']['domain_age'] = domain_info
    if domain_info.get('days_old', 365) < 30:
        result['risk_score'] += 30
        result['findings'].append(f"Domain is very new ({domain_info.get('days_old', 0)} days old) — common in phishing.")
    elif domain_info.get('days_old', 365) < 180:
        result['risk_score'] += 10
        result['findings'].append(f"Domain is relatively new ({domain_info.get('days_old', 0)} days old).")

    # 4. Short URL
    is_short = any(s in domain for s in SHORT_URL_DOMAINS)
    result['checks']['short_url'] = is_short
    if is_short:
        result['risk_score'] += 20
        result['findings'].append('Short URL detected — real destination is hidden.')
        result['recommendations'].append('Expand short URLs before clicking.')

    # 5. Typosquatting
    typo = _check_typosquatting(ext.domain)
    result['checks']['typosquatting'] = typo
    if typo.get('detected'):
        result['risk_score'] += 35
        result['findings'].append(f"Possible typosquatting of '{typo['target']}' detected.")

    # 6. Homograph Detection
    homograph = _check_homograph(domain)
    result['checks']['homograph'] = homograph
    if homograph:
        result['risk_score'] += 40
        result['findings'].append('Homograph attack detected — domain uses lookalike Unicode characters.')

    # 7. Suspicious Keywords in URL
    keyword_hits = [kw for kw in SUSPICIOUS_KEYWORDS if kw in url.lower()]
    result['checks']['suspicious_keywords'] = keyword_hits
    if len(keyword_hits) >= 3:
        result['risk_score'] += 20
        result['findings'].append(f"Multiple suspicious keywords found: {', '.join(keyword_hits[:5])}")
    elif keyword_hits:
        result['risk_score'] += 5

    # 8. IP Address URL
    ip_url = bool(re.match(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url))
    result['checks']['ip_url'] = ip_url
    if ip_url:
        result['risk_score'] += 30
        result['findings'].append('URL uses IP address instead of domain name — suspicious.')

    # 9. Excessive Subdomains
    subdomain_count = len(ext.subdomain.split('.')) if ext.subdomain else 0
    result['checks']['subdomain_count'] = subdomain_count
    if subdomain_count > 3:
        result['risk_score'] += 15
        result['findings'].append(f'Excessive subdomains ({subdomain_count}) — common phishing tactic.')

    # 10. URL Length
    url_length = len(url)
    result['checks']['url_length'] = url_length
    if url_length > 100:
        result['risk_score'] += 10
        result['findings'].append(f'Unusually long URL ({url_length} chars) — may contain hidden redirects.')

    # 11. Special Characters
    special_chars = len(re.findall(r'[@%=?&]{2,}', url))
    result['checks']['special_chars'] = special_chars
    if special_chars > 3:
        result['risk_score'] += 10
        result['findings'].append('Excessive special characters in URL.')

    # 12. Page Content Analysis
    content_check = _analyze_page_content(url)
    result['checks']['page_content'] = content_check
    if content_check.get('suspicious_forms'):
        result['risk_score'] += 25
        result['findings'].append('Suspicious login form detected that may harvest credentials.')
    if content_check.get('hidden_redirects'):
        result['risk_score'] += 20
        result['findings'].append('Hidden redirect scripts detected.')

    # 13. Google Safe Browsing
    if google_api_key:
        gsb = _check_google_safe_browsing(url, google_api_key)
        result['checks']['google_safe_browsing'] = gsb
        if gsb.get('threat_found'):
            result['risk_score'] += 50
            result['findings'].append(f"Google Safe Browsing flagged this URL: {gsb.get('threat_type')}")

    # Cap score at 100
    result['risk_score'] = min(result['risk_score'], 100)

    # Determine risk level
    if result['risk_score'] >= 65:
        result['risk_level'] = 'dangerous'
    elif result['risk_score'] >= 35:
        result['risk_level'] = 'suspicious'
    else:
        result['risk_level'] = 'safe'

    if not result['recommendations']:
        if result['risk_level'] == 'safe':
            result['recommendations'].append('Website appears safe. Always stay cautious online.')
        else:
            result['recommendations'].append('Do not enter personal or financial information on this website.')
            result['recommendations'].append('Report this website to Google Safe Browsing if confirmed phishing.')

    return result


def _check_ssl(domain: str) -> dict:
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
        conn.settimeout(5)
        conn.connect((domain, 443))
        cert = conn.getpeercert()
        conn.close()
        expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_left = (expire_date - datetime.utcnow()).days
        return {
            'valid': True,
            'expires': expire_date.strftime('%Y-%m-%d'),
            'days_left': days_left,
            'issuer': dict(x[0] for x in cert.get('issuer', [])).get('organizationName', 'Unknown')
        }
    except ssl.SSLCertVerificationError as e:
        return {'valid': False, 'error': 'Certificate verification failed'}
    except Exception as e:
        return {'valid': False, 'error': str(e)[:100]}


def _check_domain_age(domain: str) -> dict:
    try:
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation:
            if creation.tzinfo:
                now = datetime.now(timezone.utc)
            else:
                now = datetime.utcnow()
            days_old = (now - creation).days
            return {'days_old': days_old, 'created': str(creation)[:10], 'registrar': w.registrar}
    except Exception as e:
        logger.debug(f"WHOIS error for {domain}: {e}")
    return {'days_old': 365, 'created': 'Unknown', 'registrar': 'Unknown'}


def _check_typosquatting(domain_name: str) -> dict:
    domain_lower = domain_name.lower()
    for brand in KNOWN_BRANDS:
        if brand != domain_lower and brand in domain_lower:
            return {'detected': True, 'target': brand}
        # Simple edit distance check
        if _levenshtein(domain_lower, brand) <= 2 and len(brand) > 4:
            return {'detected': True, 'target': brand}
    return {'detected': False}


def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def _check_homograph(domain: str) -> bool:
    try:
        domain.encode('ascii')
        return False
    except UnicodeEncodeError:
        return True


def _analyze_page_content(url: str) -> dict:
    result = {'suspicious_forms': False, 'hidden_redirects': False, 'external_links': 0}
    try:
        resp = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
        soup = BeautifulSoup(resp.text, 'html.parser')

        forms = soup.find_all('form')
        for form in forms:
            action = form.get('action', '')
            inputs = form.find_all('input', {'type': ['password', 'text', 'email']})
            if inputs and ('login' in action.lower() or 'signin' in action.lower() or not action):
                result['suspicious_forms'] = True

        scripts = soup.find_all('script')
        for script in scripts:
            content = script.string or ''
            if 'window.location' in content or 'document.location' in content:
                result['hidden_redirects'] = True

        parsed = urlparse(url)
        links = soup.find_all('a', href=True)
        external = sum(1 for l in links if parsed.netloc not in l['href'] and l['href'].startswith('http'))
        result['external_links'] = external

    except Exception as e:
        logger.debug(f"Content analysis error: {e}")
    return result


def _check_google_safe_browsing(url: str, api_key: str) -> dict:
    try:
        endpoint = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}'
        payload = {
            'client': {'clientId': 'cybershield', 'clientVersion': '1.0'},
            'threatInfo': {
                'threatTypes': ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'],
                'platformTypes': ['ANY_PLATFORM'],
                'threatEntryTypes': ['URL'],
                'threatEntries': [{'url': url}]
            }
        }
        resp = requests.post(endpoint, json=payload, timeout=10)
        data = resp.json()
        if data.get('matches'):
            match = data['matches'][0]
            return {'threat_found': True, 'threat_type': match.get('threatType')}
        return {'threat_found': False}
    except Exception as e:
        return {'threat_found': False, 'error': str(e)[:100]}


def analyze_qr_code(image_path: str) -> dict:
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
        img = Image.open(image_path)
        decoded = decode(img)
        if decoded:
            qr_data = decoded[0].data.decode('utf-8')
            if qr_data.startswith('http'):
                url_result = analyze_url(qr_data)
                return {'found': True, 'data': qr_data, 'url_analysis': url_result}
            return {'found': True, 'data': qr_data, 'url_analysis': None}
        return {'found': False, 'data': None}
    except Exception as e:
        return {'found': False, 'error': str(e)}
