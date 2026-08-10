from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.threat import TrainingModule, Quiz, QuizResult, Certificate, DailyChallenge, Leaderboard
import secrets
from datetime import datetime, date

training_bp = Blueprint('training', __name__)


@training_bp.route('/')
@login_required
def index():
    modules = TrainingModule.query.filter_by(is_active=True).order_by(TrainingModule.order_index).all()
    completed = {r.module_id for r in QuizResult.query.filter_by(user_id=current_user.id, passed=True).all()}
    today_challenge = DailyChallenge.query.filter_by(challenge_date=date.today()).first()
    return render_template('training/index.html', modules=modules, completed=completed, today_challenge=today_challenge)


@training_bp.route('/module/<int:module_id>')
@login_required
def module(module_id):
    mod = TrainingModule.query.get_or_404(module_id)
    return render_template('training/module.html', module=mod)


@training_bp.route('/quiz/<int:module_id>')
@login_required
def quiz(module_id):
    mod = TrainingModule.query.get_or_404(module_id)
    questions = Quiz.query.filter_by(module_id=module_id).all()
    return render_template('training/quiz.html', module=mod, questions=questions)


@training_bp.route('/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    data = request.get_json()
    module_id = data.get('module_id')
    answers = data.get('answers', {})
    time_taken = data.get('time_taken', 0)

    questions = Quiz.query.filter_by(module_id=module_id).all()
    if not questions:
        return jsonify({'success': False, 'message': 'No questions found'}), 400

    score = sum(1 for q in questions if answers.get(str(q.id), '').lower() == q.correct_answer.lower())
    percentage = round((score / len(questions)) * 100, 1)
    passed = percentage >= 70

    result = QuizResult(
        user_id=current_user.id,
        module_id=module_id,
        score=score,
        total_questions=len(questions),
        percentage=percentage,
        time_taken=time_taken,
        passed=passed
    )
    db.session.add(result)

    if passed:
        current_user.cyber_score = min(1000, current_user.cyber_score + score * 10)
        _update_training_progress()
        _issue_certificate(module_id)

    _update_leaderboard()
    db.session.commit()

    return jsonify({
        'success': True,
        'score': score,
        'total': len(questions),
        'percentage': percentage,
        'passed': passed,
        'answers': {str(q.id): {'correct': q.correct_answer, 'explanation': q.explanation} for q in questions}
    })


@training_bp.route('/leaderboard')
@login_required
def leaderboard():
    top = Leaderboard.query.order_by(Leaderboard.total_score.desc()).limit(20).all()
    return render_template('training/leaderboard.html', leaderboard=top)


@training_bp.route('/certificates')
@login_required
def certificates():
    certs = Certificate.query.filter_by(user_id=current_user.id).all()
    return render_template('training/certificates.html', certificates=certs)


@training_bp.route('/certificate/<cert_id>')
def view_certificate(cert_id):
    cert = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    return render_template('training/certificate_view.html', cert=cert)


@training_bp.route('/cybercrime')
@login_required
def cybercrime():
    return render_template('training/cybercrime.html')


def _issue_certificate(module_id):
    existing = Certificate.query.filter_by(user_id=current_user.id, module_id=module_id).first()
    if not existing:
        cert = Certificate(
            user_id=current_user.id,
            module_id=module_id,
            certificate_id=secrets.token_hex(16).upper()
        )
        db.session.add(cert)


def _update_training_progress():
    total_modules = TrainingModule.query.filter_by(is_active=True).count()
    completed = QuizResult.query.filter_by(user_id=current_user.id, passed=True)\
        .distinct(QuizResult.module_id).count()
    if total_modules > 0:
        current_user.training_progress = int((completed / total_modules) * 100)


def _update_leaderboard():
    entry = Leaderboard.query.filter_by(user_id=current_user.id).first()
    if not entry:
        entry = Leaderboard(user_id=current_user.id)
        db.session.add(entry)
    entry.total_score = current_user.cyber_score
    entry.modules_completed = QuizResult.query.filter_by(user_id=current_user.id, passed=True)\
        .distinct(QuizResult.module_id).count()
    entry.updated_at = datetime.utcnow()
