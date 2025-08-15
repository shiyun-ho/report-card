# Docker Environment Management Learnings

## Session Context: Database Layer Implementation
**Phase**: 1.2 - Database Layer Setup  
**Task**: Implementing SQLAlchemy 2.0 models, migrations, and testing infrastructure  
**Key Challenge**: Consistent Docker environment management with secure credential handling

---

## 🐳 Critical Docker Patterns for Claude Code

### Pattern 1: Environment-First Development
```bash
# ✅ Always use .env files
docker compose up -d db
docker run --rm --env-file .env backend command

# ❌ Never expose credentials
docker run -e POSTGRES_PASSWORD=secret123 backend  # BAD
```

**For Claude Code**: Always check for and use existing `.env` files before running Docker commands. If credentials are needed, create/use environment files rather than inline environment variables.

### Pattern 2: Consistent Runtime Environment
**Decision Framework**:
- **Containerized app** → Use full Docker for development and testing
- **Mixed setup** → Be explicit about networking context (service names vs localhost)

**For Claude Code**: When a project uses Docker Compose, default to running all commands within the Docker environment rather than mixing host/container execution.

### Pattern 3: Clean Container Testing
```bash
# ✅ Clean, reproducible tests
docker run --rm --network project_network --env-file .env image command

# ❌ Volume mount conflicts with virtual environments
docker compose run backend command  # Can cause .venv conflicts
```

**For Claude Code**: For testing/validation commands, prefer temporary containers (`docker run --rm`) over volume-mounted service containers to avoid virtual environment conflicts.

---

## 🔒 Security Automation for Claude Code

### Credential Management Checklist
When implementing database/auth features:
1. ✅ Check for existing `.env.development` or `.env.example`
2. ✅ Create secure development defaults if missing
3. ✅ Use environment variables in all Docker commands
4. ✅ Never hardcode credentials in code or commands
5. ✅ Validate multi-tenant data isolation

### Environment File Strategy
```
.env.development    # Safe defaults for local development  
.env.example       # Template with CHANGE_ME placeholders
.env               # Active environment (gitignored)
```

**For Claude Code**: Always create both example and development environment files when setting up new projects.

---

## 🛠️ Development Workflow Automation

### Database Setup Pattern
```bash
# 1. Fresh database with correct credentials
docker compose down db && docker volume rm project_postgres_data
docker compose up -d db

# 2. Apply migrations in container
docker run --rm --env-file .env backend alembic upgrade head

# 3. Seed data in same environment  
docker run --rm --env-file .env backend python seed_script.py

# 4. Validate with tests
docker run --rm --env-file .env backend pytest
```

**For Claude Code**: Use this pattern when implementing database layers. Each step ensures environment consistency and security.

### Testing Validation Gates
When running PRP validation tests:
1. **Syntax/Format**: `ruff check --fix && ruff format`
2. **Type Check**: `mypy src/` (expect some warnings in development)
3. **Connection**: Test via Docker container, not host
4. **Migration**: Apply in clean container environment
5. **Seed Data**: Populate using environment variables
6. **Tests**: Run in containerized environment
7. **Verification**: Query database to confirm structure

---

## 🎯 Quick Reference for Claude Code

### When to Use Each Docker Approach
- **Service orchestration**: `docker compose up -d service`
- **One-off commands**: `docker run --rm --env-file .env image command`
- **Interactive debugging**: `docker compose exec service bash`
- **Clean testing**: `docker run --rm --network name --env-file .env`

### Environment Variable Best Practices
- **Development**: Use `.env.development` with safe, obvious fake credentials
- **Production**: Use `.env.example` as template, require real credential generation
- **Docker Compose**: Automatically loads `.env` file from project root
- **Security**: Mark development credentials as "INSECURE_DEV_ONLY"

### Common Pitfalls to Avoid
1. **Mixed environments**: Don't switch between host and container mid-task
2. **Credential exposure**: Don't put secrets in command history
3. **Volume conflicts**: Use `docker run --rm` for testing, not volume mounts
4. **Network confusion**: Use service names within Docker, localhost from host
5. **Permission issues**: Be consistent with user context (root vs appuser)

---

## 📋 Implementation Checklist

For any Docker-based development task:
- [ ] Check existing environment files (`.env*`)
- [ ] Use appropriate Docker networking (service names vs localhost)  
- [ ] Apply security-first credential management
- [ ] Use clean containers for validation/testing
- [ ] Maintain consistency within chosen approach
- [ ] Document any new environment variables needed
- [ ] Validate multi-tenant security if applicable

This approach ensures **production parity**, **security**, and **reproducible development environments** for all Docker-based development tasks.