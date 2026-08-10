from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from database import db
from models.user import ScanHistory, AuditLog
from models.threat import Leaderboard, Threat
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
@login_required
def index():
    stats = _get_user_stats(current_user.id)
    recent_scans = ScanHistory.query.filter_by(user_id=current_user.id)\
        .order_by(ScanHistory.created_at.desc()).limit(10).all()
    recent_threats = Threat.query.filter_by(is_active=True)\
        .order_by(Threat.created_at.desc()).limit(5).all()
    leaderboard = Leaderboard.query.order_by(Leaderboard.total_score.desc()).limit(5).all()
    # Weekly scan trend (last 7 days)
    seven_days = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        count = ScanHistory.query.filter(
            ScanHistory.user_id == current_user.id,
            func.date(ScanHistory.created_at) == day.date()
        ).count()
        seven_days.append({'day': day.strftime('%a'), 'count': count})
    return render_template('dashboard/index.html',
        stats=stats, recent_scans=recent_scans,
        recent_threats=recent_threats, leaderboard=leaderboard,
        seven_days=seven_days)


@dashboard_bp.route('/stats')
@login_required
def stats():
    return jsonify(_get_user_stats(current_user.id))


@dashboard_bp.route('/notifications')
@login_required
def notifications():
    from models.user import AuditLog
    notifs = []
    dangerous = ScanHistory.query.filter_by(
        user_id=current_user.id, risk_level='dangerous'
    ).order_by(ScanHistory.created_at.desc()).limit(5).all()
    for s in dangerous:
        notifs.append({
            'id': f'scan-{s.id}',
            'title': 'Threat Detected',
            'message': f'{s.scan_type.title()} scan flagged as dangerous: {(s.input_data or "")[:50]}',
            'time': s.created_at.strftime('%b %d, %H:%M'),
            'type': 'danger',
            'icon': 'skull-crossbones',
            'read': False
        })
    logs = AuditLog.query.filter_by(user_id=current_user.id)\
        .order_by(AuditLog.created_at.desc()).limit(5).all()
    for log in logs:
        notifs.append({
            'id': f'log-{log.id}',
            'title': log.action.replace('_', ' ').title(),
            'message': f'{log.resource or "System"} — {log.status}',
            'time': log.created_at.strftime('%b %d, %H:%M'),
            'type': 'success' if log.status == 'success' else 'warning',
            'icon': 'shield-halved',
            'read': True
        })
    if not notifs:
        notifs.append({
            'id': 'welcome',
            'title': 'Welcome to CyberShield AI',
            'message': 'Start scanning to receive security notifications.',
            'time': 'Now',
            'type': 'info',
            'icon': 'bell',
            'read': True
        })
    return jsonify({'notifications': notifs[:10]})


@dashboard_bp.route('/chart-data')
@login_required
def chart_data():
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    scans = ScanHistory.query.filter(
        ScanHistory.user_id == current_user.id,
        ScanHistory.created_at >= thirty_days_ago
    ).all()

    by_type = {}
    by_risk = {'safe': 0, 'suspicious': 0, 'dangerous': 0}
    by_day = {}

    for scan in scans:
        by_type[scan.scan_type] = by_type.get(scan.scan_type, 0) + 1
        if scan.risk_level in by_risk:
            by_risk[scan.risk_level] += 1
        day = scan.created_at.strftime('%Y-%m-%d')
        by_day[day] = by_day.get(day, 0) + 1

    return jsonify({
        'by_type': by_type,
        'by_risk': by_risk,
        'by_day': by_day,
        'total': len(scans)
    })


def _get_user_stats(user_id):
    total = ScanHistory.query.filter_by(user_id=user_id).count()
    dangerous = ScanHistory.query.filter_by(user_id=user_id, risk_level='dangerous').count()
    suspicious = ScanHistory.query.filter_by(user_id=user_id, risk_level='suspicious').count()
    urls = ScanHistory.query.filter_by(user_id=user_id, scan_type='website').count()
    emails = ScanHistory.query.filter_by(user_id=user_id, scan_type='email').count()
    from models.user import User
    user = User.query.get(user_id)
    return {
        'total_scans': total,
        'dangerous_detected': dangerous,
        'suspicious_detected': suspicious,
        'urls_scanned': urls,
        'emails_scanned': emails,
        'cyber_score': user.cyber_score if user else 0,
        'training_progress': user.training_progress if user else 0
    }
