# Month 4 — Attack Simulator, Training, Threat Intel & AI Assistant
## CyberShield AI | M.Sc. Cyber Security Final Year Project

---

## 🎯 Goal of This Month
Build the educational attack simulator, complete training system with quizzes and certificates, threat intelligence module, and the AI security assistant chatbot.

---

## 📌 What Was Done in Month 4

### 1. Attack Simulator (`routes/simulation.py`)

This is the most unique feature of the project. It shows students **how real attacks work** in a safe, educational environment. No real attacks are performed.

#### 8 Attack Simulations Built:

| # | Attack Type | What Students Learn |
|---|------------|-------------------|
| 1 | SQL Injection | How attackers bypass login with `' OR '1'='1'` |
| 2 | XSS (Cross-Site Scripting) | How scripts steal cookies via innerHTML |
| 3 | CSRF | How hidden requests transfer money from victim's session |
| 4 | Brute Force | How password lists are tried automatically |
| 5 | MITM (Man-in-the-Middle) | How ARP poisoning intercepts traffic |
| 6 | Phishing | How fake login pages steal credentials |
| 7 | DNS Spoofing | How poisoned DNS redirects to fake servers |
| 8 | DDoS | How botnets flood servers with traffic |

#### How Each Simulation Works:
Each simulation has **step-by-step code examples** showing:
1. The vulnerable code (what attackers exploit)
2. The attacker's payload (what they inject)
3. The resulting damage (what happens)
4. The secure fix (how to prevent it)

#### Example — SQL Injection Steps:
```
Step 1: Vulnerable Query
SELECT * FROM users WHERE username='{input}' AND password='{pass}'
↓
Step 2: Attacker Input
' OR '1'='1' --
↓
Step 3: Resulting Query (bypasses password!)
SELECT * FROM users WHERE username='' OR '1'='1' --' AND password=''
↓
Step 4: Safe Fix (Parameterized Query)
cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
```

#### Phishing Page Simulations (9 Types):
Educational fake pages that show students what phishing looks like:
| Page Type | Simulates |
|-----------|----------|
| login | Generic login phishing |
| bank | Fake bank login page |
| social_media | Fake social media login |
| shopping | Fake e-commerce page |
| lottery | Lottery scam page |
| courier | Fake delivery notification |
| investment | Investment scam page |
| crypto | Fake crypto exchange |
| upi | UPI payment scam (India-specific) |

> ⚠️ All pages show a warning banner: "THIS IS AN EDUCATIONAL SIMULATION"

---

### 2. Security Training System (`routes/training.py`)

#### Complete Learning Path:
```
Student → Select Module → Read Content → Take Quiz → Pass (70%+) → Get Certificate
```

#### 6 Training Modules:
| # | Module | Difficulty | Duration |
|---|--------|-----------|---------|
| 1 | Introduction to Cyber Security | Beginner | 15 min |
| 2 | Phishing Awareness | Beginner | 20 min |
| 3 | Password Security | Beginner | 15 min |
| 4 | Malware Fundamentals | Intermediate | 25 min |
| 5 | Network Security Basics | Intermediate | 20 min |
| 6 | Web Application Security | Advanced | 30 min |

#### Quiz System:
- Multiple choice questions (A, B, C, D)
- Each question worth 10 points
- Pass mark: 70%
- Explanation shown after each answer
- Time tracking (how long student took)
- Results saved to database

#### Certificate System:
- Auto-generated on passing quiz
- Unique certificate ID (e.g., `CERT-2024-ABC123`)
- Shows: student name, module name, date, score
- Viewable and shareable

#### Leaderboard:
- Ranks all users by total score
- Shows: rank, username, total score, modules completed, challenges completed
- Updates in real-time

#### Daily Challenge:
- New challenge every day
- Example: "Spot the Phish — identify 3 red flags in a suspicious email"
- Hint available
- 50 points reward

---

### 3. Threat Intelligence Module (`routes/threat.py`)

#### Features:
| Route | Purpose |
|-------|---------|
| `/threat/` | Browse all threats by category |
| `/threat/search` | Search threats by name/keyword |
| `/threat/mitre` | MITRE ATT&CK technique browser |
| `/threat/ioc` | Indicators of Compromise database |
| `/threat/explain/<type>` | Detailed threat explanation |

#### MITRE ATT&CK Integration:
Each threat is mapped to:
- **Technique ID** (e.g., T1566 for Phishing)
- **Tactic** (e.g., Initial Access, Execution, Impact)
- **Severity** (low, medium, high, critical)

#### IOC (Indicators of Compromise) Database:
Types of IOCs stored:
| Type | Example | Use |
|------|---------|-----|
| domain | secure-login-verify.tk | Phishing domain |
| ip | 192.0.2.100 | C2 server IP |
| hash | e3b0c44... | Malware file hash |
| url | http://fake-bank.xyz | Fake login URL |
| email | phish@evil.com | Phishing sender |

---

### 4. AI Security Assistant (`routes/assistant.py`)

A rule-based chatbot that answers cyber security questions.

#### How It Works:
```
User types message → Check knowledge base → Check threat keywords → 
Check scam indicators → Check tip requests → Return response
```

#### Knowledge Base (13 Topics):
| Topic | What It Explains |
|-------|----------------|
| phishing | How to identify and avoid phishing |
| password | Strong password creation tips |
| malware | Types and prevention |
| ransomware | Backup strategy, prevention |
| vpn | When and how to use VPN |
| 2fa | Why authenticator apps > SMS |
| social engineering | How to verify requests |
| zero day | Defence-in-depth strategy |
| firewall | Configuration best practices |
| encryption | TLS, AES usage |
| sql injection | Parameterized queries fix |
| xss | Output encoding, CSP fix |
| ddos | CDN, rate limiting mitigation |

#### Scam Message Analyzer:
- User pastes a suspicious SMS/WhatsApp/Telegram message
- System analyzes for 7 scam types
- Returns: scam type, confidence, detected keywords, risk level

#### Response Types:
| Type | When Used |
|------|----------|
| knowledge | Topic found in knowledge base |
| explanation | "What is..." or "Explain..." questions |
| tip | "How to stay safe", "advice" requests |
| redirect | "Is this a scam?" → directs to analyzer |
| default | Unknown question → shows topic suggestions |

---

## ✅ Month 4 Deliverables
- [x] 8 attack simulations with step-by-step code demos
- [x] 9 educational phishing page simulations
- [x] 6 training modules with content
- [x] Quiz system with scoring and explanations
- [x] Auto certificate generation on passing
- [x] Leaderboard with real-time rankings
- [x] Daily challenge system
- [x] Threat intelligence browser
- [x] MITRE ATT&CK technique mapping
- [x] IOC database with search
- [x] AI chatbot with 13-topic knowledge base
- [x] Scam message analyzer (SMS/WhatsApp/Telegram)

---

## 📅 Next Month Preview (Month 5)
- Build Admin Panel (user management, audit logs, analytics)
- Build Reports module (PDF, Excel, CSV export)
- Build REST API with JWT authentication
- Build frontend (HTML templates, CSS dark/light theme, JS)
