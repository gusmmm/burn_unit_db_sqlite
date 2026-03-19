# Project Overview
- This is a full-stack medical database application for managing critical care burn patients in a specialized unit.
- Backend: FastAPI (located in backend/)
- Frontend: Streamlit (located in frontend/)
- Database: SQLite3 (located in database/)

## Environment & Tooling
- OS: Ubuntu 24.04 LTS
- Package Manager: Strictly use uv. Never suggest pip or poetry.
- Environment: Use .venv managed by uv.

### Commands:
- Install: uv sync
- Backend: uv run fastapi dev backend/main.py
- Frontend: uv run streamlit run frontend/app.py
- Tests: uv run pytest

## Critical Constraints
- Data Integrity: NEVER alter database contents or database/schema.sql without explicit project owner approval. All schema changes must be documented.
- File Isolation: All test files, dummy data, and mock databases must be stored strictly in the tests/ folder.
- Development Cycle: Implement small, modular changes. Test each component thoroughly before moving to the next feature.
- Security: Follow strict data privacy and clinical compliance regulations (GDPR/Medical data standards).

## Coding Standards
- Modular Approach: Break down functionality into small, manageable components.

## Documentation:
- Use comprehensive docstrings for all functions and classes (include parameters and return values).
- Maintain a clear README.md and a detailed CHANGELOG.md for all updates.
- Validation: Use Pydantic v2 for all data schemas and mapping.
- Language: Support European Portuguese (pt-PT) for clinical data extraction and UI strings.

## Project Structure
- backend/: FastAPI application logic.
- frontend/: Streamlit interface code.
- database/: Contains database.db and schema.sql.
- tests/: ALL test files, dummy data, and temporary databases.