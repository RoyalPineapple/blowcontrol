# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Dyson2MQTT, please send an email to alex@squareup.com. All security vulnerabilities will be promptly addressed.

### What to include in your report:

- **Description**: A clear description of the vulnerability
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Impact**: What could happen if this vulnerability is exploited
- **Suggested fix**: If you have any suggestions for fixing the issue

### Response timeline:

- **Initial response**: Within 48 hours
- **Status update**: Within 1 week
- **Fix timeline**: Depends on severity, typically 1-4 weeks

### Security considerations:

- This project interacts with MQTT devices and may handle sensitive network credentials
- Always use environment variables for storing sensitive configuration
- Never commit `.env` files or hardcoded credentials
- Keep your MQTT credentials secure and rotate them regularly

## Best Practices

1. **Environment Variables**: Always use `.env` files for sensitive configuration
2. **Network Security**: Use secure MQTT connections when possible
3. **Credential Management**: Rotate MQTT passwords regularly
4. **Access Control**: Limit network access to your Dyson devices
5. **Updates**: Keep the software updated to the latest version 