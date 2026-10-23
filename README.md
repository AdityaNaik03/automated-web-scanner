# Automated Web Security Scanner: Secure Headers & CORS Audit Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/OWASP-A05%3A2021--Security%20Misconfiguration-red.svg)](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
[![Audit](https://img.shields.io/badge/Audit-Headers%20%26%20CORS-purple.svg)]()

> **Author:** Aditya Dasharath Naik  
> **Topic:** Automated Web Scanner: Python script for secure headers and CORS flaws  
> **Course / Program:** Information & Network Security / Web Application Security Bootcamp  
> **Format Deliverables:** `.ipynb` (Jupyter Notebook), `.py` (CLI), `requirements.txt`, `AdityaNaik_ProjectReport.docx`, `README.md`

---

## 📌 1. Project Overview

The **Automated Web Security Scanner** is a defensive, non-invasive Python security auditing tool that systematically evaluates web applications for client-side and transport-layer vulnerabilities. Modern web security relies heavily on browser-enforced security mechanisms. When web servers omit defensive HTTP response headers or misconfigure Cross-Origin Resource Sharing (CORS) rules, client browsers are left unable to defend users against critical attacks including **Cross-Site Scripting (XSS)**, **Clickjacking**, **MIME-type Confusion**, and **Unauthorized Cross-Origin Data Exfiltration**.

This project provides an automated, reproducible scanning engine that:
1. **Audits 6 Core Defensive HTTP Headers** for presence, directive syntax, and security strength.
2. **Flags Server Information Disclosure** headers (`Server`, `X-Powered-By`, etc.) that aid attacker reconnaissance.
3. **Simulates 4 Distinct CORS Attack Vectors** to identify dangerous origin reflection and credential-sharing flaws.
4. **Calculates a Weighted Security Posture Score (0–100)** and assigns an industry-standard letter grade (`A+` to `F`).
5. **Generates Multi-Format Reports**: Terminal ASCII tables (`tabulate`) and structured machine-readable JSON artifacts.

---

## 🎯 2. Threat Model & Audit Capabilities

### A. HTTP Defensive Security Headers
| Header | RFC / Standard | Severity | Security Impact Audited |
| :--- | :--- | :--- | :--- |
| **Strict-Transport-Security (HSTS)** | RFC 6797 | High | Enforces HTTPS; prevents SSL-stripping and downgrade Man-in-the-Middle (MitM) attacks. Checks `max-age >= 31536000` and `includeSubDomains`. |
| **Content-Security-Policy (CSP)** | W3C CSP Level 3 | Critical | Restricts resource loading to mitigate XSS and code injection. Flags missing policy and unsafe directives (`'unsafe-inline'`, `'unsafe-eval'`). |
| **X-Frame-Options** | RFC 7034 | Medium | Prevents UI redressing / Clickjacking by restricting `<iframe>` embedding (`DENY` or `SAMEORIGIN`). |
| **X-Content-Type-Options** | W3C Fetch Spec | Medium | Disables browser MIME-sniffing vulnerabilities. Validates explicit `nosniff` directive. |
| **Referrer-Policy** | W3C Referrer Policy | Low | Protects user privacy and sensitive URL query tokens from leaking across origins (`strict-origin-when-cross-origin`, `no-referrer`). |
| **Permissions-Policy** | W3C Feature Policy | Low | Enforces least-privilege access to sensitive browser hardware APIs (camera, microphone, geolocation, payment). |

### B. Information Disclosure Detection
- Audits response headers for server banners: `Server`, `X-Powered-By`, `X-AspNet-Version`, `X-Runtime`, `X-Version`.
- Recommends header sanitization to hinder automated exploit scanning (banner grabbing).

### C. Cross-Origin Resource Sharing (CORS) Probing Suite
The scanner probes target endpoints against four specialized origin scenarios:
1. **Arbitrary Origin Reflection (`https://evil-attacker.com`):** Detects whether the server mirrors any incoming `Origin` header. If paired with `Access-Control-Allow-Credentials: true`, an external attacker can steal private user sessions, API tokens, and PII.
2. **Null Origin Exploitation (`Origin: null`):** Evaluates if sandboxed iframes (`<iframe sandbox="...">`) or `data:` URI exploits can trigger authenticated cross-origin reads.
3. **Subdomain / Regex Confusion (`https://{target}.evil-attacker.com`):** Uncovers unanchored server-side regex whitelists (e.g., matching `target.com` inside `target.com.attacker.com`).
4. **Suffix Domain Bypass (`https://attacker-{target}`):** Detects prefix-matching flaws where arbitrary domains ending with the target string are allowed.

---

## 🏗️ 3. Architecture & Scanner Workflow

```
[Target URL Input]
        │
        ▼
[WebSecurityScanner Engine]
        │
        ├─── 1. HTTP Session Initialization (Custom AuditBot User-Agent)
        │
        ├─── 2. Defensive Header Inspection
        │        ├── Presence Check against Baseline Policy
        │        ├── Directive Strength Validation (Regex / Token Parser)
        │        └── Information Disclosure Banner Audit
        │
        ├─── 3. Active CORS Fuzzing
        │        ├── Arbitrary Origin Test
        │        ├── Null Origin Test
        │        ├── Subdomain Confusion Test
        │        └── Suffix Bypass Test
        │        └── Evaluate ACAO + ACAC Combination
        │
        ├─── 4. Posture Scoring & Grading Engine (0 - 100 Posture Scale)
        │
        └─── 5. Multi-Channel Output Generation
                 ├── Terminal Grid Tables (tabulate)
                 └── JSON Export (audit_results.json)
```

---

## 🛠️ 4. Technologies Used

- **Language:** Python 3.10+
- **HTTP Engine:** `requests` (Session management, redirect handling, case-insensitive headers)
- **Table Formatting:** `tabulate` (Clean ASCII terminal visualization)
- **Serialization:** `json` (Structured SIEM/DevSecOps output)
- **Documentation Engine:** `python-docx` (Automated generation of formal project report)
- **Specifications Referenced:** RFC 6797 (HSTS), RFC 7034 (X-Frame-Options), W3C CSP Level 3, W3C CORS, OWASP Top 10 (A05:2021 - Security Misconfiguration)

---

## 📂 5. Project Structure & Deliverables

```
├── AdityaNaik_AutomatedWebScanner.ipynb   # Complete interactive Jupyter Notebook with executed outputs
├── AdityaNaik_AutomatedWebScanner.py      # Standalone, production-ready CLI scanner script
├── AdityaNaik_ProjectReport.docx         # Comprehensive formal project report (Microsoft Word format)
├── requirements.txt                      # List of Python dependencies
├── README.md                             # Project documentation, threat model, and usage guide
├── audit_results.json                    # Sample exported audit report in JSON format
└── gemini-code-1792768670920.md          # Architecture and initial project notes
```

---

## 🚀 6. Setup & Execution Instructions

### Step 1: Clone or Extract Repository
```bash
git clone https://github.com/AdityaNaik/automated-web-scanner.git
cd automated-web-scanner
```

### Step 2: Install Dependencies
Ensure Python 3.10 or higher is installed, then run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Scanner

#### Option A: Command Line Interface (CLI)
```bash
# Scan default testbed (httpbin.org)
python AdityaNaik_AutomatedWebScanner.py

# Scan custom target URL
python AdityaNaik_AutomatedWebScanner.py --url https://github.com

# Scan with custom timeout and custom output file
python AdityaNaik_AutomatedWebScanner.py --url https://example.com --timeout 15 --output report.json
```

#### Option B: Interactive Jupyter Notebook
Launch Jupyter Notebook or JupyterLab:
```bash
jupyter notebook AdityaNaik_AutomatedWebScanner.ipynb
```
Execute cells sequentially (`Shift + Enter`) to run live audits, view formatted tables, and inspect exported JSON artifacts.

---

## 📊 7. Test Targets & Experimental Results

### Target 1: `https://httpbin.org` (Vulnerable Baseline / Testbed)
- **Score:** `0/100` | **Grade:** `F (Vulnerable)`
- **Defensive Headers:** Missing HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
- **Information Leak:** Disclosed `Server: gunicorn/19.9.0`.
- **CORS Result:** **Critical Vulnerability**. The endpoint dynamically reflects any tested origin (`https://evil-attacker.com`, `null`, etc.) with `Access-Control-Allow-Credentials: true`.

```
============================================================
  AUTOMATED WEB SECURITY SCANNER REPORT
============================================================
Target URL:            https://httpbin.org
HTTP Status Code:      200
Overall Score:         0/100 [Grade: F (Vulnerable)]
============================================================
[-] MISSING SECURITY HEADERS:
+------------+---------------------------+-----------------------------------------------------------------------------------+
| Severity   | Header                    | Remediation                                                                       |
+============+===========================+===================================================================================+
| High       | Strict-Transport-Security | Ensure max-age >= 31536000 and include 'includeSubDomains; preload'.              |
| Critical   | Content-Security-Policy   | Avoid 'unsafe-inline' and 'unsafe-eval'; define strict default-src or script-src. |
| Medium     | X-Frame-Options           | Set to 'DENY' or 'SAMEORIGIN' (or use CSP frame-ancestors).                       |
| Medium     | X-Content-Type-Options    | Set explicitly to 'nosniff'.                                                      |
| Low        | Referrer-Policy           | Set to 'strict-origin-when-cross-origin' or 'no-referrer'.                        |
| Low        | Permissions-Policy        | Explicitly declare allowed feature origins (e.g., geolocation=(), camera=()).     |
+------------+---------------------------+-----------------------------------------------------------------------------------+

[CRITICAL] CORS FLAW DETECTED:
+------------+------------------------------------------------------+---------------------------+--------+
| Severity   | Vector                                               | ACAO                      | ACAC   |
+============+======================================================+===========================+========+
| Critical   | Arbitrary Third-Party Origin Reflection              | https://evil-attacker.com | true   |
| Critical   | Null Origin Reflection (Sandboxed/Data URI exploits) | null                      | true   |
+------------+------------------------------------------------------+---------------------------+--------+
```

### Target 2: `https://github.com` (Hardened Production Service)
- **Score:** `76/100` | **Grade:** `B`
- **Defensive Headers:** Implements strong HSTS (`max-age=31536000; includeSubDomains; preload`), strict X-Frame-Options (`deny`), and X-Content-Type-Options (`nosniff`).
- **CORS Result:** Passed all 4 CORS origin fuzzing tests with zero unauthorized origin reflections.

---

## 🛡️ 8. Remediation & Hardening Guidelines

### Nginx (`nginx.conf`)
```nginx
# Secure Defensive Headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none';" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

# Suppress Server Information Disclosure
server_tokens off;
```

### Express.js (Node.js)
```javascript
const helmet = require('helmet');
const cors = require('cors');

// Enforce standard defensive headers
app.use(helmet());

// Safe CORS Whitelist (Never reflect arbitrary origins with credentials)
const whitelist = ['https://trusted-client.com', 'https://app.trusted-client.com'];
const corsOptions = {
  origin: function (origin, callback) {
    if (!origin || whitelist.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Blocked by CORS security policy'));
    }
  },
  credentials: true
};
app.use(cors(corsOptions));
```

---

## 📜 9. License & Disclaimer

This project is released under the **MIT License**.  
**Disclaimer:** This tool is designed strictly for authorized security auditing, defensive assessments, and educational purposes. Always obtain explicit permission before scanning targets that you do not own or administer.
