from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.user import ScanHistory
from scanner.website.analyzer import analyze_url, analyze_qr_code
from ai.classifiers.classifier import url_classifier
import os, json

website_bp = Blueprint('website', __name__)


@website_bp.route('/')
@login_required
def index():
    history = ScanHistory.query.filter_by(user_id=current_user.id, scan_type='website')\
        .order_by(ScanHistory.created_at.desc()).limit(20).all()
    return render_template('website/index.html', history=history)


@website_bp.route('/scan', methods=['POST'])
@login_required
def scan():
    data = request.get_json() if request.is_json else request.form
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'success': False, 'message': 'URL is required'}), 400

    from flask import current_app
    api_key = current_app.config.get('GOOGLE_SAFE_BROWSING_API_KEY', '')
    result = analyze_url(url, api_key)

    # AI prediction layer
    ai_result = url_classifier.predict(url)
    result['ai_prediction'] = ai_result

    # Merge AI score into overall
    if ai_result['label'] == 'phishing':
        result['risk_score'] = min(100, result['risk_score'] + int(ai_result['phishing_probability'] * 0.3))
        if result['risk_score'] >= 65:
            result['risk_level'] = 'dangerous'
        elif result['risk_score'] >= 35:
            result['risk_level'] = 'suspicious'

    # Save to history
    scan = ScanHistory(
        user_id=current_user.id,
        scan_type='website',
        input_data=url[:500],
        result=result['risk_level'],
        risk_score=result['risk_score'],
        risk_level=result['risk_level'],
        details=result
    )
    db.session.add(scan)

    # Update user score
    if result['risk_level'] == 'dangerous':
        current_user.cyber_score = min(1000, current_user.cyber_score + 5)
    db.session.commit()

    return jsonify({'success': True, 'result': result, 'scan_id': scan.id})


@website_bp.route('/qr-scan', methods=['POST'])
@login_required
def qr_scan():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    from flask import current_app
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, 'qr_' + file.filename)
    file.save(filepath)

    result = analyze_qr_code(filepath)
    os.remove(filepath)
    return jsonify({'success': True, 'result': result})


@website_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    scans = ScanHistory.query.filter_by(user_id=current_user.id, scan_type='website')\
        .order_by(ScanHistory.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('website/history.html', scans=scans)


@website_bp.route('/result/<int:scan_id>')
@login_required
def result(scan_id):
    scan = ScanHistory.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    return render_template('website/result.html', scan=scan)
