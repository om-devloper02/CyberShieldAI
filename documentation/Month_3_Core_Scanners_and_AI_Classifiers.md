# Month 3 — Core Scanners & AI Classifiers
## CyberShield AI | M.Sc. Cyber Security Final Year Project

---

## 🎯 Goal of This Month
Build all the core scanning engines — Website Scanner, Email Analyzer, Password Analyzer, Malware Scanner — and the AI classification system.

---

## 📌 What Was Done in Month 3

### 1. Website / URL Scanner (`scanner/website/analyzer.py`)

This is the most important scanner. It performs **13 different checks** on any URL.

#### How It Works:
```
User enters URL → 13 checks run → Risk Score calculated → Risk Level assigned
```

#### 13 Checks Performed:
| # | Check | Risk Points Added | What It Detects |
|---|-------|------------------|----------------|
| 1 | HTTPS Check | +20 if no HTTPS | Unencrypted connection |
| 2 | SSL Certificate | +25 if invalid | Expired or fake SSL |
| 3 | Domain Age (WHOIS) | +30 if < 30 days | Newly created phishing domains |
| 4 | Short URL Detection | +20 if detected | Hidden destination URLs |
| 5 | Typosquatting | +35 if detected | Fake brand domains (paypa1.com) |
| 6 | Homograph Attack | +40 if detected | Unicode lookalike characters |
| 7 | Suspicious Keywords | +20 if 3+ found | login, verify, account, secure |
| 8 | IP Address URL | +30 if detected | Direct IP instead of domain |
| 9 | Excessive Subdomains | +15 if > 3 | paypal.evil.attacker.com |
| 10 | URL Length | +10 if > 100 chars | Obfuscated long URLs |
| 11 | Special Characters | +10 if excessive | %20, @, = in URL |
| 12 | Page Content Analysis | +25/+20 | Fake login forms, hidden redirects |
| 13 | Google Safe Browsing | +50 if flagged | Known malicious URLs |

#### Risk Level Calculation:
```
Score 0-34   → SAFE (green)
Score 35-64  → SUSPICIOUS (yellow)
Score 65-100 → DANGEROUS (red)
```

#### Key Functions:
- `analyze_url(url)` — Main function, runs all 13 checks
- `_check_ssl(domain)` — Connects to port 443, validates certificate
- `_check_domain_age(domain)` — WHOIS lookup for creation date
- `_check_typosquatting(domain)` — Levenshtein distance algorithm
- `_check_homograph(domain)` — Detects non-ASCII Unicode characters
- `_analyze_page_content(url)` — Downloads page, checks for fake forms
- `_check_google_safe_browsing(url, api_key)` — Google API check
- `analyze_qr_code(image_path)` — Scans QR codes for malicious URLs

#### Typosquatting Detection Algorithm:
```python
# Levenshtein Distance — counts minimum edits to convert one string to another
# Example: "paypa1" vs "paypal" = distance of 1 (one character different)
# If distance <= 2 and brand name length > 4 → TYPOSQUATTING DETECTED
```

---

### 2. Email Phishing Analyzer (`scanner/email/analyzer.py`)

Analyzes email headers and content for phishing indicators.

#### What It Checks:
- SPF (Sender Policy Framework) — Is sender authorized?
- DKIM (DomainKeys Identified Mail) — Is email signature valid?
- DMARC — Does domain have anti-spoofing policy?
- Email header analysis — Reply-To mismatch, suspicious routing
- Content analysis — Urgency words, suspicious links, attachments
- Sender domain age — New domains are suspicious

---

### 3. Password Strength Analyzer (`scanner/password_analyzer.py`)

#### Analysis Steps:
| Step | What It Does |
|------|-------------|
| 1 | Character set analysis (lowercase, uppercase, digits, special) |
| 2 | Entropy calculation (bits of randomness) |
| 3 | Strength scoring (0-100) |
| 4 | Common password check (24 most common passwords) |
| 5 | Dictionary word check |
| 6 | Crack time estimation (5 attack types) |
| 7 | Sequential pattern detection (123, abc, qwerty) |
| 8 | HaveIBeenPwned API check |

