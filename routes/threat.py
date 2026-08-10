from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from database import db
from models.threat import Threat, ThreatCategory, IOC
from ai.classifiers.classifier import threat_explainer

threat_bp = Blueprint('threat', __name__)

MITRE_TACTICS = [
    {'id': 'TA0001', 'name': 'Initial Access', 'techniques': ['T1566 Phishing', 'T1190 Exploit Public App', 'T1133 External Remote Services']},
    {'id': 'TA0002', 'name': 'Execution', 'techniques': ['T1059 Command Interpreter', 'T1204 User Execution', 'T1053 Scheduled Task']},
    {'id': 'TA0003', 'name': 'Persistence', 'techniques': ['T1547 Boot Autostart', 'T1078 Valid Accounts', 'T1505 Server Software Component']},
    {'id': 'TA0006', 'name': 'Credential Access', 'techniques': ['T1110 Brute Force', 'T1555 Credentials from Stores', 'T1056 Input Capture']},
    {'id': 'TA0009', 'name': 'Collection', 'techniques': ['T1560 Archive Data', 'T1114 Email Collection', 'T1119 Automated Collection']},
    {'id': 'TA0010', 'name': 'Exfiltration', 'techniques': ['T1041 Exfil Over C2', 'T1048 Exfil Over Alt Protocol', 'T1567 Exfil Over Web Service']},
    {'id': 'TA0040', 'name': 'Impact', 'techniques': ['T1486 Data Encrypted (Ransomware)', 'T1499 Endpoint DoS', 'T1485 Data Destruction']},
]


@threat_bp.route('/')
@login_required
def index():
    categories = ThreatCategory.query.all()
    recent_threats = Threat.query.filter_by(is_active=True).order_by(Threat.created_at.desc()).limit(10).all()
    return render_template('threat/index.html', categories=categories, recent_threats=recent_threats, mitre_tactics=MITRE_TACTICS)


@threat_bp.route('/mitre')
@login_required
def mitre():
    return render_template('threat/mitre.html', tactics=MITRE_TACTICS)


@threat_bp.route('/ioc')
@login_required
def ioc():
    ioc_type = request.args.get('type', '')
    page = request.args.get('page', 1, type=int)
    query = IOC.query.filter_by(is_active=True)
    if ioc_type:
        query = query.filter_by(type=ioc_type)
    iocs = query.order_by(IOC.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('threat/ioc.html', iocs=iocs, current_type=ioc_type)


@threat_bp.route('/explain/<threat_type>')
@login_required
def explain(threat_type):
    explanation = threat_explainer.explain(threat_type)
    if request.is_json or request.args.get('format') == 'json':
        return jsonify(explanation)
    return render_template('threat/explain.html', explanation=explanation, threat_type=threat_type)


@threat_bp.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    results = []
    if q:
        results = Threat.query.filter(
            Threat.name.ilike(f'%{q}%') | Threat.description.ilike(f'%{q}%')
        ).limit(20).all()
    return render_template('threat/search.html', results=results, query=q)


@threat_bp.route('/api/threats')
@login_required
def api_threats():
    category = request.args.get('category', '')
    severity = request.args.get('severity', '')
    query = Threat.query.filter_by(is_active=True)
    if category:
        cat = ThreatCategory.query.filter_by(name=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if severity:
        query = query.filter_by(severity=severity)
    threats = query.order_by(Threat.created_at.desc()).limit(100).all()
    return jsonify([t.to_dict() for t in threats])
