from datetime import datetime
from database import db


class ThreatCategory(db.Model):
    __tablename__ = 'threat_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(20))
    threats = db.relationship('Threat', backref='category', lazy='dynamic')


class Threat(db.Model):
    __tablename__ = 'threats'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('threat_categories.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))  # low, medium, high, critical
    mitre_technique = db.Column(db.String(50))
    mitre_tactic = db.Column(db.String(100))
    ioc_type = db.Column(db.String(50))
    ioc_value = db.Column(db.Text)
    source = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'mitre_technique': self.mitre_technique,
            'mitre_tactic': self.mitre_tactic,
            'category': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat()
        }


class IOC(db.Model):
    __tablename__ = 'iocs'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # ip, domain, hash, url, email
    value = db.Column(db.Text, nullable=False, index=True)
    threat_name = db.Column(db.String(200))
    confidence = db.Column(db.Integer, default=50)
    source = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TrainingModule(db.Model):
    __tablename__ = 'training_modules'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    duration_minutes = db.Column(db.Integer, default=15)
    order_index = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    quizzes = db.relationship('Quiz', backref='module', lazy='dynamic')


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('training_modules.id'))
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(300))
    option_b = db.Column(db.String(300))
    option_c = db.Column(db.String(300))
    option_d = db.Column(db.String(300))
    correct_answer = db.Column(db.String(1))  # a, b, c, d
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=10)


class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('training_modules.id'))
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer)
    percentage = db.Column(db.Float)
    time_taken = db.Column(db.Integer)  # seconds
    passed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('training_modules.id'))
    certificate_id = db.Column(db.String(50), unique=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    module = db.relationship('TrainingModule', backref='certificates')


class DailyChallenge(db.Model):
    __tablename__ = 'daily_challenges'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    challenge_date = db.Column(db.Date, unique=True)
    points = db.Column(db.Integer, default=50)
    hint = db.Column(db.Text)
    answer = db.Column(db.Text)


class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    total_score = db.Column(db.Integer, default=0)
    challenges_completed = db.Column(db.Integer, default=0)
    modules_completed = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='leaderboard', uselist=False)
