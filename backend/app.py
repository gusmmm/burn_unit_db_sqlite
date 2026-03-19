"""FastAPI application exposing read-only endpoints for burn unit tables."""

from pathlib import Path
import sqlite3
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

DATABASE_PATH = Path(__file__).resolve().parents[1] / "database" / "database.db"

app = FastAPI(
    title="Burn Unit Database API",
    version="0.1.0",
    description="API endpoints for burn unit reference and patient data.",
)


class PatientWrite(BaseModel):
    """Payload used for creating and replacing a patient row."""

    name: str
    birth_date: str | None = None
    gender: str | None = None
    address: int | None = None


class PatientRead(BaseModel):
    """Response model representing a patient row."""

    id: int
    name: str
    birth_date: str | None = None
    gender: str | None = None
    address: int | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection configured to expose rows as dictionaries."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def get_patient_or_404(connection: sqlite3.Connection, patient_id: int) -> dict[str, Any]:
    """Fetch a patient by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(row)


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


@app.post("/patients", tags=["patients"], response_model=PatientRead, status_code=201)
def create_patient(payload: PatientWrite) -> dict[str, Any]:
    """Create a new patient row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO patients (name, birth_date, gender, address)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.name,
                    payload.birth_date,
                    payload.gender,
                    payload.address,
                ),
            )
            patient_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM patients WHERE id = ?",
                (patient_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid patient data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Patient created but could not be read back")
    return dict(row)


@app.put("/patients/{patient_id}", tags=["patients"], response_model=PatientRead)
def update_patient(patient_id: int, payload: PatientWrite) -> dict[str, Any]:
    """Replace patient editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_patient_or_404(connection, patient_id)
            connection.execute(
                """
                UPDATE patients
                SET name = ?,
                    birth_date = ?,
                    gender = ?,
                    address = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.birth_date,
                    payload.gender,
                    payload.address,
                    patient_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM patients WHERE id = ?",
                (patient_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid patient data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Patient updated but could not be read back")
    return dict(row)


@app.delete("/patients/{patient_id}", tags=["patients"])
def delete_patient(patient_id: int) -> dict[str, str]:
    """Delete one patient by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_patient_or_404(connection, patient_id)
            connection.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete patient because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Patient {patient_id} deleted"}


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
