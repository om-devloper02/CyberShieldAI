# Month 1 — Project Planning & Research
## CyberShield AI | M.Sc. Cyber Security Final Year Project

---

## 🎯 Goal of This Month
Understand the project requirements, do research on cyber security topics, and plan the full project structure.

---

## 📌 What Was Done in Month 1

### 1. Project Title Finalization
- **Title:** CyberShield AI — AI-Powered Cyber Security Awareness, Detection & Attack Simulation Platform
- **Purpose:** Educational platform for students and organizations to learn about cyber threats safely.

### 2. Problem Statement
Cyber attacks are increasing every year. Most people do not know:
- How phishing attacks work
- How to check if a website is safe
- How to create strong passwords
- How malware spreads

**Solution:** Build a platform that educates users through simulations, scanners, and AI assistance.

### 3. Research Topics Studied
| Topic | Description |
|-------|-------------|
| Phishing Attacks | How fake websites/emails steal credentials |
| SQL Injection | How attackers exploit database queries |
| XSS (Cross-Site Scripting) | Script injection in web pages |
| CSRF | Cross-site request forgery attacks |
| MITM | Man-in-the-Middle attack techniques |
| DDoS | Distributed Denial of Service attacks |
| Password Security | Entropy, crack time, common passwords |
| Malware Types | Viruses, Trojans, Ransomware, Spyware |
| MITRE ATT&CK Framework | Industry standard for threat classification |

### 4. Technology Stack Selected
| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend | Python 3.11 + Flask 3.x | Lightweight, easy to build REST APIs |
| Database | SQLite (dev) / PostgreSQL (prod) | Simple setup for development |
| ORM | SQLAlchemy | Easy database management |
| Authentication | Flask-Login + JWT | Session + API token support |
| Frontend | HTML + Jinja2 + CSS + JS | Server-side rendering |
| AI/ML | Rule-based classifiers | No GPU needed, fast and explainable |
| Deployment | Docker + Docker Compose | Easy containerized deployment |

### 5. Project Modules Planned
1. 🌐 Website / URL Scanner
2. 📧 Email Phishing Analyzer
3. 🔑 Password Strength Analyzer
4. 🐛 Malware File Scanner
5. 🌐 Network Scanner
6. ⚗️ Attack Simulator (SQLi, XSS, CSRF, MITM, DDoS, Phishing)
7. 🎓 Security Training & Quizzes
8. 🤖 AI Security Assistant (Chatbot)
9. 📊 Threat Intelligence (MITRE ATT&CK + IOC Database)
10. 📈 Reports (PDF, Excel, CSV)
11. 👨‍💼 Admin Panel

### 6. Database Design (Initial Planning)
Tables planned:
- `users` — User accounts with roles
- `roles` — admin, analyst, user
- `scan_history` — All scan records
- `audit_logs` — All user actions
- `threats` — Threat intelligence database
- `iocs` — Indicators of Compromise
- `training_modules` — Learning content
- `quizzes` — Quiz questions
- `certificates` — Completion certificates
- `leaderboard` — User scores

### 7. Project Folder Structure Planned
```
CyberShieldAI/
├── app.py          → Flask app factory
├── config.py       → Configuration
├── database.py     → DB setup & seeding
├── models/         → Database models
├── routes/         → URL routes (blueprints)
├── scanner/        → Scanning engines
├── ai/             → AI classifiers
├── templates/      → HTML pages
├── static/         → CSS, JS, Images
├── tests/          → Test cases
└── documentation/  → This folder
```

---

## 📚 References Studied
- OWASP Top 10 Web Application Security Risks
- MITRE ATT&CK Framework (https://attack.mitre.org)
- HaveIBeenPwned API Documentation
- Google Safe Browsing API Documentation
- VirusTotal API Documentation
- Flask Official Documentation

---

## ✅ Month 1 Deliverables
- [x] Project title and problem statement finalized
- [x] Technology stack selected
- [x] All modules planned
- [x] Database schema designed
- [x] Folder structure planned
- [x] Research on all cyber attack types completed

---

## 📅 Next Month Preview (Month 2)
- Set up the project environment
- Create Flask app, database models
- Build Authentication system (Register, Login, JWT)
- Build Dashboard
