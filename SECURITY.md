# Security Policy: Scriptorium

## 1. Scope & Posture

Scriptorium is a single-user offline authoring and worldbuilding platform. It is designed to run locally on Linux workstations without persistent network listening daemons, setuid binaries, or remote service endpoints.

Security priorities for Scriptorium focus on:
- **Local Execution Safety**: Safe handling of arbitrary filenames, shell escaping, path traversal prevention, and sandboxed temporary directories.
- **Data Protection & Integrity**: Non-destructive operations, transactional directory creation, crash recovery, and verified backup archives.
- **Supply Chain Integrity**: SHA-256 digest validation of downloaded binaries (e.g., Typst) and immutable pinning of external CI actions and dependencies.

---

## 2. Supported Versions

Only the current release branch on `main` receives security updates.

| Version / Branch | Supported | Notes |
| :--- | :--- | :--- |
| `main` (Latest) | :white_check_mark: | Active engineering & security fixes |
| Legacy Drafts / Releases | :x: | Unsupported |

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability, please disclose it responsibly:

1. **Preferred Method**: Submit a report via [GitHub Private Vulnerability Reporting](https://github.com/aryansinghnagar/Scriptorium/security/advisories/new).
2. **Alternative Method**: Email the project maintainer at `aryansinghnagar@gmail.com` with the subject tag `[SECURITY: Scriptorium]`.

### Response Timeline (SLA)
- **Initial Acknowledgment**: Within **72 hours** of report receipt.
- **Assessment & Triage**: Within **7 days** of acknowledgment.
- **Patch & Advisory Publication**: Within **30 days** depending on severity and complexity.

---

## 4. What to Include in a Report
- A clear description of the vulnerability, affected components, and potential impact.
- Step-by-step reproduction instructions or a proof-of-concept script/fixture.
- Any suggested remediations or mitigations.

Please do not open public GitHub issues for undisclosed security vulnerabilities.
