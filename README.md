# 🛡️ CyberShield AI
### AI-Powered Cyber Security Awareness, Detection & Attack Simulation Platform

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Educational](https://img.shields.io/badge/Purpose-Educational%20Only-red)

> **⚠️ Disclaimer:** This platform is for educational and defensive cyber security purposes only. No real attacks are performed. All simulations run in a controlled educational environment.

---

## 📋 Overview

CyberShield AI is a complete, production-ready cyber security platform built with Python Flask. It helps students, researchers, and organizations understand cyber attacks through safe simulations, detect phishing threats, analyze security risks, and improve their cyber hygiene.


## ✨ Features

| Module | Description |
|--------|-------------|
| 🌐 **Website Scanner** | URL analysis, SSL, WHOIS, domain age, typosquatting, AI risk scoring |
| 📧 **Email Scanner** | SPF/DKIM/DMARC, header analysis, AI phishing classifier |
| 🔑 **Password Analyzer** | Entropy, crack time, HaveIBeenPwned check |
| 🐛 **Malware Scanner** | Hash generation, YARA rules, VirusTotal lookup |
| 🌐 **Network Scanner** | Device discovery, port scanning, risk analysis |
| ⚗️ **Attack Simulator** | Safe demos: SQLi, XSS, CSRF, MITM, DDoS, Phishing |
| 🎓 **Training** | Interactive lessons, quizzes, certificates, leaderboard |
| 🤖 **AI Assistant** | Security Q&A, threat explanations, scam checker |
| 📊 **Threat Intel** | MITRE ATT&CK mapping, IOC database |
| 📈 **Reports** | PDF, Excel, CSV export with analytics |
| 👨‍💼 **Admin Panel** | User management, threat DB, audit logs |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/CyberShieldAI.git
cd CyberShieldAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Run the application
python app.py
```

Visit: **http://localhost:5000**

**Default Admin:** `admin` / `Admin@123`

### Docker Setup

```bash
docker-compose up -d
```

## 🔧 Configuration

Edit `.env` file:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-key-here

# Optional API keys for enhanced features
VIRUSTOTAL_API_KEY=your-key
GOOGLE_SAFE_BROWSING_API_KEY=your-key
```

## 📁 Project Structure

```
CyberShieldAI/
├── app.py                  # Flask application factory
├── config.py               # Configuration classes
├── database.py             # DB setup & seeding
├── models/
│   ├── user.py             # User, Role, ScanHistory, AuditLog
│   └── threat.py           # Threat, IOC, Training, Quiz models
├── routes/
│   ├── auth.py             # Authentication (JWT + session)
│   ├── dashboard.py        # Dashboard & stats
│   ├── website.py          # Website/phishing scanner
│   ├── email.py            # Email analyzer
│   ├── password.py         # Password strength analyzer
│   ├── malware.py          # Malware/file scanner
│   ├── network.py          # Network scanner
│   ├── simulation.py       # Educational attack simulations
│   ├── training.py         # Lessons, quizzes, certificates
│   ├── threat.py           # Threat intelligence
│   ├── assistant.py        # AI security assistant
│   ├── reports.py          # PDF/Excel/CSV reports
│   ├── admin.py            # Admin panel
│   └── api.py              # REST API (JWT)
├── scanner/
│   ├── website/analyzer.py # URL analysis engine
│   ├── email/analyzer.py   # Email analysis engine
│   ├── malware/analyzer.py # File analysis engine
│   ├── network/scanner.py  # Network scanning engine
│   └── password_analyzer.py
├── ai/classifiers/
│   └── classifier.py       # URL, Email, Scam classifiers + Explainer
├── templates/              # Jinja2 HTML templates
├── static/
│   ├── css/main.css        # Dark/light theme CSS
│   └── js/main.js          # Frontend JS
├── tests/test_app.py       # pytest test suite
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📡 REST API

All API endpoints require JWT Bearer token.

```bash
# Login to get token
POST /auth/login
{"username": "user", "password": "pass"}

# Scan URL
POST /api/v1/scan/url
Authorization: Bearer <token>
{"url": "https://example.com"}

# Check Password
POST /api/v1/scan/password
{"password": "mypassword"}

# Scan Message
POST /api/v1/scan/message
{"message": "You won a lottery! Click now"}
```

## 🛡️ Security Note

- All simulations are **educational only** — no real attacks
- Passwords are never stored (only analyzed in memory)
- Files are deleted after scanning
- All actions are audit logged
- JWT tokens with expiry
- Role-based access control

## 📄 License

MIT License — For educational and defensive security use only.

---

Built with ❤️ for M.Sc. Cyber Security Final Year Project
