from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()
cors = CORS()

logger = logging.getLogger(__name__)


def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from models.user import RevokedToken
        jti = jwt_payload['jti']
        return RevokedToken.query.filter_by(jti=jti).first() is not None


def create_tables(app):
    with app.app_context():
        db.create_all()
        seed_initial_data()
        logger.info("Database tables created successfully")


def seed_initial_data():
    from models.user import User, Role
    from models.threat import ThreatCategory

    if not Role.query.first():
        roles = [
            Role(name='admin', description='Full system access'),
            Role(name='user', description='Standard user access'),
            Role(name='analyst', description='Security analyst access'),
        ]
        db.session.add_all(roles)
        db.session.commit()

    if not ThreatCategory.query.first():
        categories = [
            ThreatCategory(name='Phishing', description='Phishing attacks and simulations', icon='fa-fish', color='#e74c3c'),
            ThreatCategory(name='Malware', description='Malicious software analysis', icon='fa-bug', color='#e67e22'),
            ThreatCategory(name='Social Engineering', description='Human manipulation attacks', icon='fa-user-secret', color='#9b59b6'),
            ThreatCategory(name='Network Attack', description='Network-based threats', icon='fa-network-wired', color='#3498db'),
            ThreatCategory(name='Web Attack', description='Web application attacks', icon='fa-globe', color='#1abc9c'),
            ThreatCategory(name='Password Attack', description='Password cracking techniques', icon='fa-key', color='#f39c12'),
        ]
        db.session.add_all(categories)
        db.session.commit()

    if not User.query.filter_by(username='admin').first():
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin',
            email='admin@cybershield.ai',
            full_name='CyberShield Admin',
            role_id=admin_role.id,
            is_active=True,
            is_verified=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        logger.info("Default admin user created: admin / Admin@123")

    _seed_training_modules()
    _seed_sample_threats()


def _seed_training_modules():
    from models.threat import TrainingModule, Quiz, DailyChallenge
    from datetime import date

    if TrainingModule.query.first():
        return

    modules_data = [
        ('Introduction to Cyber Security', 'Learn the fundamentals of cyber security and why it matters.', 'fa-shield-halved', 'beginner', 15, 1,
         'Cyber security protects systems, networks, and data from digital attacks. Key concepts include confidentiality, integrity, and availability (CIA triad).'),
        ('Phishing Awareness', 'Recognize and defend against phishing attacks.', 'fa-fish', 'beginner', 20, 2,
         'Phishing is a social engineering attack where attackers impersonate trusted entities to steal credentials. Always verify sender addresses and hover over links.'),
        ('Password Security', 'Create and manage strong passwords effectively.', 'fa-key', 'beginner', 15, 3,
         'Strong passwords are long, unique, and random. Use a password manager. Enable multi-factor authentication on all important accounts.'),
        ('Malware Fundamentals', 'Understand viruses, trojans, ransomware and more.', 'fa-bug', 'intermediate', 25, 4,
         'Malware includes viruses, worms, trojans, ransomware, and spyware. Keep software updated, use antivirus, and never open suspicious attachments.'),
        ('Network Security Basics', 'Learn about firewalls, ports, and network threats.', 'fa-network-wired', 'intermediate', 20, 5,
         'Network security involves protecting data in transit. Key tools include firewalls, VPNs, and intrusion detection systems.'),
        ('Web Application Security', 'SQL injection, XSS, CSRF and how to prevent them.', 'fa-globe', 'advanced', 30, 6,
         'Web attacks exploit application vulnerabilities. Use parameterized queries, input validation, CSRF tokens, and Content Security Policy headers.'),
    ]

    for title, desc, icon, diff, duration, order, content in modules_data:
        mod = TrainingModule(title=title, description=desc, icon=icon, difficulty=diff,
                             duration_minutes=duration, order_index=order, content=content, is_active=True)
        db.session.add(mod)
    db.session.commit()

    mod1 = TrainingModule.query.filter_by(title='Introduction to Cyber Security').first()
    if mod1:
        quizzes = [
            ('What does the CIA triad stand for in cyber security?',
             'Confidentiality, Integrity, Availability', 'Cost, Investment, Analysis', 'Control, Identity, Access', 'None of the above', 'a',
             'The CIA triad represents the three core principles of information security.'),
            ('Which is the best first line of defense against cyber attacks?',
             'Strong awareness and training', 'Ignoring emails', 'Disabling firewalls', 'Sharing passwords', 'a',
             'Human awareness is often the most critical defense layer.'),
        ]
        for q, a, b, c, d, ans, expl in quizzes:
            db.session.add(Quiz(module_id=mod1.id, question=q, option_a=a, option_b=b, option_c=c, option_d=d,
                                correct_answer=ans, explanation=expl, points=10))
        db.session.commit()

    if not DailyChallenge.query.filter_by(challenge_date=date.today()).first():
        db.session.add(DailyChallenge(
            title='Spot the Phish',
            description='Identify 3 red flags in a suspicious email scenario.',
            challenge_date=date.today(),
            points=50,
            hint='Look for urgency, mismatched URLs, and generic greetings.',
            answer='urgency,mismatched_url,generic_greeting'
        ))
        db.session.commit()


def _seed_sample_threats():
    from models.threat import Threat, ThreatCategory, IOC

    if Threat.query.first():
        return

    cat_map = {c.name: c for c in ThreatCategory.query.all()}
    threats = [
        ('Emotet Banking Trojan', 'Phishing', 'high', 'T1566', 'Initial Access', 'Emotet spreads via phishing emails with malicious attachments.'),
        ('LockBit Ransomware', 'Malware', 'critical', 'T1486', 'Impact', 'Ransomware that encrypts files and demands cryptocurrency payment.'),
        ('Credential Stuffing', 'Password Attack', 'medium', 'T1110', 'Credential Access', 'Attackers use leaked credentials to access multiple accounts.'),
        ('DNS Spoofing', 'Network Attack', 'high', 'T1557', 'Collection', 'Attackers redirect DNS queries to malicious servers.'),
        ('Fake Login Pages', 'Phishing', 'high', 'T1566.002', 'Initial Access', 'Clone websites designed to steal login credentials.'),
    ]
    for name, cat, sev, mitre, tactic, desc in threats:
        c = cat_map.get(cat)
        if c:
            db.session.add(Threat(category_id=c.id, name=name, description=desc, severity=sev,
                                  mitre_technique=mitre, mitre_tactic=tactic, source='CyberShield Intel'))
    db.session.commit()

    if not IOC.query.first():
        iocs = [
            ('domain', 'secure-login-verify.tk', 'Phishing Campaign', 85),
            ('ip', '192.0.2.100', 'C2 Server', 70),
            ('hash', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Malware Sample', 90),
            ('url', 'http://fake-bank-login.xyz/account', 'Fake Login Page', 95),
        ]
        for ioc_type, value, threat, conf in iocs:
            db.session.add(IOC(type=ioc_type, value=value, threat_name=threat, confidence=conf, source='Threat Feed'))
        db.session.commit()
