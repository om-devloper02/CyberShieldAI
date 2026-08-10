import os
import re
import math
import logging
import json
import tldextract
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class URLClassifier:
    """Rule-based + ML URL phishing classifier."""

    PHISHING_TLDS = {'.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.top', '.xyz', '.click', '.link'}
    BRAND_KEYWORDS = ['paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
                      'instagram', 'netflix', 'bank', 'secure', 'account', 'login', 'verify']

    def predict(self, url: str) -> dict:
        features = self._extract_features(url)
        score = self._score_features(features)
        label = 'phishing' if score >= 0.5 else 'legitimate'
        confidence = round(min(score * 100, 99) if label == 'phishing' else (1 - score) * 100, 1)
        return {
            'label': label,
            'confidence': confidence,
            'phishing_probability': round(score * 100, 1),
            'features': features
        }

    def _extract_features(self, url: str) -> dict:
        ext = tldextract.extract(url)
        parsed = urlparse(url if url.startswith('http') else 'http://' + url)
        domain = parsed.netloc.lower()

        return {
            'url_length': len(url),
            'domain_length': len(domain),
            'has_https': url.startswith('https'),
            'num_dots': url.count('.'),
            'num_hyphens': url.count('-'),
            'num_at': url.count('@'),
            'num_special': len(re.findall(r'[%=?&]', url)),
            'has_ip': bool(re.match(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url)),
            'suspicious_tld': ('.' + ext.suffix) in self.PHISHING_TLDS if ext.suffix else False,
            'brand_in_subdomain': any(b in ext.subdomain.lower() for b in self.BRAND_KEYWORDS),
            'brand_in_path': any(b in parsed.path.lower() for b in self.BRAND_KEYWORDS),
            'path_depth': len([p for p in parsed.path.split('/') if p]),
            'has_redirect': '//' in parsed.path or '%2F%2F' in url,
            'subdomain_count': len(ext.subdomain.split('.')) if ext.subdomain else 0,
        }

    def _score_features(self, f: dict) -> float:
        score = 0.0
        if f['url_length'] > 75: score += 0.1
        if f['url_length'] > 100: score += 0.1
        if not f['has_https']: score += 0.15
        if f['has_ip']: score += 0.25
        if f['suspicious_tld']: score += 0.2
        if f['brand_in_subdomain']: score += 0.25
        if f['brand_in_path']: score += 0.1
        if f['num_hyphens'] > 2: score += 0.1
        if f['num_dots'] > 4: score += 0.1
        if f['num_at'] > 0: score += 0.2
        if f['subdomain_count'] > 3: score += 0.1
        if f['has_redirect']: score += 0.15
        if f['num_special'] > 5: score += 0.1
        return min(score, 1.0)


class EmailClassifier:
    """Rule-based email spam/phishing classifier."""

    SPAM_PATTERNS = [
        r'(?i)(urgent|act now|limited time|click here|verify your|suspend)',
        r'(?i)(free money|win a prize|lottery|inheritance|million dollar)',
        r'(?i)(your account (has been|will be) (suspended|closed|limited))',
        r'(?i)(confirm your (identity|password|email|account))',
        r'(?i)(unusual (sign-in|activity|login) detected)',
        r'(?i)(update your (payment|billing|credit card) information)',
    ]

    def predict(self, subject: str, body: str, sender: str = '') -> dict:
        text = f"{subject} {body} {sender}".lower()
        matches = []
        score = 0.0

        for pattern in self.SPAM_PATTERNS:
            if re.search(pattern, text):
                matches.append(pattern[4:30])
                score += 0.18

        # Additional signals
        if text.count('http') > 5:
            score += 0.1
        if re.search(r'[A-Z]{5,}', subject or ''):
            score += 0.1
        if '!!!' in text or '???' in text:
            score += 0.05

        score = min(score, 1.0)
        label = 'phishing' if score >= 0.4 else 'legitimate'

        return {
            'label': label,
            'confidence': round((score if label == 'phishing' else 1 - score) * 100, 1),
            'phishing_probability': round(score * 100, 1),
            'matched_patterns': matches
        }


class ScamMessageClassifier:
    """Classifies SMS/WhatsApp/Telegram scam messages."""

    SCAM_INDICATORS = {
        'prize_scam': ['congratulations', 'you have won', 'claim your prize', 'lottery winner'],
        'bank_scam': ['your account is blocked', 'kyc update', 'bank alert', 'debit card blocked'],
        'investment_scam': ['guaranteed returns', 'double your money', 'risk free investment', 'crypto profit'],
        'job_scam': ['work from home', 'earn daily', 'part time job', 'data entry job'],
        'courier_scam': ['your parcel is held', 'delivery failed', 'customs fee', 'package detained'],
        'upi_scam': ['send money to receive money', 'collect gift', 'upi cashback', 'scan to receive'],
        'otp_scam': ['share your otp', 'verify your number', 'customer care', 'refund process'],
    }

    def predict(self, message: str) -> dict:
        msg_lower = message.lower()
        detected_types = {}
        total_score = 0.0

        for scam_type, keywords in self.SCAM_INDICATORS.items():
            hits = [kw for kw in keywords if kw in msg_lower]
            if hits:
                detected_types[scam_type] = hits
                total_score += len(hits) * 0.15

        has_url = bool(re.search(r'https?://\S+', message))
        has_phone = bool(re.search(r'\b[6-9]\d{9}\b', message))
        has_urgency = bool(re.search(r'(?i)(urgent|immediately|now|today only|expire)', message))

        if has_url: total_score += 0.1
        if has_urgency: total_score += 0.15

        total_score = min(total_score, 1.0)
        label = 'scam' if total_score >= 0.3 else 'legitimate'

        return {
            'label': label,
            'confidence': round((total_score if label == 'scam' else 1 - total_score) * 100, 1),
            'scam_probability': round(total_score * 100, 1),
            'detected_types': detected_types,
            'has_url': has_url,
            'has_phone': has_phone,
            'has_urgency': has_urgency
        }


