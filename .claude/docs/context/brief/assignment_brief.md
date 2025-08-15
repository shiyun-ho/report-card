Take-Home Assignment July 2025

1. Scenario (Teacher Report Card Assistant)
A mid-sized school group (3 schools, ~120 teachers) wants a one‑stop tool for teachers to prepare term report cards: review a student’s recent performance/notes and generate a concise briefing they can share or print.

2. Task Overview
The system must let a teacher:
    1. Review a student’s recent performance, notes, and achievements gathered from multiple sources.
    2. Record grades for core subjects (Math, English, Science, etc.), behavior comments, and an overall performance band.
    3. Auto‑suggest achievements (pulled from a shared achievements DB) and allow quick inclusion/exclusion.
    4. Generate & export a professional, printable report card for the selected term.
2 pages:
    • Dashboard to see all students and overall states
    • Report generation page
Use mock data only. No live AI calls are required.
Stack requirements:
    • Backend API
    • Frontend UI
    • PostgreSQL database
    • Docker Compose to run it all
Languages: Python, JavaScript/TypeScript, or a mix.
Multi-teacher: Can support multiple users.
Multi‑School: Different schools share the same system
Multi‑Role:
    • Teachers can only see students they teach. 
    • Head teachers can see all students.

3. What We’re Looking for
    • Thoughtful AI-assisted development workflow
        ◦ It’s fine if 100% of your code is AI-generated, just show that you understand, curated, and validated what was written. 
        ◦ We care about thoughtful prompt use, pruning AI artifacts, and clear reasoning.
    • Code security: 
        ◦ RBAC, input validation, safe SQL, CSRF protection etc.
    • Testing
        ◦ Unit tests, Integration Tests
    • No “weird AI junk”
        ◦ No leftover files or unused code from AI scaffolds.
        ◦ No overly complex abstractions without purpose.
        ◦ Show you understand what’s there.
    • Ensuring edge cases are handled
        ◦ Will test some edge cases on both frontend and API-side e.g. student doesn’t exist or date range doesn’t exist

4. Rules & Constraints
    • AI tools (ChatGPT, Copilot, Cursor, Claude Code etc.) are highly encouraged during development. 
    • Do not include any real secrets, API keys, or tokens.
    • Seed your mock database with realistic sample data for 2–3 students.

5. Deliverables
    1. Source Code via public repository access or zip file (frontend, backend, db).
        ◦ Should include a README.md with:
            ▪ Setup/run instructions (preferably just `docker-compose up`)
            ▪ Stack overview & key decisions
            ▪ Code security
            ▪ DB Schemas
            ▪ API contract
            ▪ How to run tests
    2. Also,  include a comprehensive document of how you leveraged AI tools during development.
        ◦ Walk us through your workflow.
        ◦ Show us what prompts you use explain why you used them.
        ◦ Reflect on what worked well and what didn’t.

