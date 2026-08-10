from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.user import ScanHistory
from scanner.email.analyzer import analyze_email_text
from ai.classifiers.classifier import email_classifier
import os

email_bp = Blueprint('email', __name__)


@email_bp.route('/')
@login_required
def index():
    history = ScanHistory.query.filter_by(user_id=current_user.id, scan_type='email')\
        .order_by(ScanHistory.created_at.desc()).limit(20).all()
    return render_template('email/index.html', history=history)


@email_bp.route('/scan', methods=['POST'])
@login_required
def scan():
    raw_email = ''

    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        raw_email = file.read().decode('utf-8', errors='replace')
    else:
        data = request.get_json() if request.is_json else request.form
        raw_email = data.get('email_text', '').strip()

    if not raw_email:
        return jsonify({'success': False, 'message': 'Email content is required'}), 400

    result = analyze_email_text(raw_email)

    # AI enhancement
    import email as email_lib, email.policy
    try:
        msg = email_lib.message_from_string(raw_email, policy=email_lib.policy.default)
        subject = msg.get('Subject', '')
        body = result.get('content_analysis', {})
        ai_pred = email_classifier.predict(subject, raw_email[:2000])
        result['ai_prediction'] = ai_pred
        if ai_pred['label'] == 'phishing':
            result['threat_score'] = min(100, result['threat_score'] + int(ai_pred['phishing_probability'] * 0.2))
    except Exception:
        pass

    # Recalculate risk level after AI boost
    if result['threat_score'] >= 65:
        result['risk_level'] = 'dangerous'
    elif result['threat_score'] >= 35:
        result['risk_level'] = 'suspicious'

    scan = ScanHistory(
        user_id=current_user.id,
        scan_type='email',
        input_data=raw_email[:200] + '...',
        result=result['risk_level'],
        risk_score=result['threat_score'],
        risk_level=result['risk_level'],
        details=result
    )
    db.session.add(scan)
    db.session.commit()

    return jsonify({'success': True, 'result': result, 'scan_id': scan.id})


@email_bp.route('/result/<int:scan_id>')
@login_required
def result(scan_id):
    scan = ScanHistory.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    return render_template('email/result.html', scan=scan)
