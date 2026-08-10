from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.user import User, ScanHistory
from models.threat import Threat, IOC
from scanner.website.analyzer import analyze_url
from scanner.email.analyzer import analyze_email_text
from scanner.password_analyzer import analyze_password
from ai.classifiers.classifier import url_classifier, scam_classifier

api_bp = Blueprint('api', __name__)


def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


@api_bp.route('/scan/url', methods=['POST'])
@jwt_required()
def api_scan_url():
    user = get_current_user()
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL required'}), 400

    from flask import current_app
    result = analyze_url(url, current_app.config.get('GOOGLE_SAFE_BROWSING_API_KEY', ''))
    ai = url_classifier.predict(url)
    result['ai_prediction'] = ai

    scan = ScanHistory(user_id=user.id, scan_type='website', input_data=url[:500],
                       result=result['risk_level'], risk_score=result['risk_score'],
                       risk_level=result['risk_level'], details=result)
    db.session.add(scan)
    db.session.commit()
    return jsonify({'success': True, 'result': result, 'scan_id': scan.id})


@api_bp.route('/scan/email', methods=['POST'])
@jwt_required()
def api_scan_email():
    user = get_current_user()
    data = request.get_json()
    raw_email = data.get('email', '').strip()
    if not raw_email:
        return jsonify({'error': 'Email content required'}), 400

    result = analyze_email_text(raw_email)
    scan = ScanHistory(user_id=user.id, scan_type='email', input_data=raw_email[:200],
                       result=result['risk_level'], risk_score=result['threat_score'],
                       risk_level=result['risk_level'], details=result)
    db.session.add(scan)
    db.session.commit()
    return jsonify({'success': True, 'result': result, 'scan_id': scan.id})


@api_bp.route('/scan/password', methods=['POST'])
@jwt_required()
def api_scan_password():
    data = request.get_json()
    password = data.get('password', '')
    if not password:
        return jsonify({'error': 'Password required'}), 400
    result = analyze_password(password)
    return jsonify({'success': True, 'result': result})


@api_bp.route('/scan/message', methods=['POST'])
@jwt_required()
def api_scan_message():
    data = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message required'}), 400
    result = scam_classifier.predict(message)
    return jsonify({'success': True, 'result': result})


@api_bp.route('/history', methods=['GET'])
@jwt_required()
def api_history():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    scan_type = request.args.get('type', '')
    query = ScanHistory.query.filter_by(user_id=user.id)
    if scan_type:
        query = query.filter_by(scan_type=scan_type)
    scans = query.order_by(ScanHistory.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return jsonify({
        'scans': [s.to_dict() for s in scans.items],
        'total': scans.total,
        'pages': scans.pages,
        'current_page': page
    })


@api_bp.route('/threats', methods=['GET'])
@jwt_required()
def api_threats():
    severity = request.args.get('severity', '')
    query = Threat.query.filter_by(is_active=True)
    if severity:
        query = query.filter_by(severity=severity)
    threats = query.limit(50).all()
    return jsonify([t.to_dict() for t in threats])


@api_bp.route('/ioc/check', methods=['POST'])
@jwt_required()
def api_ioc_check():
    data = request.get_json()
    value = data.get('value', '').strip()
    if not value:
        return jsonify({'error': 'Value required'}), 400
    ioc = IOC.query.filter_by(value=value, is_active=True).first()
    if ioc:
        return jsonify({'found': True, 'type': ioc.type, 'threat': ioc.threat_name, 'confidence': ioc.confidence})
    return jsonify({'found': False})


@api_bp.route('/user/profile', methods=['GET'])
@jwt_required()
def api_profile():
    user = get_current_user()
    return jsonify(user.to_dict())
