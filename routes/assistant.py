from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai.classifiers.classifier import threat_explainer, scam_classifier

assistant_bp = Blueprint('assistant', __name__)

SECURITY_KB = {
    'phishing': 'Phishing uses fake emails/sites to steal credentials. Always verify sender, check URLs carefully, enable 2FA.',
    'password': 'Use 16+ character passwords with mixed case, numbers, symbols. Use a password manager. Never reuse passwords.',
    'malware': 'Malware = malicious software. Keep antivirus updated, avoid suspicious downloads, scan files before opening.',
    'ransomware': 'Ransomware encrypts your files and demands payment. Backup data (3-2-1 rule), patch systems, train users.',
    'vpn': 'VPN encrypts internet traffic. Use on public WiFi. Choose providers with no-log policy.',
    '2fa': 'Two-factor authentication adds a second verification step. Use authenticator apps over SMS for stronger security.',
    'social engineering': 'Manipulation to gain info or access. Be skeptical of unsolicited requests, verify through official channels.',
    'zero day': 'Zero-day = unknown vulnerability with no patch. Keep systems updated, use defence-in-depth strategy.',
    'firewall': 'Firewall monitors and controls network traffic. Enable OS firewall, configure rules for least-privilege access.',
    'encryption': 'Encryption scrambles data so only authorized parties can read it. Use TLS for web, AES for files.',
    'sql injection': 'SQL injection inserts malicious SQL via input fields. Fix: use parameterized queries, input validation, WAF.',
    'xss': 'XSS injects scripts into web pages. Fix: output encoding, Content Security Policy, input sanitization.',
    'ddos': 'DDoS floods a server to make it unavailable. Mitigate with CDN, rate limiting, DDoS protection services.',
}


@assistant_bp.route('/')
@login_required
def index():
    from flask import redirect, url_for
    return redirect(url_for('dashboard.index', chat='open'))


@assistant_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    message = data.get('message', '').strip().lower()

    if not message:
        return jsonify({'response': 'Please ask a cyber security question.', 'type': 'info'})

    response = _generate_response(message)
    return jsonify(response)


@assistant_bp.route('/analyze-message', methods=['POST'])
@login_required
def analyze_message():
    data = request.get_json()
    message = data.get('message', '').strip()
    msg_type = data.get('type', 'sms')  # sms, whatsapp, telegram

    if not message:
        return jsonify({'success': False, 'message': 'Message content required'}), 400

    result = scam_classifier.predict(message)
    result['message_type'] = msg_type
    return jsonify({'success': True, 'result': result})


def _generate_response(message: str) -> dict:
    # Check knowledge base
    for topic, answer in SECURITY_KB.items():
        if topic in message:
            return {
                'response': answer,
                'type': 'knowledge',
                'topic': topic,
                'learn_more': f'/threat/explain/{topic.replace(" ", "_")}'
            }

    # Threat explanation
    threat_keywords = ['explain', 'what is', 'how does', 'tell me about']
    for kw in threat_keywords:
        if kw in message:
            for threat in ['phishing', 'malware', 'ransomware', 'xss', 'sql', 'ddos', 'mitm', 'brute force']:
                if threat in message:
                    explanation = threat_explainer.explain(threat)
                    return {
                        'response': explanation['explanation'],
                        'type': 'explanation',
                        'mitigations': explanation['mitigations'],
                        'severity': explanation['severity'],
                        'mitre': explanation['mitre_tactic']
                    }

    # Scam message analysis request
    if any(kw in message for kw in ['is this scam', 'is this phishing', 'check this message', 'suspicious message']):
        return {
            'response': 'Please use the "Analyze Message" feature to check a suspicious message. Go to Assistant > Analyze Message and paste the content.',
            'type': 'redirect',
            'action': 'analyze_message'
        }

    # Tips
    if any(kw in message for kw in ['tip', 'advice', 'how to stay safe', 'protect']):
        tips = [
            '🔒 Use unique strong passwords for every account.',
            '📱 Enable 2FA on all important accounts.',
            '🔗 Hover over links before clicking to verify the URL.',
            '💾 Keep regular backups using the 3-2-1 rule.',
            '🛡️ Keep software and OS updated to patch vulnerabilities.',
            '📧 Be suspicious of unsolicited emails asking for information.',
            '🌐 Only enter sensitive info on HTTPS websites.',
            '📶 Avoid public WiFi without a VPN.',
        ]
        import random
        return {'response': random.choice(tips), 'type': 'tip'}

    # Default
    return {
        'response': "I can help with cyber security topics like phishing, malware, passwords, VPN, 2FA, SQL injection, XSS, DDoS, ransomware, encryption, and more. Ask me anything about staying secure online!",
        'type': 'default',
        'suggestions': list(SECURITY_KB.keys())[:6]
    }
