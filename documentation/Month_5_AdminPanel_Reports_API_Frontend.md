# Month 5 — Admin Panel, Reports, REST API & Frontend
## CyberShield AI | M.Sc. Cyber Security Final Year Project

---

## 🎯 Goal of This Month
Build the Admin Panel, Reports export system, complete REST API, and all frontend HTML templates with dark/light theme.

---

## 📌 What Was Done in Month 5

### 1. Admin Panel (`routes/admin.py`)

Only accessible by users with `admin` role. Regular users get 403 Forbidden.

#### Admin Features:
| Route | Purpose |
|-------|---------|
| `/admin/` | Admin dashboard with system stats |
| `/admin/users` | View, activate/deactivate all users |
| `/admin/users/<id>/toggle` | Enable or disable a user account |
| `/admin/logs` | View all audit logs with filters |
| `/admin/threats` | Manage threat intelligence database |
| `/admin/threats/add` | Add new threat to database |
| `/admin/iocs` | Manage IOC database |
| `/admin/iocs/add` | Add new IOC |
| `/admin/training` | Manage training modules |
| `/admin/analytics` | System-wide analytics and charts |

#### Admin Dashboard Stats:
- Total registered users
- Total scans performed (all users)
- Total threats in database
- Total IOCs in database
- Recent audit logs (last 20 actions)
- System health status

#### User Management:
- View all users with their role, scan count, last login
- Activate / Deactivate user accounts
- View individual user's scan history
- Cannot delete admin account

#### Audit Log Viewer:
- Shows all actions: LOGIN, LOGOUT, REGISTER, SCAN, PASSWORD_CHANGE, etc.
- Filters by: user, action type, date range, status (success/failed)
- Shows: timestamp, user, action, IP address, user agent, status
- Useful for detecting suspicious activity

---

### 2. Reports Module (`routes/reports.py`)

Users can export their scan history and security reports.

#### Export Formats:
| Format | Library Used | Contents |
|--------|-------------|---------|
| PDF | ReportLab | Formatted report with charts, scan summary |
| Excel | OpenPyXL | Spreadsheet with all scan data |
| CSV | Python csv | Raw data for analysis |

#### Report Contents:
- User information and cyber score
- Total scans by type (website, email, password, malware, network)
- Risk distribution (safe, suspicious, dangerous)
- Scan history table with dates and results
- Security recommendations
- Training progress summary

#### Report Routes:
| Route | Purpose |
|-------|---------|
| `/reports/` | Reports dashboard |
| `/reports/summary` | View report summary in browser |
| `/reports/export/pdf` | Download PDF report |
| `/reports/export/excel` | Download Excel file |
| `/reports/export/csv` | Download CSV file |

---

### 3. REST API (`routes/api.py`)

A complete JWT-protected REST API for programmatic access.

#### Authentication:
```bash
# Step 1: Login to get JWT token
POST /auth/login
Body: {"username": "user", "password": "pass"}
Response: {"access_token": "eyJ...", "refresh_token": "eyJ..."}

# Step 2: Use token in all API requests
Authorization: Bearer eyJ...
```

#### API Endpoints:
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/scan/url` | Scan a URL for phishing |
| POST | `/api/v1/scan/password` | Analyze password strength |
| POST | `/api/v1/scan/message` | Check message for scams |
| POST | `/api/v1/scan/email` | Analyze email for phishing |
| GET | `/api/v1/history` | Get user's scan history |
| GET | `/api/v1/threats` | Get threat intelligence list |
| GET | `/api/v1/iocs` | Get IOC database |
| GET | `/api/v1/stats` | Get user statistics |

#### API Response Format:
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "risk_score": 25,
    "risk_level": "safe",
    "findings": [],
    "recommendations": ["Website appears safe."]
  }
}
```

#### Error Response Format:
```json
{
  "success": false,
  "message": "Invalid or expired token",
  "error_code": 401
}
```

