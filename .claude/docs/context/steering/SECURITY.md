# Security Policy

## 🔐 Security Best Practices

### Environment Variables and Credentials

**NEVER commit credentials to version control!**

1. **Development Environment**
   - Use `.env.development` for local development (contains safe defaults)
   - These credentials should ONLY be used locally
   - Never use development credentials in production

2. **Production Environment**
   - Copy `.env.example` to `.env`
   - Replace ALL `CHANGE_ME` placeholders with secure values
   - Generate secure keys using: `openssl rand -hex 32`
   - Use strong, unique passwords for database
   - Store production credentials in a secure vault (e.g., AWS Secrets Manager, HashiCorp Vault)

3. **Git Safety**
   - `.env` files are gitignored and should NEVER be committed
   - Only `.env.example` and `.env.development` are safe to commit
   - Always review changes before committing to ensure no secrets are included

### Credential Generation

Generate secure keys for production:

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate SESSION_SECRET_KEY
openssl rand -hex 32

# Generate strong password
openssl rand -base64 32
```

### Docker Compose Security

- The `docker-compose.yml` file uses environment variables (no hardcoded values)
- Default values have been removed to force explicit configuration
- Always provide credentials via `.env` file or environment variables

### Checklist Before Deployment

- [ ] All `CHANGE_ME` values in `.env` have been replaced
- [ ] Strong, unique passwords are used for database
- [ ] Secure random keys generated for SECRET_KEY and SESSION_SECRET_KEY
- [ ] DEBUG is set to False in production
- [ ] CORS origins are properly configured
- [ ] HTTPS is configured for production
- [ ] Database backups are configured
- [ ] Monitoring and alerting are set up
- [ ] Rate limiting is configured
- [ ] Security headers are properly set

## 🚨 Reporting Security Vulnerabilities

If you discover a security vulnerability, please:

1. **DO NOT** create a public GitHub issue
2. Send details to the security team
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## 📋 Security Features

This application includes:

- Session-based authentication (not JWT)
- Password hashing with bcrypt
- CSRF protection
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic
- Secure headers configuration
- Role-based access control (RBAC)
- Multi-tenant data isolation

## 🔄 Regular Security Tasks

- Review and rotate credentials quarterly
- Update dependencies monthly
- Conduct security audits before major releases
- Monitor for suspicious activity
- Review access logs regularly