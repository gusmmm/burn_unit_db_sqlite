"""FastAPI application exposing read-only endpoints for burn unit tables."""

from pathlib import Path
import sqlite3
from typing import Any

from fastapi import FastAPI, HTTPException

DATABASE_PATH = Path(__file__).resolve().parents[1] / "database" / "database.db"

app = FastAPI(
    title="Burn Unit Database API",
    version="0.1.0",
    description="Read-only API endpoints for burn unit reference and patient data.",
)


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection configured to expose rows as dictionaries."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_all_rows(table_name: str) -> list[dict[str, Any]]:
    """Fetch all rows from the provided table name in ascending id order when available."""
    query = f"SELECT * FROM {table_name}"
    if table_name in {"patients", "addresses", "pathologies"}:
        query += " ORDER BY id"

    try:
        with get_connection() as connection:
            rows = connection.execute(query).fetchall()
    except sqlite3.OperationalError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not query table '{table_name}': {exc}",
        ) from exc

    return [dict(row) for row in rows]


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    """Return a small index of available endpoints."""
    return {
        "message": "Burn Unit Database API is running.",
        "endpoints": "/patients, /addresses, /pathologies, /patient-pathologies",
    }


@app.get("/patients", tags=["patients"])
def get_patients() -> list[dict[str, Any]]:
    """Return every patient row from the patients table."""
    return fetch_all_rows("patients")


@app.get("/addresses", tags=["addresses"])
def get_addresses() -> list[dict[str, Any]]:
    """Return every address row from the addresses table."""
    return fetch_all_rows("addresses")


@app.get("/pathologies", tags=["pathologies"])
def get_pathologies() -> list[dict[str, Any]]:
    """Return every pathology row from the pathologies table."""
    return fetch_all_rows("pathologies")


@app.get("/patient-pathologies", tags=["patient_pathologies"])
def get_patient_pathologies() -> list[dict[str, Any]]:
    """Return every row from the patient_pathologies join table."""
    return fetch_all_rows("patient_pathologies")
