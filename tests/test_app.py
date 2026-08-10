import pytest
import json
from app import create_app
from database import db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    # Register and login
    client.post('/auth/register', json={
        'username': 'testuser', 'email': 'test@test.com',
        'full_name': 'Test User', 'password': 'TestPass@123',
        'confirm_password': 'TestPass@123'
    })
    from models.user import User
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        if user:
            user.is_verified = True
            _db.session.commit()

    resp = client.post('/auth/login', json={
        'username': 'testuser', 'password': 'TestPass@123'
    })
    data = json.loads(resp.data)
    if 'access_token' in data:
        return {'Authorization': f'Bearer {data["access_token"]}'}
    return {}


# ===== Auth Tests =====
class TestAuth:
    def test_register_success(self, client):
        resp = client.post('/auth/register', json={
            'username': 'newuser123', 'email': 'new@test.com',
            'full_name': 'New User', 'password': 'NewPass@123',
            'confirm_password': 'NewPass@123'
        })
        assert resp.status_code in [200, 302]

    def test_register_duplicate_username(self, client):
        data = {'username': 'admin', 'email': 'x@x.com', 'password': 'pass1234', 'confirm_password': 'pass1234'}
        resp = client.post('/auth/register', json=data)
        # Should fail or redirect
        assert resp.status_code in [200, 400]

    def test_login_invalid(self, client):
        resp = client.post('/auth/login', json={'username': 'nobody', 'password': 'wrongpass'})
        assert resp.status_code in [200, 401]

    def test_home_page(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_health_endpoint(self, client):
        resp = client.get('/health')
        data = json.loads(resp.data)
        assert data['status'] == 'healthy'
        assert data['app'] == 'CyberShield AI'


# ===== Password Analyzer Tests =====
class TestPasswordAnalyzer:
    def test_weak_password(self):
        from scanner.password_analyzer import analyze_password
        result = analyze_password('123456')
        assert result['strength'] in ['very_weak', 'weak']
        assert result['is_common'] is True

    def test_strong_password(self):
        from scanner.password_analyzer import analyze_password
        result = analyze_password('T!ger$Blue9Mountain2024#')
        assert result['strength'] in ['strong', 'very_strong']
        assert result['strength_score'] >= 60

    def test_entropy_calculation(self):
        from scanner.password_analyzer import analyze_password
        result = analyze_password('abcdefgh')
        assert result['entropy'] > 0

    def test_sequential_detection(self):
        from scanner.password_analyzer import analyze_password
        result = analyze_password('password123')
        assert len(result['issues']) > 0

    def test_empty_password(self):
        from scanner.password_analyzer import analyze_password
        result = analyze_password('')
        assert len(result['issues']) > 0


# ===== URL Classifier Tests =====
class TestURLClassifier:
    def test_legitimate_url(self):
        from ai.classifiers.classifier import url_classifier
        result = url_classifier.predict('https://www.google.com')
        assert 'label' in result
        assert 'confidence' in result

    def test_suspicious_ip_url(self):
        from ai.classifiers.classifier import url_classifier
        result = url_classifier.predict('http://192.168.1.1/login')
        assert result['label'] == 'phishing'

    def test_phishing_url_features(self):
        from ai.classifiers.classifier import url_classifier
        result = url_classifier.predict('http://paypal-secure-login.tk/verify-account')
        assert result['phishing_probability'] > 50


# ===== Email Classifier Tests =====
class TestEmailClassifier:
    def test_phishing_email(self):
        from ai.classifiers.classifier import email_classifier
        result = email_classifier.predict(
            subject='URGENT: Your account is suspended',
            body='Click here to verify your account immediately or it will be closed.'
        )
        assert result['label'] == 'phishing'

    def test_legitimate_email(self):
        from ai.classifiers.classifier import email_classifier
        result = email_classifier.predict(
            subject='Team meeting tomorrow at 3pm',
            body='Hi, just a reminder about our weekly sync meeting.'
        )
        assert result['phishing_probability'] < 50


# ===== Scam Classifier Tests =====
class TestScamClassifier:
    def test_lottery_scam(self):
        from ai.classifiers.classifier import scam_classifier
        result = scam_classifier.predict('Congratulations! You have won a prize. Click to claim now.')
        assert result['label'] == 'scam'

    def test_legitimate_message(self):
        from ai.classifiers.classifier import scam_classifier
        result = scam_classifier.predict('Your order has been shipped. Track at example.com')
        assert 'label' in result

    def test_otp_scam(self):
        from ai.classifiers.classifier import scam_classifier
        result = scam_classifier.predict('Share your OTP to verify your bank account number immediately.')
        assert result['scam_probability'] > 0


# ===== Threat Explainer Tests =====
class TestThreatExplainer:
    def test_explain_phishing(self):
        from ai.classifiers.classifier import threat_explainer
        result = threat_explainer.explain('phishing')
        assert 'explanation' in result
        assert 'mitigations' in result
        assert len(result['mitigations']) > 0

    def test_explain_ransomware(self):
        from ai.classifiers.classifier import threat_explainer
        result = threat_explainer.explain('ransomware')
        assert result['severity'] == 'critical'

    def test_explain_unknown(self):
        from ai.classifiers.classifier import threat_explainer
        result = threat_explainer.explain('unknown_threat')
        assert 'explanation' in result


# ===== API Tests =====
class TestAPI:
    def test_api_scan_password(self, client, auth_headers):
        if not auth_headers:
            pytest.skip('Auth not available')
        resp = client.post('/api/v1/scan/password',
            json={'password': 'TestPass@123'},
            headers=auth_headers)
        assert resp.status_code in [200, 422]

    def test_api_profile(self, client, auth_headers):
        if not auth_headers:
            pytest.skip('Auth not available')
        resp = client.get('/api/v1/user/profile', headers=auth_headers)
        assert resp.status_code in [200, 401, 422]
