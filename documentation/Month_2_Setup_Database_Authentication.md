# Month 2 — Project Setup, Database & Authentication
## CyberShield AI | M.Sc. Cyber Security Final Year Project

---

## 🎯 Goal of This Month
Set up the complete project environment, create all database models, and build the full authentication system.

---

## 📌 What Was Done in Month 2

### 1. Environment Setup
```bash
# Created virtual environment
python -m venv venv
venv\Scripts\activate

# Installed all dependencies
pip install -r requirements.txt

# Created .env file with configuration
SECRET_KEY=cybershield-secret-key
JWT_SECRET_KEY=jwt-secret-key
FLASK_ENV=development
```

**Key packages installed:**
| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | Database ORM |
| Flask-Login | 0.6.3 | Session authentication |
| Flask-JWT-Extended | 4.7.1 | API token authentication |
| Flask-Mail | 0.10.0 | Email sending |
| Flask-CORS | 5.0.0 | Cross-origin requests |
| Werkzeug | 3.1.0 | Password hashing |
| python-dotenv | 1.0.1 | Environment variables |

---

### 2. Flask App Factory Created (`app.py`)
- Used **Application Factory Pattern** — best practice for Flask
- Registers all 14 blueprints
- Sets up error handlers (400, 401, 403, 404, 500)
- Creates upload and AI model directories automatically
- Initializes logging to file (`cybershield.log`) and console

```python
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    create_tables(app)
    return app
```

---

### 3. Configuration System (`config.py`)
Three environments created:
| Config | Database | Debug | Use Case |
|--------|----------|-------|---------|
| DevelopmentConfig | SQLite (local file) | True | Local development |
| ProductionConfig | PostgreSQL (env var) | False | Live deployment |
| TestingConfig | SQLite in-memory | True | Automated tests |

---

### 4. Database Extensions (`database.py`)
Extensions initialized:
- `SQLAlchemy` — ORM for all database operations
- `LoginManager` — Handles user sessions
- `JWTManager` — Handles API tokens
- `Mail` — Email sending
- `CORS` — API cross-origin access

**Token Revocation System:**
```python
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedToken.query.filter_by(jti=jti).first() is not None
```

---

### 5. Database Models Created

#### `models/user.py`
| Model | Fields | Purpose |
|-------|--------|---------|
| Role | id, name, description | admin / analyst / user roles |
| User | id, username, email, password_hash, role_id, cyber_score, etc. | Main user account |
| RevokedToken | id, jti, revoked_at | JWT token blacklist |
| ScanHistory | id, user_id, scan_type, result, risk_score, risk_level | All scan records |
| AuditLog | id, user_id, action, ip_address, status | Security audit trail |

#### `models/threat.py`
| Model | Fields | Purpose |
|-------|--------|---------|
| ThreatCategory | id, name, icon, color | Phishing, Malware, etc. |
| Threat | id, name, severity, mitre_technique | Threat intelligence |
| IOC | id, type, value, confidence | Indicators of Compromise |
| TrainingModule | id, title, content, difficulty | Learning modules |
| Quiz | id, question, options, correct_answer | Quiz questions |
| QuizResult | id, user_id, score, percentage | User quiz scores |
| Certificate | id, user_id, certificate_id | Completion certificates |
| DailyChallenge | id, title, points, answer | Daily security challenge |
| Leaderboard | id, user_id, total_score, rank | User rankings |

---

### 6. Database Seeding (Auto on First Run)
When app starts for the first time, it automatically creates:
- 3 Roles: admin, analyst, user
- 6 Threat Categories: Phishing, Malware, Social Engineering, Network, Web, Password
- 1 Default Admin: `admin` / `Admin@123`
- 6 Training Modules with quiz questions
- 5 Sample Threats with MITRE ATT&CK mapping
- 4 Sample IOCs (domain, IP, hash, URL)
- 1 Daily Challenge

---

### 7. Authentication System (`routes/auth.py`)

#### Features Built:
| Feature | Route | Method |
|---------|-------|--------|
| Register | `/auth/register` | GET, POST |
| Login | `/auth/login` | GET, POST |
| Logout | `/auth/logout` | GET |
| Forgot Password | `/auth/forgot-password` | GET, POST |
| Profile View | `/auth/profile` | GET |
| Update Profile | `/auth/profile/update` | POST |
| Settings | `/auth/settings` | GET |
| Change Password | `/auth/settings/password` | POST |
| JWT Refresh | `/auth/api/refresh` | POST |
| JWT Logout | `/auth/api/logout` | DELETE |

#### Security Features in Auth:
- Passwords hashed using `werkzeug.security.generate_password_hash`
- JWT tokens with 24-hour expiry
- Refresh tokens with 30-day expiry
- Token revocation stored in database
- Audit log created for every login/logout/register action
- Both JSON (API) and HTML (web) responses supported
- Login by username OR email supported

#### Password Reset Flow (No Email Needed):
```
User provides: username + email + new_password
System verifies: username AND email must match in DB
If match: password is reset immediately
```

---

### 8. Dashboard Built (`routes/dashboard.py`)
| Route | Purpose |
|-------|---------|
| `/dashboard/` | Main dashboard with stats |
| `/dashboard/stats` | JSON stats API |
| `/dashboard/notifications` | Security notifications |
| `/dashboard/chart-data` | Chart data for graphs |

**Stats shown on dashboard:**
- Total scans performed
- Dangerous threats detected
- Suspicious items found
- URLs scanned
- Emails analyzed
- Cyber score
- Training progress
- Weekly scan trend (last 7 days chart)
- Recent 10 scans
- Latest 5 threats
- Top 5 leaderboard

---

## ✅ Month 2 Deliverables
- [x] Virtual environment and all packages installed
- [x] Flask app factory with 3 config environments
- [x] All 9 database models created
- [x] Auto database seeding on first run
- [x] Complete authentication system (register, login, logout, forgot password)
- [x] JWT API authentication with token revocation
- [x] Audit logging for all auth actions
- [x] Dashboard with stats, charts, notifications

---

## 📅 Next Month Preview (Month 3)
- Build Website/URL Scanner
- Build Email Phishing Analyzer
- Build Password Strength Analyzer
- Build Malware File Scanner
- Build AI Classifiers
