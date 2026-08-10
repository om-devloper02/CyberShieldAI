from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from database import db
from models.user import User, AuditLog, ScanHistory
from models.threat import Threat, ThreatCategory, IOC, TrainingModule, Quiz
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Admin access required'}), 403
            return render_template('errors/403.html'), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_scans': ScanHistory.query.count(),
        'threats_detected': ScanHistory.query.filter_by(risk_level='dangerous').count(),
        'threats_in_db': Threat.query.count(),
        'recent_logs': AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    }
    return render_template('admin/index.html', stats=stats)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter(User.username.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
    users_page = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users_page, search=search)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot deactivate yourself'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active})


@admin_bp.route('/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete yourself'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/threats')
@login_required
@admin_required
def threats():
    page = request.args.get('page', 1, type=int)
    threats_page = Threat.query.order_by(Threat.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    categories = ThreatCategory.query.all()
    return render_template('admin/threats.html', threats=threats_page, categories=categories)


@admin_bp.route('/threats/add', methods=['POST'])
@login_required
@admin_required
def add_threat():
    data = request.get_json() if request.is_json else request.form
    threat = Threat(
        category_id=data.get('category_id'),
        name=data.get('name', ''),
        description=data.get('description', ''),
        severity=data.get('severity', 'medium'),
        mitre_technique=data.get('mitre_technique', ''),
        mitre_tactic=data.get('mitre_tactic', ''),
        source=data.get('source', 'manual')
    )
    db.session.add(threat)
    db.session.commit()
    return jsonify({'success': True, 'id': threat.id})


@admin_bp.route('/threats/<int:threat_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_threat(threat_id):
    threat = Threat.query.get_or_404(threat_id)
    db.session.delete(threat)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/iocs')
@login_required
@admin_required
def iocs():
    page = request.args.get('page', 1, type=int)
    iocs_page = IOC.query.order_by(IOC.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('admin/iocs.html', iocs=iocs_page)


@admin_bp.route('/iocs/add', methods=['POST'])
@login_required
@admin_required
def add_ioc():
    data = request.get_json() if request.is_json else request.form
    ioc = IOC(
        type=data.get('type'),
        value=data.get('value', ''),
        threat_name=data.get('threat_name', ''),
        confidence=int(data.get('confidence', 50)),
        source=data.get('source', 'manual')
    )
    db.session.add(ioc)
    db.session.commit()
    return jsonify({'success': True, 'id': ioc.id})


@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '')
    query = AuditLog.query
    if action_filter:
        query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))
    logs_page = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('admin/logs.html', logs=logs_page, action_filter=action_filter)


@admin_bp.route('/training/modules')
@login_required
@admin_required
def training_modules():
    modules = TrainingModule.query.order_by(TrainingModule.order_index).all()
    return render_template('admin/training_modules.html', modules=modules)


@admin_bp.route('/training/modules/add', methods=['POST'])
@login_required
@admin_required
def add_module():
    data = request.get_json() if request.is_json else request.form
    mod = TrainingModule(
        title=data.get('title', ''),
        description=data.get('description', ''),
        content=data.get('content', ''),
        difficulty=data.get('difficulty', 'beginner'),
        duration_minutes=int(data.get('duration_minutes', 15)),
        order_index=int(data.get('order_index', 0)),
        icon=data.get('icon', 'fa-book')
    )
    db.session.add(mod)
    db.session.commit()
    return jsonify({'success': True, 'id': mod.id})


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    thirty_days = datetime.utcnow() - timedelta(days=30)
    scans_by_day = db.session.query(
        db.func.date(ScanHistory.created_at),
        db.func.count(ScanHistory.id)
    ).filter(ScanHistory.created_at >= thirty_days)\
     .group_by(db.func.date(ScanHistory.created_at)).all()

    return render_template('admin/analytics.html', scans_by_day=scans_by_day)
