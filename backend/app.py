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


class PatientCreate(BaseModel):
    """Payload used for creating a patient row with explicit id."""

    id: int
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


class PatientPatch(BaseModel):
    """Payload used for partial updates of a patient row."""

    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    address: int | None = None


class PathologyCreate(BaseModel):
    """Payload used for creating a pathology row."""

    id: int
    name: str
    fsn: str | None = None
    semantic_tag: str | None = None
    definition: str | None = None
    icd11_code: str | None = None
    mesh_id: str | None = None
    status: str | None = "Active"


class PathologyWrite(BaseModel):
    """Payload used for replacing editable pathology fields."""

    name: str
    fsn: str | None = None
    semantic_tag: str | None = None
    definition: str | None = None
    icd11_code: str | None = None
    mesh_id: str | None = None
    status: str | None = "Active"


class PathologyPatch(BaseModel):
    """Payload used for partially updating pathology fields."""

    name: str | None = None
    fsn: str | None = None
    semantic_tag: str | None = None
    definition: str | None = None
    icd11_code: str | None = None
    mesh_id: str | None = None
    status: str | None = None


class PathologyRead(BaseModel):
    """Response model representing a pathology row."""

    id: int
    name: str
    fsn: str | None = None
    semantic_tag: str | None = None
    definition: str | None = None
    icd11_code: str | None = None
    mesh_id: str | None = None
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PatientPathologyCreate(BaseModel):
    """Payload used for creating a patient-pathology association row."""

    patient_id: int
    pathology_id: int
    diagnosed_date: str | None = None
    severity: str | None = None


class PatientPathologyPatch(BaseModel):
    """Payload used for partially updating an association row."""

    patient_id: int | None = None
    pathology_id: int | None = None
    diagnosed_date: str | None = None
    severity: str | None = None


class PatientPathologyRead(BaseModel):
    """Response model representing a patient-pathology association row."""

    patient_id: int
    pathology_id: int
    diagnosed_date: str | None = None
    severity: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MedicationCreate(BaseModel):
    """Payload used for creating a medication row."""

    name: str
    atc_code: str | None = None
    description: str | None = None


class MedicationWrite(BaseModel):
    """Payload used for replacing editable medication fields."""

    name: str
    atc_code: str | None = None
    description: str | None = None


class MedicationPatch(BaseModel):
    """Payload used for partially updating medication fields."""

    name: str | None = None
    atc_code: str | None = None
    description: str | None = None


class MedicationRead(BaseModel):
    """Response model representing a medication row."""

    id: int
    name: str
    atc_code: str | None = None
    description: str | None = None
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


