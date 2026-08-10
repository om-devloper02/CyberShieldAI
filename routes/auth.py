from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from database import db
from models.user import User, Role, RevokedToken, AuditLog
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


def log_action(user_id, action, resource=None, status='success', details=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:300],
        details=details,
        status=status
    )
    db.session.add(log)
    db.session.commit()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        full_name = data.get('full_name', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Valid email is required.')
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            if request.is_json:
                return jsonify({'success': False, 'errors': errors}), 400
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        user_role = Role.query.filter_by(name='user').first()
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role_id=user_role.id,
            is_active=True,
            is_verified=True  # No email verification needed
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        log_action(user.id, 'REGISTER', 'user')
        logger.info(f"New user registered: {username}")

        if request.is_json:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify({
                'success': True,
                'message': 'Registration successful!',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            })

        flash('Welcome to CyberShield AI! Your account is ready.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user or not user.check_password(password):
            log_action(None, 'LOGIN_FAILED', 'auth', status='failed', details={'username': username})
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Account is disabled'}), 403
            flash('Your account has been disabled.', 'danger')
            return render_template('auth/login.html')

        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()

        login_user(user, remember=remember)
        log_action(user.id, 'LOGIN', 'auth')

        if request.is_json:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify({
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            })

        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_action(current_user.id, 'LOGOUT', 'auth')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Reset password using username + email verification — no OTP/email needed."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if not new_password or len(new_password) < 8:
            msg = 'Password must be at least 8 characters.'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return render_template('auth/forgot_password.html')

        if new_password != confirm_password:
            msg = 'Passwords do not match.'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return render_template('auth/forgot_password.html')

        # Verify user by matching both username AND email
        user = User.query.filter_by(username=username, email=email).first()

        if not user:
            msg = 'No account found with that username and email combination.'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return render_template('auth/forgot_password.html')

        user.set_password(new_password)
        db.session.commit()
        log_action(user.id, 'PASSWORD_RESET', 'auth')

        if request.is_json:
            return jsonify({'success': True, 'message': 'Password reset successful!'})

        flash('Password reset successful! Please login with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


# JWT API endpoints
@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token})


@auth_bp.route('/api/logout', methods=['DELETE'])
@jwt_required()
def api_logout():
    jti = get_jwt()['jti']
    revoked = RevokedToken(jti=jti)
    db.session.add(revoked)
    db.session.commit()
    return jsonify({'message': 'Token revoked successfully'})


@auth_bp.route('/profile')
@login_required
def profile():
    from models.user import AuditLog
    recent_logs = AuditLog.query.filter_by(user_id=current_user.id)\
        .order_by(AuditLog.created_at.desc()).limit(8).all()
    return render_template('auth/profile.html', user=current_user, recent_logs=recent_logs)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json() if request.is_json else request.form
    current_user.full_name = data.get('full_name', current_user.full_name).strip()
    current_user.bio = data.get('bio', current_user.bio)
    db.session.commit()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Profile updated'})
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/settings')
@login_required
def settings():
    from models.user import ScanHistory
    scan_count = ScanHistory.query.filter_by(user_id=current_user.id).count()
    return render_template('auth/settings.html', user=current_user, scan_count=scan_count)


@auth_bp.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json() if request.is_json else request.form
    current_pw = data.get('current_password', '')
    new_pw = data.get('new_password', '')
    confirm_pw = data.get('confirm_password', '')

    if not current_user.check_password(current_pw):
        msg = 'Current password is incorrect.'
        if request.is_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'danger')
        return redirect(url_for('auth.settings'))

    if len(new_pw) < 8:
        msg = 'New password must be at least 8 characters.'
        if request.is_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'danger')
        return redirect(url_for('auth.settings'))

    if new_pw != confirm_pw:
        msg = 'New passwords do not match.'
        if request.is_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'danger')
        return redirect(url_for('auth.settings'))

    current_user.set_password(new_pw)
    db.session.commit()
    log_action(current_user.id, 'PASSWORD_CHANGE', 'auth')

    if request.is_json:
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    flash('Password updated successfully.', 'success')
    return redirect(url_for('auth.settings'))
