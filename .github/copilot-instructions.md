# Project Overview
- This project is a full-stack web application for managing a personal medical database.
- The database will store information about critical care burn patients admited in a burn unit.

## IMPORTANT instructions
- NEVER alter the database contents or schema without explicit instructions from the project owner. Any changes to the database must be approved and documented to ensure data integrity and consistency.
- Always follow best practices for security, data privacy, and compliance with relevant regulations.
- Keep the codebase clean and maintainable. Use consistent coding standards and practices throughout the project.
- Use a modular approach to development, breaking down the application into smaller, manageable components.
- Before implementing new features or enhancements, consult with the project owner and document the changes thoroughly. Make small changes each time and test them to ensure they work as expected without introducing bugs or issues.
- All test files and dummy data files and database files must be stored in the `tests/` folder. Do not store any test files or dummy data files or database files outside of the `tests/` folder.

## Technologies Used
- The database is a sqlite3 database. The database and schema are in the folder `database/`. The database is called `database.db`. The schema is in the file `schema.sql`.
- The backend is built using the `FastAPI` framework. The backend code is in the folder `backend/`.
- The frontend is built using `streamlit`. The frontend code is in the folder `frontend/`.

## Environment & Tooling
- **OS**: Always assume Ubuntu 24.04 LTS.
- **Package Management**: Strictly use `uv`. Never suggest `pip` or `poetry`.
- **Environment**: Use `.venv` managed by `uv`.

## Documentation
- All code must be well-documented with clear comments explaining the purpose and functionality of each component.
- Use docstrings for all functions and classes to provide detailed explanations of their behavior, parameters, and return values.
- Maintain a comprehensive README file that provides an overview of the project, setup instructions, and usage guidelines.
- Document any changes to the database schema or application features in a changelog file to keep track of modifications and updates.