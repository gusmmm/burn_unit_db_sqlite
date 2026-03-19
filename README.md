# burn_unit_db_sqlite

Create your personal database for a critical care burn unit (SQLite version).

## Requirements

- Ubuntu 24.04 LTS (project assumption)
- `uv` installed
- Python 3.12+

## Install dependencies

From project root:

```bash
uv sync
```

## Run backend (FastAPI)

Default (host `127.0.0.1`, port `8000`):

```bash
uv run main.py --mode backend
```

Choose host/port:

```bash
uv run main.py --mode backend --host 127.0.0.1 --port 8000
```

API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Run frontend (Streamlit)

Default frontend port `8501`, calling backend at `http://127.0.0.1:8000`:

```bash
uv run main.py --mode frontend
```

Choose frontend port and backend URL:

```bash
uv run main.py --mode frontend --port 8504 --api-url http://127.0.0.1:8000
```

Open in browser:

- `http://127.0.0.1:8501` (or your selected frontend port)

## Typical workflow

1. Start backend:

```bash
uv run main.py --mode backend --port 8000
```

2. In another terminal, start frontend:

```bash
uv run main.py --mode frontend --port 8501 --api-url http://127.0.0.1:8000
```

## Launcher help

```bash
uv run main.py --help
```
