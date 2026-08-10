from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.user import ScanHistory
from scanner.password_analyzer import analyze_password

password_bp = Blueprint('password', __name__)


@password_bp.route('/')
@login_required
def index():
    return render_template('password/index.html')


@password_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json() if request.is_json else request.form
    password = data.get('password', '')

    if not password:
        return jsonify({'success': False, 'message': 'Password is required'}), 400

    result = analyze_password(password)

    scan = ScanHistory(
        user_id=current_user.id,
        scan_type='password',
        input_data='[REDACTED]',
        result=result['strength'],
        risk_score=100 - result['strength_score'],
        risk_level='safe' if result['strength_score'] >= 60 else ('suspicious' if result['strength_score'] >= 30 else 'dangerous'),
        details={k: v for k, v in result.items() if k != 'password'}
    )
    db.session.add(scan)
    db.session.commit()

    return jsonify({'success': True, 'result': result})