#### Rate Limiting:
- API endpoints are protected against abuse
- JWT tokens expire after 24 hours
- Refresh tokens valid for 30 days

---

### 4. Frontend Templates (`templates/`)

#### Template Structure:
```
templates/
├── base.html              ← Master layout (navbar, sidebar, footer)
├── index.html             ← Landing page
├── auth/
│   ├── login.html         ← Login form
│   ├── register.html      ← Registration form
│   ├── profile.html       ← User profile page
│   ├── settings.html      ← Account settings
│   └── forgot_password.html
├── dashboard/
│   └── index.html         ← Main dashboard with charts
├── website/
│   ├── index.html         ← URL scanner form
│   ├── result.html        ← Scan results with risk gauge
│   └── history.html       ← Past scan history
├── email/
│   ├── index.html         ← Email analyzer form
│   └── result.html        ← Email analysis results
├── password/
│   └── index.html         ← Password strength checker
├── malware/
│   └── index.html         ← File upload scanner
├── network/
│   └── index.html         ← Network scanner
├── simulation/
│   ├── index.html         ← Attack simulator menu
│   ├── demo.html          ← Step-by-step attack demo
│   └── phishing/          ← 9 educational phishing pages
├── training/
│   ├── index.html         ← Training modules list
│   ├── module.html        ← Module content reader
│   ├── quiz.html          ← Quiz interface
│   ├── certificates.html  ← User certificates
│   ├── certificate_view.html ← Single certificate view
│   └── leaderboard.html   ← Rankings
├── threat/
│   ├── index.html         ← Threat browser
│   ├── search.html        ← Threat search
│   ├── mitre.html         ← MITRE ATT&CK viewer
│   ├── ioc.html           ← IOC database
│   └── explain.html       ← Threat explanation
├── reports/
│   ├── index.html         ← Reports dashboard
│   └── summary.html       ← Report summary view
├── admin/
│   ├── index.html         ← Admin dashboard
│   ├── users.html         ← User management
│   ├── logs.html          ← Audit logs
│   ├── threats.html       ← Threat management
│   ├── iocs.html          ← IOC management
│   ├── training_modules.html ← Training management
│   └── analytics.html     ← System analytics
└── errors/
    ├── 400.html, 401.html, 403.html, 404.html, 500.html
```

---

### 5. CSS & JavaScript (`static/`)

#### `static/css/main.css`
- Dark theme (default) and Light theme toggle
- Responsive design (works on mobile, tablet, desktop)
- Custom color scheme: dark navy background, cyan/green accents
- Animated risk gauge for scan results
- Card-based layout for dashboard widgets
- Sidebar navigation with icons

#### `static/js/main.js`
- Theme toggle (dark/light) with localStorage persistence
- Real-time password strength meter (updates as user types)
- AJAX form submissions (no page reload for scans)
- Chart.js integration for dashboard graphs:
  - Scan type distribution (pie chart)
  - Risk level distribution (doughnut chart)
  - Weekly scan trend (line chart)
- Notification bell with unread count
- Copy-to-clipboard for certificates
- File drag-and-drop for malware scanner

---

## ✅ Month 5 Deliverables
- [x] Admin panel with user management
- [x] Audit log viewer with filters
- [x] Threat and IOC management for admin
- [x] PDF report export (ReportLab)
- [x] Excel report export (OpenPyXL)
- [x] CSV report export
- [x] Complete REST API with JWT auth
- [x] All 40+ HTML templates created
- [x] Dark/light theme CSS
- [x] Interactive JavaScript (charts, AJAX, real-time updates)
- [x] Responsive mobile-friendly design
- [x] Error pages (400, 401, 403, 404, 500)

---

## 📅 Next Month Preview (Month 6)
- Write automated tests (pytest)
- Docker containerization
- CI/CD pipeline (GitHub Actions)
- Final testing, bug fixes
- Project documentation completion
- Deployment preparation
