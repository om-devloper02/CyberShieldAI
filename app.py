import os
import logging
from flask import Flask, render_template, jsonify
from config import config
from database import init_extensions, create_tables

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('cybershield.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AI_MODELS_PATH'], exist_ok=True)

    init_extensions(app)

    register_blueprints(app)
    register_error_handlers(app)

    create_tables(app)

    logger.info(f"CyberShield AI started in {config_name} mode")
    return app


def register_blueprints(app):
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.website import website_bp
    from routes.email import email_bp
    from routes.password import password_bp
    from routes.malware import malware_bp
    from routes.network import network_bp
    from routes.simulation import simulation_bp
    from routes.training import training_bp
    from routes.reports import reports_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.threat import threat_bp
    from routes.assistant import assistant_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(website_bp, url_prefix='/website')
    app.register_blueprint(email_bp, url_prefix='/email')
    app.register_blueprint(password_bp, url_prefix='/password')
    app.register_blueprint(malware_bp, url_prefix='/malware')
    app.register_blueprint(network_bp, url_prefix='/network')
    app.register_blueprint(simulation_bp, url_prefix='/simulation')
    app.register_blueprint(training_bp, url_prefix='/training')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(threat_bp, url_prefix='/threat')
    app.register_blueprint(assistant_bp, url_prefix='/assistant')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'app': 'CyberShield AI', 'version': '1.0.0'})


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server Error: {e}")
        return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
