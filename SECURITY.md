# Security Policy

## Supported Versions

NovaEngine maintains active security maintenance on the latest minor release line.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | Yes                |
| < 1.0   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability within NovaEngine, please report it via private disclosure rather than creating a public issue.

Send a detailed report to the project maintainer:
- Contact: Raúl Salas Sahuquillo
- Email: raulsalassahuquillo.dev@gmail.com
- Subject line format: `[SECURITY] NovaEngine Vulnerability Disclosure`

Please include the following information in your report:
- A description of the issue, including its potential severity and real-world attack vectors.
- Clear reproduction steps or a minimal proof of concept script.
- Any impacted components (for example, calculation overflow, currency conversion anomalies, or storage injection).
- Proposed remediation or patch if available.

You can expect an initial response acknowledging your report within 48 hours. We ask for coordinated disclosure so maintainers have sufficient time to audit and distribute a remediation before details are published.

## Zero Hardcoded Secrets Policy

NovaEngine is an open-core library and enforces a strict zero-credential policy:
- No private API keys, client secrets, service account credentials, or proprietary identifiers are permitted within the codebase.
- Any integrations requiring authenticated third-party endpoints must use runtime environment configuration or client parameter injection.
- Contributions found to introduce secrets or personal identifying information will be immediately declined.