class ThreatExplainer:
    """Generates human-readable explanations for detected threats."""

    EXPLANATIONS = {
        'phishing': "Phishing is a cyberattack where attackers impersonate trusted entities to steal credentials or personal information.",
        'malware': "Malware is malicious software designed to damage, disrupt, or gain unauthorized access to systems.",
        'sql_injection': "SQL Injection exploits vulnerabilities in database queries by inserting malicious SQL code.",
        'xss': "Cross-Site Scripting (XSS) injects malicious scripts into web pages viewed by other users.",
        'csrf': "CSRF tricks users into performing unwanted actions on websites where they're authenticated.",
        'brute_force': "Brute force attacks try every possible password combination until the correct one is found.",
        'mitm': "Man-in-the-Middle attacks intercept communication between two parties without their knowledge.",
        'dns_spoofing': "DNS Spoofing redirects users to malicious websites by corrupting DNS cache entries.",
        'ddos': "DDoS floods a server with traffic to make it unavailable to legitimate users.",
        'ransomware': "Ransomware encrypts victim's files and demands payment for the decryption key.",
    }

    MITIGATIONS = {
        'phishing': ['Verify sender identity', 'Check URL before clicking', 'Enable 2FA', 'Use email filtering'],
        'malware': ['Keep antivirus updated', 'Scan downloads', 'Avoid suspicious attachments', 'Regular backups'],
        'sql_injection': ['Use parameterized queries', 'Input validation', 'Least privilege DB access', 'WAF deployment'],
        'xss': ['Output encoding', 'Content Security Policy', 'Input sanitization', 'HTTPOnly cookies'],
        'csrf': ['CSRF tokens', 'SameSite cookies', 'Verify Origin headers', 'Re-authentication for sensitive actions'],
        'brute_force': ['Account lockout policy', 'Strong password policy', 'MFA', 'CAPTCHA', 'Rate limiting'],
        'mitm': ['Use HTTPS', 'Certificate pinning', 'VPN on public WiFi', 'HSTS headers'],
        'dns_spoofing': ['DNSSEC', 'Encrypted DNS (DoH/DoT)', 'Monitor DNS responses', 'Trusted DNS servers'],
        'ddos': ['Rate limiting', 'CDN protection', 'Traffic filtering', 'DDoS mitigation service'],
        'ransomware': ['Regular backups (3-2-1 rule)', 'Email filtering', 'Patch management', 'User awareness training'],
    }

    def explain(self, threat_type: str) -> dict:
        threat_key = threat_type.lower().replace(' ', '_').replace('-', '_')
        return {
            'threat_type': threat_type,
            'explanation': self.EXPLANATIONS.get(threat_key, f'{threat_type} is a cyber security threat.'),
            'mitigations': self.MITIGATIONS.get(threat_key, ['Follow security best practices', 'Keep systems updated']),
            'severity': self._get_severity(threat_key),
            'mitre_tactic': self._get_mitre(threat_key)
        }

    def _get_severity(self, key: str) -> str:
        critical = {'ransomware', 'malware', 'ddos'}
        high = {'phishing', 'sql_injection', 'mitm', 'xss'}
        medium = {'brute_force', 'csrf', 'dns_spoofing'}
        if key in critical: return 'critical'
        if key in high: return 'high'
        if key in medium: return 'medium'
        return 'low'

    def _get_mitre(self, key: str) -> str:
        mapping = {
            'phishing': 'T1566 - Phishing',
            'malware': 'T1204 - User Execution',
            'sql_injection': 'T1190 - Exploit Public-Facing Application',
            'xss': 'T1059 - Command and Scripting Interpreter',
            'brute_force': 'T1110 - Brute Force',
            'mitm': 'T1557 - Adversary-in-the-Middle',
            'dns_spoofing': 'T1584 - Compromise Infrastructure',
            'ddos': 'T1499 - Endpoint Denial of Service',
            'ransomware': 'T1486 - Data Encrypted for Impact',
        }
        return mapping.get(key, 'Unknown')


# Singleton instances
url_classifier = URLClassifier()
email_classifier = EmailClassifier()
scam_classifier = ScamMessageClassifier()
threat_explainer = ThreatExplainer()
