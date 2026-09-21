# Support Policy for Ars Arcanum

Thank you for using Ars Arcanum! This document outlines our support policy, community channels, and expectations.

---

## Supported Versions

| Version | Status | Security Patches | Bug Fixes |
| :--- | :--- | :--- | :--- |
| **1.6.x** | **Current Stable** | ✅ Yes | ✅ Yes |
| **1.5.x** | Deprecated | ⚠️ Critical Only | ❌ No |
| **< 1.5.0** | End of Life | ❌ No | ❌ No |

---

## How to Get Support

1. **Author Manual & Docs**: Check the comprehensive [Author Manual](docs/AUTHOR_MANUAL.md) and [Architecture Documentation](docs/ARCHITECTURE.md).
2. **Built-in Diagnostics**: Run `arcanum doctor` or `arcanum doctor --report` to diagnose your installation, toolchain dependencies, and manuscript integrity.
3. **Bug Reports**: If you discover a defect, submit a [Bug Report](https://github.com/aryansinghnagar/Scriptorium/issues/new?template=bug_report.yml) with your diagnostic report.
4. **Feature Proposals**: Submit ideas via [Feature Requests](https://github.com/aryansinghnagar/Scriptorium/issues/new?template=feature_request.yml).
5. **Security Vulnerabilities**: Report security issues privately via [GitHub Private Vulnerability Reporting](https://github.com/aryansinghnagar/Scriptorium/security/advisories/new).

---

## Operating Environment Support

Ars Arcanum targets offline Linux authoring workstations. Detailed platform tiers are maintained in [docs/SUPPORT_MATRIX.md](docs/SUPPORT_MATRIX.md).

- **Tier 1 (Target Reference)**: Linux Mint 21/22 XFCE, Debian 12/13 XFCE (x86_64).
- **Tier 2 (Compatible)**: Ubuntu 22.04/24.04 LTS, Debian derivatives, Linux ARM64 (aarch64).
