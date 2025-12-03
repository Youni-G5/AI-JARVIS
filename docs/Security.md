# Security Policy

## Overview

AI-JARVIS takes security seriously. This document outlines our security practices and how to report vulnerabilities.

## Security Features

### 1. Sandboxed Execution

- All system actions run in isolated containers
- Resource limits enforced (CPU, memory, network)
- No access to sensitive system paths
- Read-only filesystem for most operations

### 2. Action Validation

**Multi-layer validation:**
1. Permission check (YAML rules)
2. Argument validation (Pydantic)
3. Safety level assessment
4. Sandbox requirement

### 3. Audit Logging

- All actions logged with timestamp
- User context recorded
- Results and errors tracked
- Logs stored securely

### 4. Dry-run Mode

- Test actions without execution
- Validate plans before running
- Review potential impact

### 5. Rate Limiting

- API rate limits per endpoint
- Prevents abuse and DoS
- Configurable thresholds

---

## Dangerous Actions Blocked

The following are **automatically blocked**:

```bash
# File system destruction
rm -rf /
mkfs
dd if=/dev/zero of=/dev/sda

# System modification
chmod 777 /etc
chown root:root /

# Network attacks
DDoS commands
Port scanning
```

---

## Permission Levels

### Low Risk
- Open applications
- Search web
- Send notifications
- Take screenshots

### Medium Risk
- Read files
- Control volume
- IoT device control

### High Risk
- Write files
- Execute custom commands (sandboxed)

### Critical Risk ⚠️
- Delete files
- System modifications
- Security-critical IoT (locks, alarms)
- **Always requires user confirmation**

---

## Best Practices

### For Users

1. **Review permissions** before enabling new actions
2. **Use dry-run mode** for critical operations
3. **Keep sandbox enabled** in production
4. **Monitor audit logs** regularly
5. **Update regularly** for security patches

### For Developers

1. **Never disable sandbox** without explicit user consent
2. **Validate all inputs** with Pydantic models
3. **Use type hints** everywhere
4. **Write tests** for security-critical code
5. **Follow principle of least privilege**

---

## Reporting Vulnerabilities

### 🔒 Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Instead:

1. **Email:** security@ai-jarvis.dev (if available)
2. **Private disclosure:** Use GitHub Security Advisories
3. **Expected response:** Within 48 hours

### What to include:

- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information

---

## Security Updates

- **Critical:** Immediate patch release
- **High:** Within 7 days
- **Medium:** Next minor release
- **Low:** Planned release cycle

Subscribe to **GitHub Security Advisories** for notifications.

---

## Data Privacy

### Local-First Architecture

- All data processed locally by default
- No telemetry without consent
- Memory stored on-device
- No cloud dependency

### Optional Cloud Features

- Explicit opt-in required
- Data encrypted in transit (TLS)
- Data encrypted at rest
- User controls data deletion

---

## Compliance

- **GDPR**: Right to deletion, data portability
- **CCPA**: Data privacy controls
- **SOC 2**: (Enterprise version)

---

## Security Checklist

Before deploying:

- [ ] Changed default passwords
- [ ] Enabled sandbox mode
- [ ] Reviewed permission rules
- [ ] Configured firewall
- [ ] Enabled HTTPS
- [ ] Set up log monitoring
- [ ] Tested backup/restore
- [ ] Reviewed audit logs

---

## Contact

For security concerns: security@ai-jarvis.dev

For general questions: GitHub Discussions

---

**Last updated:** December 2025