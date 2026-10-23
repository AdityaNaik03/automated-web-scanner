"""
Automated Web Security Scanner: Secure Headers & CORS Misconfigurations
Author: Aditya Dasharath Naik
Project: Automated Web Security Scanner
Platform: Python 3.10+ / CLI & Jupyter Notebook
"""

import sys
import argparse
import json
import re
from urllib.parse import urlparse
from typing import Dict, List, Any
from datetime import datetime, timezone
import requests
import tabulate

# Baseline Security Header Policies
SECURITY_HEADERS_POLICY = {
    "Strict-Transport-Security": {
        "severity": "High",
        "description": "Enforces secure (HTTPS) connections and protects against SSL-stripping MITM attacks.",
        "recommendation": "Ensure max-age >= 31536000 and include 'includeSubDomains; preload'.",
        "check_func": lambda val: "includesubdomains" in val.lower() and int(re.search(r'max-age=(\d+)', val, re.IGNORECASE).group(1) if re.search(r'max-age=(\d+)', val, re.IGNORECASE) else 0) >= 31536000
    },
    "Content-Security-Policy": {
        "severity": "Critical",
        "description": "Restricts resource loading to mitigate Cross-Site Scripting (XSS) and data injection.",
        "recommendation": "Avoid 'unsafe-inline' and 'unsafe-eval' in script-src; define strict default-src or script-src.",
        "check_func": lambda val: not bool(re.search(r'(?:script-src|default-src)[^;]*[\'"]unsafe-inline[\'"]', val, re.I)) and ("default-src" in val.lower() or "script-src" in val.lower())
    },
    "X-Frame-Options": {
        "severity": "Medium",
        "description": "Prevents Clickjacking by restricting whether the site can be embedded in an iframe.",
        "recommendation": "Set to 'DENY' or 'SAMEORIGIN' (or use CSP frame-ancestors).",
        "check_func": lambda val: val.strip().upper() in ["DENY", "SAMEORIGIN"]
    },
    "X-Content-Type-Options": {
        "severity": "Medium",
        "description": "Disables MIME-sniffing vulnerabilities, preventing browsers from interpreting text as HTML/JS.",
        "recommendation": "Set explicitly to 'nosniff'.",
        "check_func": lambda val: val.strip().lower() == "nosniff"
    },
    "Referrer-Policy": {
        "severity": "Low",
        "description": "Controls how much referrer information is sent along with requests.",
        "recommendation": "Set to 'strict-origin-when-cross-origin' or 'no-referrer'.",
        "check_func": lambda val: any(p in ["strict-origin-when-cross-origin", "no-referrer", "same-origin"] for p in [t.strip().lower() for t in val.split(",")])
    },
    "Permissions-Policy": {
        "severity": "Low",
        "description": "Restricts browser features like camera, microphone, geolocation, and payment APIs.",
        "recommendation": "Explicitly declare allowed feature origins (e.g., geolocation=(), camera=()).",
        "check_func": lambda val: len(val.strip()) > 0
    }
}

DISCLOSURE_HEADERS = ["Server", "X-Powered-By", "X-AspNet-Version", "X-Runtime", "X-Version"]


