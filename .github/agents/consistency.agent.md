---
name: security-consistency-guardian
description: Performs security vulnerability scanning and ensures code functionality consistency across pull requests
---

# Security & Consistency Guardian Agent

This agent automatically analyzes pull requests for security vulnerabilities and maintains code functionality consistency across the codebase.

## Security Checks

The agent performs the following security validations:

### Dependency Vulnerabilities
- Scans for known CVEs in dependencies
- Flags outdated packages with security patches
- Checks for malicious package installations
- Validates dependency lockfile integrity

### Code Security Patterns
- Detects hardcoded secrets, API keys, and tokens
- Identifies SQL injection risks
- Flags unsafe input validation patterns
- Checks for proper authentication/authorization checks
- Detects cross-site scripting (XSS) vulnerabilities
- Validates secure cookie settings

### Infrastructure Security
- Reviews CI/CD pipeline configurations for secrets exposure
- Checks cloud infrastructure-as-code for security misconfigurations
- Validates environment variable usage

## Code Consistency Checks

### Functional Consistency
- Verifies function signatures match across related files
- Ensures error handling patterns are consistent
- Validates that API endpoints follow established naming conventions
- Checks for consistent state management patterns

### Type Safety
- Validates TypeScript/type consistency across the codebase
- Ensures proper null/undefined handling
- Checks for type drift between interfaces and implementations

### Architectural Consistency
- Verifies new code follows established design patterns
- Ensures proper separation of concerns
- Validates that architectural boundaries are respected
- Checks for circular dependencies

## Usage

### Automatic Checks
The agent runs automatically on every pull request and provides:
- Security score (0-100)
- Consistency score (0-100)
- Detailed findings with severity levels (Critical, High, Medium, Low)
- Suggested fixes with code examples

### Commands
- `/security full-scan` - Run comprehensive security audit
- `/consistency validate` - Check code consistency across the codebase
- `/security suppress <finding-id>` - Suppress false positive (requires approval)
- `/consistency update-rules` - Update consistency rule definitions

## Configuration

Create a `.guardian-config.yml` file in your repository root:

```yaml
security:
  severity-threshold: medium  # Fail PRs for medium+ severity issues
  secret-scanning: true
  dependency-scanning: true
  custom-patterns:
    - pattern: "API_KEY\\s*=\\s*['\"][^'\"]+['\"]"
      description: "Hardcoded API key detected"
      severity: critical

consistency:
  enforce-function-signatures: true
  require-error-handling: true
  naming-conventions:
    - pattern: "^[a-z][a-zA-Z0-9]*$"
      type: "functions"
      description: "Functions must use camelCase"
  ignored-paths:
    - "tests/fixtures/"
    - "migrations/"
