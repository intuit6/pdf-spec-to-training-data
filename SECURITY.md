# 安全政策

## Reporting a Vulnerability

We take the security of our project seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report

1. **Email**: Send an email to security@example.com (替换为你的安全邮箱)
   - Please include:
     - Description of the vulnerability
     - Steps to reproduce
     - Potential impact
     - Any suggestions for mitigation

2. **PGP**: If you prefer, you can use PGP encryption.
   - Our public key: (在此处添加你的 PGP 公钥)

3. **Response Time**: We aim to respond within 48 hours and provide a timeline for fixing.

4. **Disclosure**: We follow responsible disclosure:
   - Secret: Vulnerability details remain private
   - Coordinated: We work with reporter to fix before public disclosure
   - Timely: We aim to release a fix within 14 days

## Security Best Practices for Users

### 1. Keep Updated

Always use the latest stable version:

```bash
pip install --upgrade pdf-spec-to-training-data
```

### 2. Dependencies

We use standard, well-audited dependencies. However:

- Regularly update: `pip install -U`
- Review `requirements.txt` for any concerns
- Use dependency monitoring tools (dependabot)

### 3. File Handling

The project processes arbitrary PDF files. To minimize risk:

- **Only process trusted PDFs**: Untrusted PDFs may contain malicious content
- **Run in sandbox** (if processing untrusted files):
  ```bash
  python -m venv restricted_env
  # Or use Docker: docker run --rm -v $(pwd):/data python:3.11-slim
  ```
- **Limit permissions**: Don't run as root/admin

### 4. OCR Considerations

OCR functionality requires Tesseract or PaddleOCR:

- Tesseract runs locally, no data leaves your machine
- Ensure Tesseract is installed from official sources
- Regular updates: `apt upgrade tesseract-ocr` or `brew upgrade tesseract`

### 5. Data Privacy

- All processing happens locally by default
- No telemetry or data collection in the core library
- If you extend the code, be mindful not to send PDF content to external services

### 6. Input Validation

The code includes some basic validation:

- File type checking (PDF header)
- Size limits (configurable)
- Sanitization of extracted text

However, **always validate inputs yourself** if processing untrusted documents.

### 7. Supply Chain Security

We strive to provide a secure package:

- Minimal dependencies (only what's needed)
- Regular security updates via dependabot
- No dynamic code generation
- No eval() or exec() on user input

You can verify:

```bash
# Check package contents
pip download pdf-spec-to-training-data --no-deps
tar -tzf pdf_spec_to_training_data-*.tar.gz

# Check for known vulnerabilities
safety check  # requires `pip install safety`
```

### 8. Reporting Security Issues

If you discover a security issue:

1. **DO NOT** open a public GitHub issue
2. Email security@example.com with details
3. We'll acknowledge within 48 hours
4. We'll work with you to understand and fix the issue
5. We'll coordinate public disclosure timeline

### 9. Security Updates

Security fixes will be:

- Released as patch versions (x.y.Z)
- Announced in GitHub Security Advisories
- Backported to recent minor versions when possible
- Listed in CHANGELOG.md under "Security"

### 10. Known Issues

Currently known limitations:

- **No sandboxing**: Code runs with user's permissions
- **Memory usage**: Large PDFs can consume significant memory
- **Zip bombs**: Extremely large/complex PDFs may cause DoS
- **Arbitrary file write**: If you use custom output paths, ensure they're safe

## AdditionalSecurity Recommendations

### For Production Use

1. **Containerization**: Use Docker with minimal privileges
2. **Resource limits**: Set memory and CPU limits
3. **Input restrictions**: Only allow trusted sources
4. **Output scanning**: Scan extracted text for sensitive data
5. **Audit logging**: Log all processing activities

### For High-Security Environments

1. **Air-gapped deployment**: No internet access
2. **Code review**: Review all code before deployment
3. **Static analysis**: Run bandit, safety checks
4. **Dependency pinning**: Use exact versions in requirements.txt
5. **Regular updates**: Subscribe to security announcements

## Security Policy Updates

This security policy may be updated. Check this file for the latest version.

Last updated: 2025-03-23