def get_pathology_or_404(connection: sqlite3.Connection, pathology_id: int) -> dict[str, Any]:
    """Fetch a pathology by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM pathologies WHERE id = ?",
        (pathology_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Pathology not found")
    return dict(row)


def get_pathologies_by_field_or_404(
    connection: sqlite3.Connection,
    field: str,
    value: str,
) -> list[dict[str, Any]]:
    """Fetch pathologies by icd11_code or mesh_id, raising 404 when there are no matches."""
    if field not in {"icd11_code", "mesh_id"}:
        raise HTTPException(status_code=400, detail="Invalid lookup field")

    rows = connection.execute(
        f"SELECT * FROM pathologies WHERE {field} = ? ORDER BY id",
        (value,),
    ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No pathologies found for {field}='{value}'")
    return [dict(row) for row in rows]


def get_patient_pathology_or_404(
    connection: sqlite3.Connection,
    patient_id: int,
    pathology_id: int,
) -> dict[str, Any]:
    """Fetch an association row by composite key or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT *
        FROM patient_pathologies
        WHERE patient_id = ? AND pathology_id = ?
        """,
        (patient_id, pathology_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Association not found")
    return dict(row)


def get_medication_or_404(connection: sqlite3.Connection, medication_id: int) -> dict[str, Any]:
    """Fetch a medication by id or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT id,
               name,
               ATC_code AS atc_code,
               description,
               created_at,
               updated_at
        FROM medications
        WHERE id = ?
        """,
        (medication_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return dict(row)


def fetch_all_rows(table_name: str) -> list[dict[str, Any]]:
    """Fetch all rows from the provided table name in ascending id order when available."""
    query = f"SELECT * FROM {table_name}"
    if table_name in {"patients", "addresses", "pathologies", "medications"}:
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
        "endpoints": "/patients, /addresses, /pathologies, /patient-pathologies, /medications",
    }


@app.get("/patients", tags=["patients"])
def get_patients() -> list[dict[str, Any]]:
    """Return every patient row from the patients table."""
    return fetch_all_rows("patients")


@app.get("/patients/{patient_id}", tags=["patients"], response_model=PatientRead)
def get_patient(patient_id: int) -> dict[str, Any]:
    """Return one patient row by id."""
    with get_connection() as connection:
        return get_patient_or_404(connection, patient_id)


@app.post("/patients", tags=["patients"], response_model=PatientRead, status_code=201)
def create_patient(payload: PatientCreate) -> dict[str, Any]:
    """Create a new patient row and return the inserted record."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO patients (id, name, birth_date, gender, address)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload.id,
                    payload.name,
                    payload.birth_date,
                    payload.gender,
                    payload.address,
                ),
            )
            row = connection.execute(
                "SELECT * FROM patients WHERE id = ?",
                (payload.id,),
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


@app.patch("/patients/{patient_id}", tags=["patients"], response_model=PatientRead)
def patch_patient(patient_id: int, payload: PatientPatch) -> dict[str, Any]:
    """Partially update patient fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"name", "birth_date", "gender", "address"}
    assignments: list[str] = []
    values: list[Any] = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        assignments.append(f"{field} = ?")
        values.append(value)

    if not assignments:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    assignments.append("updated_at = CURRENT_TIMESTAMP")
    values.append(patient_id)

    query = f"UPDATE patients SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_patient_or_404(connection, patient_id)
            connection.execute(query, values)
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


@app.get("/pathologies/{pathology_id}", tags=["pathologies"], response_model=PathologyRead)
def get_pathology(pathology_id: int) -> dict[str, Any]:
    """Return one pathology row by id."""
    with get_connection() as connection:
        return get_pathology_or_404(connection, pathology_id)


@app.get("/pathologies/icd11/{icd11_code}", tags=["pathologies"], response_model=list[PathologyRead])
def get_pathology_by_icd11_code(icd11_code: str) -> list[dict[str, Any]]:
    """Return pathology rows matching an ICD-11 code."""
    with get_connection() as connection:
        return get_pathologies_by_field_or_404(connection, "icd11_code", icd11_code)


@app.get("/pathologies/mesh/{mesh_id}", tags=["pathologies"], response_model=list[PathologyRead])
def get_pathology_by_mesh_id(mesh_id: str) -> list[dict[str, Any]]:
    """Return pathology rows matching a MeSH id."""
    with get_connection() as connection:
        return get_pathologies_by_field_or_404(connection, "mesh_id", mesh_id)


@app.post("/pathologies", tags=["pathologies"], response_model=PathologyRead, status_code=201)
def create_pathology(payload: PathologyCreate) -> dict[str, Any]:
    """Create a new pathology row and return the inserted record."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO pathologies (id, name, fsn, semantic_tag, definition, icd11_code, mesh_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.id,
                    payload.name,
                    payload.fsn,
                    payload.semantic_tag,
                    payload.definition,
                    payload.icd11_code,
                    payload.mesh_id,
                    payload.status,
                ),
            )
            row = connection.execute(
                "SELECT * FROM pathologies WHERE id = ?",
                (payload.id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid pathology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Pathology created but could not be read back")
    return dict(row)


@app.put("/pathologies/{pathology_id}", tags=["pathologies"], response_model=PathologyRead)
def update_pathology(pathology_id: int, payload: PathologyWrite) -> dict[str, Any]:
    """Replace pathology editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_pathology_or_404(connection, pathology_id)
            connection.execute(
                """
                UPDATE pathologies
                SET name = ?,
                    fsn = ?,
                    semantic_tag = ?,
                    definition = ?,
                    icd11_code = ?,
                    mesh_id = ?,
                    status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.fsn,
                    payload.semantic_tag,
                    payload.definition,
                    payload.icd11_code,
                    payload.mesh_id,
                    payload.status,
                    pathology_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM pathologies WHERE id = ?",
                (pathology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid pathology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Pathology updated but could not be read back")
    return dict(row)


@app.patch("/pathologies/{pathology_id}", tags=["pathologies"], response_model=PathologyRead)
def patch_pathology(pathology_id: int, payload: PathologyPatch) -> dict[str, Any]:
    """Partially update pathology fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"name", "fsn", "semantic_tag", "definition", "icd11_code", "mesh_id", "status"}
    assignments: list[str] = []
    values: list[Any] = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        assignments.append(f"{field} = ?")
        values.append(value)

    if not assignments:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    assignments.append("updated_at = CURRENT_TIMESTAMP")
    values.append(pathology_id)

    query = f"UPDATE pathologies SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_pathology_or_404(connection, pathology_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM pathologies WHERE id = ?",
                (pathology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid pathology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Pathology updated but could not be read back")
    return dict(row)


@app.delete("/pathologies/{pathology_id}", tags=["pathologies"])
def delete_pathology(pathology_id: int) -> dict[str, str]:
    """Delete one pathology by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_pathology_or_404(connection, pathology_id)
            connection.execute("DELETE FROM pathologies WHERE id = ?", (pathology_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete pathology because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Pathology {pathology_id} deleted"}


@app.get("/medications", tags=["medications"])
def get_medications() -> list[dict[str, Any]]:
    """Return every medication row from the medications table."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id,
                   name,
                   ATC_code AS atc_code,
                   description,
                   created_at,
                   updated_at
            FROM medications
            ORDER BY id
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/medications/{medication_id}", tags=["medications"], response_model=MedicationRead)
def get_medication(medication_id: int) -> dict[str, Any]:
    """Return one medication row by id."""
    with get_connection() as connection:
        return get_medication_or_404(connection, medication_id)


@app.post("/medications", tags=["medications"], response_model=MedicationRead, status_code=201)
def create_medication(payload: MedicationCreate) -> dict[str, Any]:
    """Create a new medication row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO medications (name, ATC_code, description)
                VALUES (?, ?, ?)
                """,
                (
                    payload.name,
                    payload.atc_code,
                    payload.description,
                ),
            )
            medication_id = cursor.lastrowid
            row = connection.execute(
                """
                SELECT id,
                       name,
                       ATC_code AS atc_code,
                       description,
                       created_at,
                       updated_at
                FROM medications
                WHERE id = ?
                """,
                (medication_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid medication data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Medication created but could not be read back")
    return dict(row)


@app.put("/medications/{medication_id}", tags=["medications"], response_model=MedicationRead)
def update_medication(medication_id: int, payload: MedicationWrite) -> dict[str, Any]:
    """Replace medication editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_medication_or_404(connection, medication_id)
            connection.execute(
                """
                UPDATE medications
                SET name = ?,
                    ATC_code = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.atc_code,
                    payload.description,
                    medication_id,
                ),
            )
            row = connection.execute(
                """
                SELECT id,
                       name,
                       ATC_code AS atc_code,
                       description,
                       created_at,
                       updated_at
                FROM medications
                WHERE id = ?
                """,
                (medication_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid medication data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Medication updated but could not be read back")
    return dict(row)


@app.patch("/medications/{medication_id}", tags=["medications"], response_model=MedicationRead)
def patch_medication(medication_id: int, payload: MedicationPatch) -> dict[str, Any]:
    """Partially update medication fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"name", "atc_code", "description"}
    assignments: list[str] = []
    values: list[Any] = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        column_name = "ATC_code" if field == "atc_code" else field
        assignments.append(f"{column_name} = ?")
        values.append(value)

    if not assignments:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    assignments.append("updated_at = CURRENT_TIMESTAMP")
    values.append(medication_id)

    query = f"UPDATE medications SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_medication_or_404(connection, medication_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT id,
                       name,
                       ATC_code AS atc_code,
                       description,
                       created_at,
                       updated_at
                FROM medications
                WHERE id = ?
                """,
                (medication_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid medication data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Medication updated but could not be read back")
    return dict(row)


@app.delete("/medications/{medication_id}", tags=["medications"])
def delete_medication(medication_id: int) -> dict[str, str]:
    """Delete one medication by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_medication_or_404(connection, medication_id)
            connection.execute("DELETE FROM medications WHERE id = ?", (medication_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete medication because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Medication {medication_id} deleted"}


@app.get("/patient-pathologies", tags=["patient_pathologies"])
def get_patient_pathologies() -> list[dict[str, Any]]:
    """Return every row from the patient_pathologies join table."""
    return fetch_all_rows("patient_pathologies")


@app.post(
    "/patient-pathologies",
    tags=["patient_pathologies"],
    response_model=PatientPathologyRead,
    status_code=201,
)
def create_patient_pathology_association(payload: PatientPathologyCreate) -> dict[str, Any]:
    """Create a patient-pathology association and return the inserted row."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO patient_pathologies (patient_id, pathology_id, diagnosed_date, severity)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.patient_id,
                    payload.pathology_id,
                    payload.diagnosed_date,
                    payload.severity,
                ),
            )
            row = connection.execute(
                """
                SELECT *
                FROM patient_pathologies
                WHERE patient_id = ? AND pathology_id = ?
                """,
                (payload.patient_id, payload.pathology_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid association data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association created but could not be read back")
    return dict(row)


@app.patch(
    "/patient-pathologies/{patient_id}/{pathology_id}",
    tags=["patient_pathologies"],
    response_model=PatientPathologyRead,
)
def patch_patient_pathology_association(
    patient_id: int,
    pathology_id: int,
    payload: PatientPathologyPatch,
) -> dict[str, Any]:
    """Partially update an association row by composite key and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"patient_id", "pathology_id", "diagnosed_date", "severity"}
    assignments: list[str] = []
    values: list[Any] = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        assignments.append(f"{field} = ?")
        values.append(value)

    if not assignments:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    values.extend([patient_id, pathology_id])
    query = (
        f"UPDATE patient_pathologies SET {', '.join(assignments)} "
        "WHERE patient_id = ? AND pathology_id = ?"
    )

    new_patient_id = updates.get("patient_id", patient_id)
    new_pathology_id = updates.get("pathology_id", pathology_id)

    try:
        with get_connection() as connection:
            get_patient_pathology_or_404(connection, patient_id, pathology_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT *
                FROM patient_pathologies
                WHERE patient_id = ? AND pathology_id = ?
                """,
                (new_patient_id, new_pathology_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid association data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association updated but could not be read back")
    return dict(row)


@app.delete("/patient-pathologies/{patient_id}/{pathology_id}", tags=["patient_pathologies"])
def delete_patient_pathology_association(patient_id: int, pathology_id: int) -> dict[str, str]:
    """Delete one association row by composite key."""
    with get_connection() as connection:
        get_patient_pathology_or_404(connection, patient_id, pathology_id)
        connection.execute(
            "DELETE FROM patient_pathologies WHERE patient_id = ? AND pathology_id = ?",
            (patient_id, pathology_id),
        )

    return {"message": f"Association ({patient_id}, {pathology_id}) deleted"}