class WebSecurityScanner:
    """
    Automated security scanner for auditing HTTP defensive headers
    and CORS origin validation vulnerabilities.
    """

    def __init__(self, target_url: str, timeout: int = 10):
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AutomatedSecurityAuditBot/1.0 (+https://github.com/AdityaNaik/SecScanner)"
        })
        self.findings = {
            "target": self.target_url,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": None,
            "headers_analyzed": {},
            "missing_headers": [],
            "misconfigured_headers": [],
            "information_leakage": [],
            "cors_vulnerabilities": [],
            "score": 100,
            "rating": "A+"
        }

    def scan_security_headers(self) -> None:
        """Audits present, missing, and misconfigured HTTP headers."""
        try:
            response = self.session.get(self.target_url, timeout=self.timeout, allow_redirects=True)
            self.findings["status_code"] = response.status_code
            headers = response.headers
            self.findings["headers_analyzed"] = dict(headers)

            # 1. Audit Missing & Weak Defensive Headers
            for header, rule in SECURITY_HEADERS_POLICY.items():
                if header not in headers:
                    self.findings["missing_headers"].append({
                        "header": header,
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "recommendation": rule["recommendation"]
                    })
                    deductions = {"Critical": 25, "High": 15, "Medium": 10, "Low": 5}
                    self.findings["score"] -= deductions.get(rule["severity"], 5)
                else:
                    val = headers[header]
                    is_secure = rule["check_func"](val)
                    if not is_secure:
                        self.findings["misconfigured_headers"].append({
                            "header": header,
                            "current_value": val,
                            "severity": rule["severity"],
                            "issue": f"Weak or incomplete directive in '{header}'",
                            "recommendation": rule["recommendation"]
                        })
                        self.findings["score"] -= 8

            # 2. Audit Server / Tech Banner Leaks
            for d_header in DISCLOSURE_HEADERS:
                if d_header in headers:
                    self.findings["information_leakage"].append({
                        "header": d_header,
                        "value": headers[d_header],
                        "severity": "Low",
                        "recommendation": f"Suppress or sanitize '{d_header}' banner in web server configuration."
                    })
                    self.findings["score"] -= 3

        except requests.RequestException as e:
            self.findings["error"] = f"Connection error: {str(e)}"

    def scan_cors_vulnerabilities(self) -> None:
        """Tests CORS misconfigurations using diverse Origin vectors."""
        domain = self.parsed_url.netloc
        test_cases = [
            {
                "name": "Arbitrary Third-Party Origin Reflection",
                "origin": "https://evil-attacker.com",
                "expected": "Should NOT reflect arbitrary origin with credentials."
            },
            {
                "name": "Null Origin Reflection (Sandboxed/Data URI exploits)",
                "origin": "null",
                "expected": "Should NOT trust null origin."
            },
            {
                "name": "Prefix / Subdomain Confusion Bypass",
                "origin": f"https://{domain}.evil-attacker.com",
                "expected": "Should NOT match via improper regex or substring."
            },
            {
                "name": "Suffix Domain Bypass",
                "origin": f"https://attacker-{domain}",
                "expected": "Should reject non-whitelisted domain prefix."
            }
        ]

        for tc in test_cases:
            headers = {"Origin": tc["origin"]}
            try:
                res = self.session.get(self.target_url, headers=headers, timeout=self.timeout)
                acao = res.headers.get("Access-Control-Allow-Origin")
                acac = res.headers.get("Access-Control-Allow-Credentials")

                if acao:
                    # Critical: Reflected Origin + Credentials
                    if (acao == tc["origin"] or acao == "*") and acac and acac.lower() == "true":
                        self.findings["cors_vulnerabilities"].append({
                            "vector": tc["name"],
                            "tested_origin": tc["origin"],
                            "severity": "Critical",
                            "acao": acao,
                            "acac": acac,
                            "impact": "Full credentialed cross-origin read access (API session hijacking / PII theft).",
                            "recommendation": "Never dynamically reflect the Origin header with Access-Control-Allow-Credentials: true. Implement a strict server-side whitelist."
                        })
                        self.findings["score"] -= 35
                    # High/Medium: Arbitrary Reflection without credentials
                    elif acao == tc["origin"]:
                        self.findings["cors_vulnerabilities"].append({
                            "vector": tc["name"],
                            "tested_origin": tc["origin"],
                            "severity": "Medium",
                            "acao": acao,
                            "acac": str(acac),
                            "impact": "Reflects unauthenticated arbitrary origins; may expose internal unauthenticated endpoints.",
                            "recommendation": "Restrict Access-Control-Allow-Origin to trusted explicit origins."
                        })
                        self.findings["score"] -= 15
                    # Wildcard with Credentials
                    elif acao == "*" and acac and acac.lower() == "true":
                        self.findings["cors_vulnerabilities"].append({
                            "vector": "Wildcard Origin with Credentials Enabled",
                            "tested_origin": tc["origin"],
                            "severity": "High",
                            "acao": acao,
                            "acac": acac,
                            "impact": "Breaches W3C CORS specification; potential browser parsing flaws.",
                            "recommendation": "Wildcards cannot be combined with credentials."
                        })
                        self.findings["score"] -= 20
            except requests.RequestException:
                continue

    def compute_rating(self) -> None:
        self.findings["score"] = max(0, self.findings["score"])
        score = self.findings["score"]
        if score >= 90:
            self.findings["rating"] = "A+"
        elif score >= 80:
            self.findings["rating"] = "A"
        elif score >= 70:
            self.findings["rating"] = "B"
        elif score >= 60:
            self.findings["rating"] = "C"
        elif score >= 50:
            self.findings["rating"] = "D"
        else:
            self.findings["rating"] = "F (Vulnerable)"

    def run_full_scan(self) -> Dict[str, Any]:
        self.scan_security_headers()
        self.scan_cors_vulnerabilities()
        self.compute_rating()
        return self.findings

    def print_report(self) -> None:
        results = self.findings
        print("\n" + "=" * 60)
        print(f"  AUTOMATED WEB SECURITY SCANNER REPORT")
        print("=" * 60)
        print(f"Target URL:            {results['target']}")
        print(f"HTTP Status Code:      {results['status_code']}")
        print(f"Scan Timestamp (UTC):  {results['scan_timestamp']}")
        print(f"Overall Score:         {results['score']}/100 [Grade: {results['rating']}]")
        print("=" * 60)

        # Missing Headers Table
        if results["missing_headers"]:
            print("\n[-] MISSING SECURITY HEADERS:")
            table_data = [[h["severity"], h["header"], h["recommendation"]] for h in results["missing_headers"]]
            print(tabulate.tabulate(table_data, headers=["Severity", "Header", "Remediation"], tablefmt="grid"))
        else:
            print("\n[+] All baseline security headers are present!")

        # Misconfigured Headers Table
        if results["misconfigured_headers"]:
            print("\n[!] WEAK / MISCONFIGURED HEADERS:")
            w_data = [
                [
                    h["severity"],
                    h["header"],
                    (h["current_value"][:60] + "..." if len(h["current_value"]) > 60 else h["current_value"]),
                    h["issue"]
                ]
                for h in results["misconfigured_headers"]
            ]
            print(tabulate.tabulate(w_data, headers=["Severity", "Header", "Current Value", "Issue Detected"], tablefmt="grid"))

        # Information Leaks Table
        if results["information_leakage"]:
            print("\n[!] INFORMATION DISCLOSURE DETECTED:")
            l_data = [[l["header"], l["value"], l["recommendation"]] for l in results["information_leakage"]]
            print(tabulate.tabulate(l_data, headers=["Banner Header", "Leaked Value", "Mitigation"], tablefmt="grid"))

        # CORS Vulnerabilities Table
        if results["cors_vulnerabilities"]:
            print("\n[CRITICAL] CORS FLAW DETECTED:")
            c_data = [[c["severity"], c["vector"], c["acao"], c["acac"], c["impact"]] for c in results["cors_vulnerabilities"]]
            print(tabulate.tabulate(c_data, headers=["Severity", "Vector", "ACAO", "ACAC", "Impact"], tablefmt="grid"))
        else:
            print("\n[+] CORS origin configuration passed security validation.")
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Automated Web Security Scanner: Audits HTTP Security Headers & CORS Misconfigurations."
    )
    parser.add_argument("-u", "--url", default="https://httpbin.org", help="Target URL to scan (default: https://httpbin.org)")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    parser.add_argument("-o", "--output", default="audit_results.json", help="Path to output JSON report (default: audit_results.json)")

    args = parser.parse_args()

    print(f"[*] Initializing audit for {args.url}...")
    scanner = WebSecurityScanner(target_url=args.url, timeout=args.timeout)
    results = scanner.run_full_scan()
    scanner.print_report()

    # Save JSON report
    with open(args.output, "w") as f:
        json.dump(results, f, indent=4)
    print(f"[+] Detailed JSON report exported to '{args.output}'.\n")


if __name__ == "__main__":
    main()
