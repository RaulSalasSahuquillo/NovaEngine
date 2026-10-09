# Contributing to NovaEngine

Thank you for your interest in contributing to NovaEngine. As an open-core simulation engine for financial modeling, precision, clarity, and architectural integrity are our primary priorities.

Before submitting any contributions, please review our terms and guidelines carefully.

## Mandatory Reciprocal License Terms

All contributions to NovaEngine are governed by the NovaEngine Source Reciprocal and Contribution License. Under these terms:

- Any modification, enhancement, bug fix, or extension made to NovaEngine must be contributed back to this upstream repository via pull request.
- Retaining private modifications, creating closed-source variations, or maintaining private forks without submitting upstream patches is strictly prohibited.
- If you intend to use the codebase independently, commercially, or without reciprocal upstream contributions, you must obtain prior written permission from the creator:
  Raúl Salas Sahuquillo (raulsalassahuquillo.dev@gmail.com).

By submitting a pull request, you agree that your code will be licensed under the project license.

## Code Standards and Style Guidelines

### 1. Numerical Precision and Financial Integrity
- Monetary amounts and exchange rates must be treated with precision safeguards.
- All core ledger positions must maintain a clear audit trail (broker commissions, exchange canons, transaction taxes, and capital gains withholdings).
- Never store API keys, personal credentials, or proprietary environment values in source code.

### 2. Testing Requirements
Any change affecting calculation formulas, currency harmonization, or order settlement must be backed by unit tests:
- Tax bracket calculations must include edge tests at statutory boundaries.
- Market provider tests should use mocks to avoid unnecessary network calls during continuous integration.
- Ensure the test suite passes cleanly before opening a pull request:
  `pytest`

## Pull Request Workflow

1. Fork the official repository and create a feature branch off `main`.
2. Implement your changes, adhering to human-written documentation principles and formatting standards.
3. Add or update unit tests to verify your implementation.
4. Verify that no personal data, API tokens, or temporary artifacts are staged.
5. Submit a pull request with a clear description of the problem addressed and the solution implemented.
6. A maintainer will review your pull request for code quality, architectural consistency, and numerical correctness.