#### Entropy Formula:
```
Entropy = password_length × log2(charset_size)

Example: 12-char password with all 4 types:
charset = 26+26+10+32 = 94 characters
Entropy = 12 × log2(94) = 12 × 6.55 = 78.6 bits → STRONG
```

#### Crack Time Estimation:
| Attack Type | Speed | Example |
|-------------|-------|---------|
| Online Slow | 100/sec | Login form with rate limiting |
| Online Fast | 10,000/sec | No rate limiting |
| Offline Slow | 1,000,000/sec | MD5 hash cracking |
| Offline Fast | 1,000,000,000/sec | GPU hash cracking |
| GPU Cluster | 100,000,000,000/sec | Professional cracking rig |

#### HaveIBeenPwned Integration (k-Anonymity):
```
Password → SHA1 hash → Send only first 5 chars to API
API returns all hashes starting with those 5 chars
Check locally if full hash is in the list
→ Password NEVER sent to external server (privacy safe!)
```

#### Strength Levels:
```
Score 80-100 → Very Strong 💪
Score 60-79  → Strong ✅
Score 40-59  → Moderate ⚠️
Score 20-39  → Weak ❌
Score 0-19   → Very Weak 🚨
```

---

### 4. Malware File Scanner (`scanner/malware/analyzer.py`)

#### What It Does:
- Generates MD5, SHA1, SHA256 hashes of uploaded file
- Checks against YARA rules for malware patterns
- Looks up hash on VirusTotal API
- Checks file extension vs actual file content (extension spoofing)
- Analyzes file entropy (high entropy = possibly encrypted/packed malware)

#### File Safety:
- Files are scanned in memory
- Deleted immediately after scanning
- Never stored permanently
- Max file size: 16MB

---

### 5. Network Scanner (`scanner/network/scanner.py`)

#### Features:
- Discovers devices on local network
- Scans common ports (21, 22, 23, 25, 80, 443, 3306, 8080, etc.)
- Identifies open services
- Flags risky open ports (Telnet:23, FTP:21, RDP:3389)
- Risk assessment per device

---

### 6. AI Classifiers (`ai/classifiers/classifier.py`)

#### Three Classifiers Built:

**A. URLClassifier**
- Extracts 14 features from any URL
- Scores each feature with risk weight
- Returns: label (phishing/legitimate), confidence %, phishing probability

**B. EmailClassifier**
- 6 regex patterns for spam/phishing detection
- Checks for urgency words, ALL CAPS subject, excessive links
- Returns: label, confidence, matched patterns

**C. ScamMessageClassifier**
- Detects 7 types of scams: prize, bank, investment, job, courier, UPI, OTP
- Checks for URLs, phone numbers, urgency words
- Designed for Indian scam patterns (UPI, KYC, OTP scams)
- Returns: scam type, confidence, detected keywords

**D. ThreatExplainer**
- Explains 10 threat types in plain English
- Provides MITRE ATT&CK technique mapping
- Lists specific mitigations for each threat
- Assigns severity level (critical/high/medium/low)

---

## ✅ Month 3 Deliverables
- [x] Website URL Scanner with 13 checks
- [x] SSL certificate validation
- [x] WHOIS domain age lookup
- [x] Typosquatting detection (Levenshtein algorithm)
- [x] Google Safe Browsing API integration
- [x] QR code URL scanner
- [x] Email phishing analyzer (SPF/DKIM/DMARC)
- [x] Password analyzer with entropy + crack time
- [x] HaveIBeenPwned k-anonymity integration
- [x] Malware file scanner with YARA + VirusTotal
- [x] Network port scanner
- [x] URL, Email, Scam AI classifiers
- [x] Threat explainer with MITRE ATT&CK mapping

---

## 📅 Next Month Preview (Month 4)
- Build Attack Simulator (8 attack demos)
- Build Security Training system (lessons + quizzes + certificates)
- Build Threat Intelligence module
- Build AI Security Assistant (chatbot)
