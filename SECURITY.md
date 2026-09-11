# 🔐 Security Policy

## Supported Versions

| Version | Supported |
| :--- | :--- |
| `main` (latest) | ✅ |
| Older branches | ❌ |

## 🚨 Reporting a Vulnerability

**Please do NOT open a public issue for security vulnerabilities.**

Instead, report privately via one of the following:

1. **GitHub Security Advisories** (preferred):
   https://github.com/fathiamustafamusa-hash/sentinelai/security/advisories/new

2. **Email**: fathiamustafamusa@gmail.com
   - Subject: `[SECURITY] SentinelAI - <short description>`
   - Include: description, reproduction steps, impact assessment, suggested fix

### What to expect
- **Acknowledgment** within 48 hours
- **Initial assessment** within 5 business days
- **Fix or mitigation** depending on severity

## 🛡️ Security Controls in Place

| Control | Tool | Where |
| :--- | :--- | :--- |
| SAST (Python) | Bandit | CI workflow |
| Dependency CVEs | pip-audit | CI workflow |
| Container CVEs | Trivy | CI workflow |
| Password hashing | bcrypt | app/utils/security.py |
| JWT signing | python-jose | app/utils/security.py |
| Input validation | Pydantic v2 | app/schemas/ |
| Non-root containers | Docker USER directive | Dockerfile |
| Secret management | env vars | .gitignore enforced |

## 🔍 Scope

**In scope:**
- Authentication / JWT bypass
- SQL injection
- SSRF
- Privilege escalation (RBAC bypass)
- Sensitive data exposure
- Dependency vulnerabilities

**Out of scope:**
- DoS via resource exhaustion on demo deployments
- Social engineering
- Issues in third-party tools (report upstream)

## 🙏 Thanks

We appreciate responsible disclosure and will publicly credit researchers (with permission) in release notes.
