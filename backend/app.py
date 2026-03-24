"""FastAPI application exposing read-only endpoints for burn unit tables."""

from pathlib import Path
import sqlite3
from typing import Any
from datetime import date

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


class AntibioticCreate(BaseModel):
    """Payload used for creating an antibiotic row."""

    name: str
    atc_code: str
    description: str | None = None


class AntibioticWrite(BaseModel):
    """Payload used for replacing editable antibiotic fields."""

    name: str
    atc_code: str
    description: str | None = None


class AntibioticPatch(BaseModel):
    """Payload used for partially updating antibiotic fields."""

    name: str | None = None
    atc_code: str | None = None
    description: str | None = None


class AntibioticRead(BaseModel):
    """Response model representing an antibiotic row."""

    id: int
    name: str
    atc_code: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProvenanceDestinationCreate(BaseModel):
    """Payload used for creating a provenance/destination row."""

    name: str
    type: str | None = None
    location: int | None = None


class ProvenanceDestinationWrite(BaseModel):
    """Payload used for replacing editable provenance/destination fields."""

    name: str
    type: str | None = None
    location: int | None = None


class ProvenanceDestinationPatch(BaseModel):
    """Payload used for partially updating provenance/destination fields."""

    name: str | None = None
    type: str | None = None
    location: int | None = None


class ProvenanceDestinationRead(BaseModel):
    """Response model representing a provenance/destination row."""

    id: int
    name: str
    type: str | None = None
    location: int | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BurnEtiologyCreate(BaseModel):
    """Payload used for creating a burn etiology row."""

    name: str
    description: str | None = None


class BurnEtiologyWrite(BaseModel):
    """Payload used for replacing editable burn etiology fields."""

    name: str
    description: str | None = None


class BurnEtiologyPatch(BaseModel):
    """Payload used for partially updating burn etiology fields."""

    name: str | None = None
    description: str | None = None


class BurnEtiologyRead(BaseModel):
    """Response model representing a burn etiology row."""

    id: int
    name: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BurnUnitCaseCreate(BaseModel):
    """Payload used for creating a burn unit case row."""

    id: int
    patient_id: int
    TBSA_burned: float | None = None
    admission_date: str | None = None
    burn_date: str | None = None
    release_date: str | None = None
    admission_provenance: int | None = None
    release_destination: int | None = None
    burn_mecanism: str | None = None
    burn_etiology: int | None = None
    violence_related: bool | None = None
    suicide_attempt: bool | None = None
    accident_type: str | None = None
    wildfire: bool | None = None
    bonfire_fogueira: bool | None = None
    fireplace_lareira: bool | None = None
    note: str | None = None
    special_forces: str | None = None


class BurnUnitCaseWrite(BaseModel):
    """Payload used for replacing editable burn unit case fields."""

    patient_id: int
    TBSA_burned: float | None = None
    admission_date: str | None = None
    burn_date: str | None = None
    release_date: str | None = None
    admission_provenance: int | None = None
    release_destination: int | None = None
    burn_mecanism: str | None = None
    burn_etiology: int | None = None
    violence_related: bool | None = None
    suicide_attempt: bool | None = None
    accident_type: str | None = None
    wildfire: bool | None = None
    bonfire_fogueira: bool | None = None
    fireplace_lareira: bool | None = None
    note: str | None = None
    special_forces: str | None = None


class BurnUnitCasePatch(BaseModel):
    """Payload used for partially updating burn unit case fields."""

    patient_id: int | None = None
    TBSA_burned: float | None = None
    admission_date: str | None = None
    burn_date: str | None = None
    release_date: str | None = None
    admission_provenance: int | None = None
    release_destination: int | None = None
    burn_mecanism: str | None = None
    burn_etiology: int | None = None
    violence_related: bool | None = None
    suicide_attempt: bool | None = None
    accident_type: str | None = None
    wildfire: bool | None = None
    bonfire_fogueira: bool | None = None
    fireplace_lareira: bool | None = None
    note: str | None = None
    special_forces: str | None = None


class BurnUnitCaseRead(BaseModel):
    """Response model representing a burn unit case row."""

    id: int
    patient_id: int
    TBSA_burned: float | None = None
    admission_date: str | None = None
    burn_date: str | None = None
    release_date: str | None = None
    admission_provenance: int | None = None
    release_destination: int | None = None
    burn_mecanism: str | None = None
    burn_etiology: int | None = None
    violence_related: bool | None = None
    suicide_attempt: bool | None = None
    accident_type: str | None = None
    wildfire: bool | None = None
    bonfire_fogueira: bool | None = None
    fireplace_lareira: bool | None = None
    note: str | None = None
    special_forces: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CaseBurnsCreate(BaseModel):
    """Payload used for creating a case_burns association row."""

    case_id: int
    burn_depth_id: int
    anatomic_location_id: int
    note: str | None = None


class CaseBurnsPatch(BaseModel):
    """Payload used for partially updating a case_burns association row."""

    case_id: int | None = None
    burn_depth_id: int | None = None
    anatomic_location_id: int | None = None
    note: str | None = None


class CaseBurnsRead(BaseModel):
    """Response model representing a case_burns association row."""

    case_id: int
    burn_depth_id: int
    anatomic_location_id: int
    note: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CaseInfectionCreate(BaseModel):
    """Payload used for creating a case_infections association row."""

    case_id: int
    infection_id: int
    date_of_infection: str | None = None
    note: str | None = None


class CaseInfectionPatch(BaseModel):
    """Payload used for partially updating a case_infections association row."""

    case_id: int | None = None
    infection_id: int | None = None
    date_of_infection: str | None = None
    note: str | None = None


class CaseInfectionRead(BaseModel):
    """Response model representing a case_infections association row."""

    case_id: int
    infection_id: int
    date_of_infection: str | None = None
    note: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CaseAntibioticCreate(BaseModel):
    """Payload used for creating a case_antibiotics association row."""

    case_id: int
    antibiotic_id: int
    indication: int | None = None
    date_started: str | None = None
    date_stopped: str | None = None
    note: str | None = None


class CaseAntibioticPatch(BaseModel):
    """Payload used for partially updating a case_antibiotics association row."""

    case_id: int | None = None
    antibiotic_id: int | None = None
    indication: int | None = None
    date_started: str | None = None
    date_stopped: str | None = None
    note: str | None = None


class CaseAntibioticRead(BaseModel):
    """Response model representing a case_antibiotics association row."""

    case_id: int
    antibiotic_id: int
    indication: int | None = None
    date_started: str | None = None
    date_stopped: str | None = None
    note: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CaseAssociatedInjuryCreate(BaseModel):
    """Payload used for creating a case_associated_injuries association row."""

    case_id: int
    injury_id: int
    date_of_injury: date | None = None
    note: str | None = None


class CaseAssociatedInjuryPatch(BaseModel):
    """Payload used for partially updating a case_associated_injuries association row."""

    date_of_injury: date | None = None
    note: str | None = None


class CaseAssociatedInjuryRead(BaseModel):
    """Response model representing a case_associated_injuries association row."""

    case_id: int
    injury_id: int
    date_of_injury: date | None = None
    note: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)



class PatientMedicationCreate(BaseModel):
    """Payload used for creating a patient-medication association row."""

    patient_id: int
    medication_id: int
    prescribed_date: str | None = None
    dosage: str | None = None


class PatientMedicationPatch(BaseModel):
    """Payload used for partially updating a patient-medication association row."""

    patient_id: int | None = None
    medication_id: int | None = None
    prescribed_date: str | None = None
    dosage: str | None = None


class PatientMedicationRead(BaseModel):
    """Response model representing a patient-medication association row."""

    patient_id: int
    medication_id: int
    prescribed_date: str | None = None
    dosage: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InfectionCreate(BaseModel):
    """Payload used for creating an infection row with explicit id."""
    
    id: int
    name: str
    description: str | None = None


class InfectionWrite(BaseModel):
    """Payload used for replacing editable infection fields."""

    name: str
    description: str | None = None


class InfectionPatch(BaseModel):
    """Payload used for partially updating infection fields."""

    name: str | None = None
    description: str | None = None


class InfectionRead(BaseModel):
    """Response model representing an infection row."""

    id: int
    name: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MicrobiologySpecimenCreate(BaseModel):
    """Payload used for creating a microbiology specimen row."""

    loinc_code: str
    specimen_type: str
    note: str | None = None


class MicrobiologySpecimenWrite(BaseModel):
    """Payload used for replacing editable microbiology specimen fields."""

    loinc_code: str
    specimen_type: str
    note: str | None = None


class MicrobiologySpecimenPatch(BaseModel):
    """Payload used for partially updating microbiology specimen fields."""

    loinc_code: str | None = None
    specimen_type: str | None = None
    note: str | None = None


class MicrobiologySpecimenRead(BaseModel):
    """Response model representing a microbiology_specimens row."""

    id: int
    loinc_code: str
    specimen_type: str
    note: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MicrobiologyAgentCreate(BaseModel):
    """Payload used for creating a microbiology agent row."""

    snomed_ct_code: str
    name: str
    description: str | None = None


class MicrobiologyAgentWrite(BaseModel):
    """Payload used for replacing editable microbiology agent fields."""

    snomed_ct_code: str
    name: str
    description: str | None = None


class MicrobiologyAgentPatch(BaseModel):
    """Payload used for partially updating microbiology agent fields."""

    snomed_ct_code: str | None = None
    name: str | None = None
    description: str | None = None


class MicrobiologyAgentRead(BaseModel):
    """Response model representing a microbiology_agents row."""

    id: int
    snomed_ct_code: str
    name: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CaseMicrobiologyCreate(BaseModel):
    """Payload used for creating a case_microbiology row."""

    case_id: int
    specimen_id: int
    microorganism_id: int
    hospital_test_id: str | None = None
    date_of_collection: str | None = None
    date_of_reporting: str | None = None
    note: str | None = None


class CaseMicrobiologyWrite(BaseModel):
    """Payload used for replacing editable case_microbiology fields."""

    case_id: int
    specimen_id: int
    microorganism_id: int
    hospital_test_id: str | None = None
    date_of_collection: str | None = None
    date_of_reporting: str | None = None
    note: str | None = None


class CaseMicrobiologyPatch(BaseModel):
    """Payload used for partially updating case_microbiology fields."""

    case_id: int | None = None
    specimen_id: int | None = None
    microorganism_id: int | None = None
    hospital_test_id: str | None = None
    date_of_collection: str | None = None
    date_of_reporting: str | None = None
    note: str | None = None


class CaseMicrobiologyRead(BaseModel):
    """Response model representing a case_microbiology row."""

    id: int
    case_id: int
    specimen_id: int
    microorganism_id: int
    hospital_test_id: str | None = None
    date_of_collection: str | None = None
    date_of_reporting: str | None = None
    note: str | None = None
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


def get_antibiotic_or_404(connection: sqlite3.Connection, antibiotic_id: int) -> dict[str, Any]:
    """Fetch an antibiotic by id or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT id,
               name,
               atc_code,
               description,
               created_at,
               updated_at
        FROM antibiotics
        WHERE id = ?
        """,
        (antibiotic_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Antibiotic not found")
    return dict(row)


def get_patient_medication_or_404(
    connection: sqlite3.Connection,
    patient_id: int,
    medication_id: int,
) -> dict[str, Any]:
    """Fetch a patient-medication association row by composite key or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT *
        FROM patient_medications
        WHERE patient_id = ? AND medication_id = ?
        """,
        (patient_id, medication_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Patient-medication association not found")
    return dict(row)


def get_provenance_destination_or_404(
    connection: sqlite3.Connection,
    provenance_destination_id: int,
) -> dict[str, Any]:
    """Fetch a provenance/destination row by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM provenance_destination WHERE id = ?",
        (provenance_destination_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Provenance/destination not found")
    return dict(row)


def get_burn_etiology_or_404(connection: sqlite3.Connection, burn_etiology_id: int) -> dict[str, Any]:
    """Fetch a burn etiology row by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM burn_etiology WHERE id = ?",
        (burn_etiology_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Burn etiology not found")
    return dict(row)


def get_burn_unit_case_or_404(connection: sqlite3.Connection, burn_unit_case_id: int) -> dict[str, Any]:
    """Fetch a burn unit case row by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM burn_unit_cases WHERE id = ?",
        (burn_unit_case_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Burn unit case not found")
    return dict(row)



def get_case_burns_or_404(
    connection: sqlite3.Connection,
    case_id: int,
    burn_depth_id: int,
    anatomic_location_id: int,
) -> dict[str, Any]:
    """Fetch a case_burns association row by composite key or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT *
        FROM case_burns
        WHERE case_id = ? AND burn_depth_id = ? AND anatomic_location_id = ?
        """,
        (case_id, burn_depth_id, anatomic_location_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Case burn association not found")
    return dict(row)


def get_case_infection_or_404(
    connection: sqlite3.Connection,
    case_id: int,
    infection_id: int,
) -> dict[str, Any]:
    """Fetch a case_infections association row by composite key or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT *
        FROM case_infections
        WHERE case_id = ? AND infection_id = ?
        """,
        (case_id, infection_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Case infection association not found")
    return dict(row)


def get_case_antibiotic_or_404(
    connection: sqlite3.Connection,
    case_id: int,
    antibiotic_id: int,
) -> dict[str, Any]:
    """Fetch a case_antibiotics association row by composite key or raise 404 if not found."""
    row = connection.execute(
        """
        SELECT *
        FROM case_antibiotics
        WHERE case_id = ? AND antibiotic_id = ?
        """,
        (case_id, antibiotic_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Case antibiotic association not found")
    return dict(row)


def get_infection_or_404(connection: sqlite3.Connection, infection_id: int) -> dict[str, Any]:
    """Fetch an infection by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM infections WHERE id = ?",
        (infection_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Infection not found")
    return dict(row)


def get_microbiology_specimen_or_404(
    connection: sqlite3.Connection,
    specimen_id: int,
) -> dict[str, Any]:
    """Fetch a microbiology specimen by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM microbiology_specimens WHERE id = ?",
        (specimen_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Microbiology specimen not found")
    return dict(row)


def get_microbiology_agent_or_404(
    connection: sqlite3.Connection,
    microorganism_id: int,
) -> dict[str, Any]:
    """Fetch a microbiology agent by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM microbiology_agents WHERE id = ?",
        (microorganism_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Microbiology agent not found")
    return dict(row)


def get_case_microbiology_or_404(
    connection: sqlite3.Connection,
    case_microbiology_id: int,
) -> dict[str, Any]:
    """Fetch a case_microbiology row by id or raise 404 if not found."""
    row = connection.execute(
        "SELECT * FROM case_microbiology WHERE id = ?",
        (case_microbiology_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Case microbiology row not found")
    return dict(row)


def fetch_all_rows(table_name: str) -> list[dict[str, Any]]:
    """Fetch all rows from the provided table name in ascending id order when available."""
    query = f"SELECT * FROM {table_name}"
    if table_name in {
        "patients",
        "addresses",
        "pathologies",
        "medications",
        "provenance_destination",
        "burn_etiology",
        "burn_unit_cases",
        "infections",
        "microbiology_specimens",
        "microbiology_agents",
        "case_microbiology",
    }:
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
        "endpoints": (
            "/patients, /addresses, /pathologies, /patient-pathologies, /medications, "
            "/patient-medications, /provenance-destinations, /burn-etiologies, /burn-unit-cases, "
            "/infections, /antibiotics, /microbiology-specimens, /microbiology-agents, /case-microbiology"
        ),
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


@app.get("/antibiotics", tags=["antibiotics"], response_model=list[AntibioticRead])
def get_antibiotics() -> list[dict[str, Any]]:
    """Return every antibiotic row from the antibiotics table."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id,
                   name,
                   atc_code,
                   description,
                   created_at,
                   updated_at
            FROM antibiotics
            ORDER BY id
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/antibiotics/{antibiotic_id}", tags=["antibiotics"], response_model=AntibioticRead)
def get_antibiotic(antibiotic_id: int) -> dict[str, Any]:
    """Return one antibiotic row by id."""
    with get_connection() as connection:
        return get_antibiotic_or_404(connection, antibiotic_id)


@app.post("/antibiotics", tags=["antibiotics"], response_model=AntibioticRead, status_code=201)
def create_antibiotic(payload: AntibioticCreate) -> dict[str, Any]:
    """Create a new antibiotic row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO antibiotics (name, atc_code, description)
                VALUES (?, ?, ?)
                """,
                (
                    payload.name,
                    payload.atc_code,
                    payload.description,
                ),
            )
            antibiotic_id = cursor.lastrowid
            row = connection.execute(
                """
                SELECT id,
                       name,
                       atc_code,
                       description,
                       created_at,
                       updated_at
                FROM antibiotics
                WHERE id = ?
                """,
                (antibiotic_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid antibiotic data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Antibiotic created but could not be read back")
    return dict(row)


@app.put("/antibiotics/{antibiotic_id}", tags=["antibiotics"], response_model=AntibioticRead)
def update_antibiotic(antibiotic_id: int, payload: AntibioticWrite) -> dict[str, Any]:
    """Replace antibiotic editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_antibiotic_or_404(connection, antibiotic_id)
            connection.execute(
                """
                UPDATE antibiotics
                SET name = ?,
                    atc_code = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.atc_code,
                    payload.description,
                    antibiotic_id,
                ),
            )
            row = connection.execute(
                """
                SELECT id,
                       name,
                       atc_code,
                       description,
                       created_at,
                       updated_at
                FROM antibiotics
                WHERE id = ?
                """,
                (antibiotic_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid antibiotic data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Antibiotic updated but could not be read back")
    return dict(row)


@app.patch("/antibiotics/{antibiotic_id}", tags=["antibiotics"], response_model=AntibioticRead)
def patch_antibiotic(antibiotic_id: int, payload: AntibioticPatch) -> dict[str, Any]:
    """Partially update antibiotic fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"name", "atc_code", "description"}
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
    values.append(antibiotic_id)

    query = f"UPDATE antibiotics SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_antibiotic_or_404(connection, antibiotic_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT id,
                       name,
                       atc_code,
                       description,
                       created_at,
                       updated_at
                FROM antibiotics
                WHERE id = ?
                """,
                (antibiotic_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid antibiotic data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Antibiotic updated but could not be read back")
    return dict(row)


@app.delete("/antibiotics/{antibiotic_id}", tags=["antibiotics"])
def delete_antibiotic(antibiotic_id: int) -> dict[str, str]:
    """Delete one antibiotic by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_antibiotic_or_404(connection, antibiotic_id)
            connection.execute("DELETE FROM antibiotics WHERE id = ?", (antibiotic_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete antibiotic because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Antibiotic {antibiotic_id} deleted"}


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


@app.get("/patient-medications", tags=["patient_medications"])
def get_patient_medications() -> list[dict[str, Any]]:
    """Return every row from the patient_medications join table."""
    return fetch_all_rows("patient_medications")


@app.post(
    "/patient-medications",
    tags=["patient_medications"],
    response_model=PatientMedicationRead,
    status_code=201,
)
def create_patient_medication_association(payload: PatientMedicationCreate) -> dict[str, Any]:
    """Create a patient-medication association and return the inserted row."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO patient_medications (patient_id, medication_id, prescribed_date, dosage)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.patient_id,
                    payload.medication_id,
                    payload.prescribed_date,
                    payload.dosage,
                ),
            )
            row = connection.execute(
                """
                SELECT *
                FROM patient_medications
                WHERE patient_id = ? AND medication_id = ?
                """,
                (payload.patient_id, payload.medication_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid patient-medication data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association created but could not be read back")
    return dict(row)


@app.patch(
    "/patient-medications/{patient_id}/{medication_id}",
    tags=["patient_medications"],
    response_model=PatientMedicationRead,
)
def patch_patient_medication_association(
    patient_id: int,
    medication_id: int,
    payload: PatientMedicationPatch,
) -> dict[str, Any]:
    """Partially update a patient-medication association row by composite key."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"patient_id", "medication_id", "prescribed_date", "dosage"}
    assignments: list[str] = []
    values: list[Any] = []
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        assignments.append(f"{field} = ?")
        values.append(value)

    if not assignments:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    values.extend([patient_id, medication_id])
    query = (
        f"UPDATE patient_medications SET {', '.join(assignments)} "
        "WHERE patient_id = ? AND medication_id = ?"
    )

    new_patient_id = updates.get("patient_id", patient_id)
    new_medication_id = updates.get("medication_id", medication_id)

    try:
        with get_connection() as connection:
            get_patient_medication_or_404(connection, patient_id, medication_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT *
                FROM patient_medications
                WHERE patient_id = ? AND medication_id = ?
                """,
                (new_patient_id, new_medication_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid patient-medication data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association updated but could not be read back")
    return dict(row)


@app.delete("/patient-medications/{patient_id}/{medication_id}", tags=["patient_medications"])
def delete_patient_medication_association(patient_id: int, medication_id: int) -> dict[str, str]:
    """Delete one patient-medication association row by composite key."""
    with get_connection() as connection:
        get_patient_medication_or_404(connection, patient_id, medication_id)
        connection.execute(
            "DELETE FROM patient_medications WHERE patient_id = ? AND medication_id = ?",
            (patient_id, medication_id),
        )

    return {"message": f"Patient-medication association ({patient_id}, {medication_id}) deleted"}


@app.get("/provenance-destinations", tags=["provenance_destinations"])
def get_provenance_destinations() -> list[dict[str, Any]]:
    """Return every provenance/destination row from the provenance_destination table."""
    return fetch_all_rows("provenance_destination")


@app.get(
    "/provenance-destinations/{provenance_destination_id}",
    tags=["provenance_destinations"],
    response_model=ProvenanceDestinationRead,
)
def get_provenance_destination(provenance_destination_id: int) -> dict[str, Any]:
    """Return one provenance/destination row by id."""
    with get_connection() as connection:
        return get_provenance_destination_or_404(connection, provenance_destination_id)


@app.post(
    "/provenance-destinations",
    tags=["provenance_destinations"],
    response_model=ProvenanceDestinationRead,
    status_code=201,
)
def create_provenance_destination(payload: ProvenanceDestinationCreate) -> dict[str, Any]:
    """Create a new provenance/destination row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO provenance_destination (name, type, location)
                VALUES (?, ?, ?)
                """,
                (
                    payload.name,
                    payload.type,
                    payload.location,
                ),
            )
            provenance_destination_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM provenance_destination WHERE id = ?",
                (provenance_destination_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid provenance/destination data: {exc}") from exc

    if row is None:
        raise HTTPException(
            status_code=500,
            detail="Provenance/destination created but could not be read back",
        )
    return dict(row)


@app.put(
    "/provenance-destinations/{provenance_destination_id}",
    tags=["provenance_destinations"],
    response_model=ProvenanceDestinationRead,
)
def update_provenance_destination(
    provenance_destination_id: int,
    payload: ProvenanceDestinationWrite,
) -> dict[str, Any]:
    """Replace provenance/destination editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_provenance_destination_or_404(connection, provenance_destination_id)
            connection.execute(
                """
                UPDATE provenance_destination
                SET name = ?,
                    type = ?,
                    location = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.type,
                    payload.location,
                    provenance_destination_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM provenance_destination WHERE id = ?",
                (provenance_destination_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid provenance/destination data: {exc}") from exc

    if row is None:
        raise HTTPException(
            status_code=500,
            detail="Provenance/destination updated but could not be read back",
        )
    return dict(row)


@app.patch(
    "/provenance-destinations/{provenance_destination_id}",
    tags=["provenance_destinations"],
    response_model=ProvenanceDestinationRead,
)
def patch_provenance_destination(
    provenance_destination_id: int,
    payload: ProvenanceDestinationPatch,
) -> dict[str, Any]:
    """Partially update provenance/destination fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"name", "type", "location"}
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
    values.append(provenance_destination_id)

    query = f"UPDATE provenance_destination SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_provenance_destination_or_404(connection, provenance_destination_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM provenance_destination WHERE id = ?",
                (provenance_destination_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid provenance/destination data: {exc}") from exc

    if row is None:
        raise HTTPException(
            status_code=500,
            detail="Provenance/destination updated but could not be read back",
        )
    return dict(row)


@app.delete("/provenance-destinations/{provenance_destination_id}", tags=["provenance_destinations"])
def delete_provenance_destination(provenance_destination_id: int) -> dict[str, str]:
    """Delete one provenance/destination row by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_provenance_destination_or_404(connection, provenance_destination_id)
            connection.execute(
                "DELETE FROM provenance_destination WHERE id = ?",
                (provenance_destination_id,),
            )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete provenance/destination because it is referenced by related data: "
                f"{exc}"
            ),
        ) from exc

    return {"message": f"Provenance/destination {provenance_destination_id} deleted"}


@app.get("/burn-etiologies", tags=["burn_etiologies"])
def get_burn_etiologies() -> list[dict[str, Any]]:
    """Return every burn etiology row from the burn_etiology table."""
    return fetch_all_rows("burn_etiology")


@app.get("/burn-etiologies/{burn_etiology_id}", tags=["burn_etiologies"], response_model=BurnEtiologyRead)
def get_burn_etiology(burn_etiology_id: int) -> dict[str, Any]:
    """Return one burn etiology row by id."""
    with get_connection() as connection:
        return get_burn_etiology_or_404(connection, burn_etiology_id)


@app.post("/burn-etiologies", tags=["burn_etiologies"], response_model=BurnEtiologyRead, status_code=201)
def create_burn_etiology(payload: BurnEtiologyCreate) -> dict[str, Any]:
    """Create a new burn etiology row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO burn_etiology (name, description)
                VALUES (?, ?)
                """,
                (
                    payload.name,
                    payload.description,
                ),
            )
            burn_etiology_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM burn_etiology WHERE id = ?",
                (burn_etiology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid burn etiology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Burn etiology created but could not be read back")
    return dict(row)


@app.put("/burn-etiologies/{burn_etiology_id}", tags=["burn_etiologies"], response_model=BurnEtiologyRead)
def update_burn_etiology(burn_etiology_id: int, payload: BurnEtiologyWrite) -> dict[str, Any]:
    """Replace burn etiology editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_burn_etiology_or_404(connection, burn_etiology_id)
            connection.execute(
                """
                UPDATE burn_etiology
                SET name = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.description,
                    burn_etiology_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM burn_etiology WHERE id = ?",
                (burn_etiology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid burn etiology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Burn etiology updated but could not be read back")
    return dict(row)


@app.patch("/burn-etiologies/{burn_etiology_id}", tags=["burn_etiologies"], response_model=BurnEtiologyRead)
def patch_burn_etiology(burn_etiology_id: int, payload: BurnEtiologyPatch) -> dict[str, Any]:
    """Partially update burn etiology fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"name", "description"}
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
    values.append(burn_etiology_id)

    query = f"UPDATE burn_etiology SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_burn_etiology_or_404(connection, burn_etiology_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM burn_etiology WHERE id = ?",
                (burn_etiology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid burn etiology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Burn etiology updated but could not be read back")
    return dict(row)


@app.delete("/burn-etiologies/{burn_etiology_id}", tags=["burn_etiologies"])
def delete_burn_etiology(burn_etiology_id: int) -> dict[str, str]:
    """Delete one burn etiology row by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_burn_etiology_or_404(connection, burn_etiology_id)
            connection.execute("DELETE FROM burn_etiology WHERE id = ?", (burn_etiology_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete burn etiology because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Burn etiology {burn_etiology_id} deleted"}


@app.get("/burn-unit-cases", tags=["burn_unit_cases"])
def get_burn_unit_cases() -> list[dict[str, Any]]:
    """Return every burn unit case row from the burn_unit_cases table."""
    return fetch_all_rows("burn_unit_cases")


@app.get("/burn-unit-cases/{burn_unit_case_id}", tags=["burn_unit_cases"], response_model=BurnUnitCaseRead)
def get_burn_unit_case(burn_unit_case_id: int) -> dict[str, Any]:
    """Return one burn unit case row by id."""
    with get_connection() as connection:
        return get_burn_unit_case_or_404(connection, burn_unit_case_id)


@app.post("/burn-unit-cases", tags=["burn_unit_cases"], response_model=BurnUnitCaseRead, status_code=201)
def create_burn_unit_case(payload: BurnUnitCaseCreate) -> dict[str, Any]:
    """Create a new burn unit case row and return the inserted record."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO burn_unit_cases (
                    id,
                    patient_id,
                    TBSA_burned,
                    admission_date,
                    burn_date,
                    release_date,
                    admission_provenance,
                    release_destination,
                    burn_mecanism,
                    burn_etiology,
                    violence_related,
                    suicide_attempt,
                    accident_type,
                    wildfire,
                    bonfire_fogueira,
                    fireplace_lareira,
                    note,
                    special_forces
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.id,
                    payload.patient_id,
                    payload.TBSA_burned,
                    payload.admission_date,
                    payload.burn_date,
                    payload.release_date,
                    payload.admission_provenance,
                    payload.release_destination,
                    payload.burn_mecanism,
                    payload.burn_etiology,
                    payload.violence_related,
                    payload.suicide_attempt,
                    payload.accident_type,
                    payload.wildfire,
                    payload.bonfire_fogueira,
                    payload.fireplace_lareira,
                    payload.note,
                    payload.special_forces,
                ),
            )
            row = connection.execute(
                "SELECT * FROM burn_unit_cases WHERE id = ?",
                (payload.id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid burn unit case data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Burn unit case created but could not be read back")
    return dict(row)


@app.put("/burn-unit-cases/{burn_unit_case_id}", tags=["burn_unit_cases"], response_model=BurnUnitCaseRead)
def update_burn_unit_case(burn_unit_case_id: int, payload: BurnUnitCaseWrite) -> dict[str, Any]:
    """Replace burn unit case editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_burn_unit_case_or_404(connection, burn_unit_case_id)
            connection.execute(
                """
                UPDATE burn_unit_cases
                SET patient_id = ?,
                    TBSA_burned = ?,
                    admission_date = ?,
                    burn_date = ?,
                    release_date = ?,
                    admission_provenance = ?,
                    release_destination = ?,
                    burn_mecanism = ?,
                    burn_etiology = ?,
                    violence_related = ?,
                    suicide_attempt = ?,
                    accident_type = ?,
                    wildfire = ?,
                    bonfire_fogueira = ?,
                    fireplace_lareira = ?,
                    note = ?,
                    special_forces = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.patient_id,
                    payload.TBSA_burned,
                    payload.admission_date,
                    payload.burn_date,
                    payload.release_date,
                    payload.admission_provenance,
                    payload.release_destination,
                    payload.burn_mecanism,
                    payload.burn_etiology,
                    payload.violence_related,
                    payload.suicide_attempt,
                    payload.accident_type,
                    payload.wildfire,
                    payload.bonfire_fogueira,
                    payload.fireplace_lareira,
                    payload.note,
                    payload.special_forces,
                    burn_unit_case_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM burn_unit_cases WHERE id = ?",
                (burn_unit_case_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid burn unit case data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Burn unit case updated but could not be read back")
    return dict(row)


@app.patch("/burn-unit-cases/{burn_unit_case_id}", tags=["burn_unit_cases"], response_model=BurnUnitCaseRead)
def patch_burn_unit_case(burn_unit_case_id: int, payload: BurnUnitCasePatch) -> dict[str, Any]:
    """Partially update burn unit case fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {
        "patient_id",
        "TBSA_burned",
        "admission_date",
        "burn_date",
        "release_date",
        "admission_provenance",
        "release_destination",
        "burn_mecanism",
        "burn_etiology",
        "violence_related",
        "suicide_attempt",
        "accident_type",
        "wildfire",
        "bonfire_fogueira",
        "fireplace_lareira",
        "note",
        "special_forces",
    }
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
    values.append(burn_unit_case_id)

    query = f"UPDATE burn_unit_cases SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_burn_unit_case_or_404(connection, burn_unit_case_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM burn_unit_cases WHERE id = ?",
                (burn_unit_case_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid burn unit case data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Burn unit case updated but could not be read back")
    return dict(row)


@app.delete("/burn-unit-cases/{burn_unit_case_id}", tags=["burn_unit_cases"])
def delete_burn_unit_case(burn_unit_case_id: int) -> dict[str, str]:
    """Delete one burn unit case row by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_burn_unit_case_or_404(connection, burn_unit_case_id)
            connection.execute("DELETE FROM burn_unit_cases WHERE id = ?", (burn_unit_case_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete burn unit case because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Burn unit case {burn_unit_case_id} deleted"}


@app.get("/case-burns", tags=["case_burns"])
def get_case_burns(case_id: int | None = None) -> list[dict[str, Any]]:
    """Return case_burns optionally filtered by case_id."""
    with get_connection() as connection:
        if case_id is not None:
            rows = connection.execute(
                """
                SELECT * FROM case_burns
                WHERE case_id = ?
                ORDER BY case_id, burn_depth_id, anatomic_location_id
                """,
                (case_id,)
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM case_burns ORDER BY case_id, burn_depth_id, anatomic_location_id"
            ).fetchall()
    return [dict(row) for row in rows]

@app.get(
    "/case-burns/{case_id}/{burn_depth_id}/{anatomic_location_id}",
    tags=["case_burns"],
    response_model=CaseBurnsRead,
)
def get_case_burn_association(
    case_id: int, burn_depth_id: int, anatomic_location_id: int
) -> dict[str, Any]:
    """Return one case_burns association by composite key."""
    with get_connection() as connection:
        return get_case_burns_or_404(connection, case_id, burn_depth_id, anatomic_location_id)

@app.post(
    "/case-burns",
    tags=["case_burns"],
    response_model=CaseBurnsRead,
    status_code=201,
)
def create_case_burn_association(payload: CaseBurnsCreate) -> dict[str, Any]:
    """Create a case_burns association and return the inserted row."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO case_burns (case_id, burn_depth_id, anatomic_location_id, note)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.case_id,
                    payload.burn_depth_id,
                    payload.anatomic_location_id,
                    payload.note,
                ),
            )
            row = connection.execute(
                """
                SELECT *
                FROM case_burns
                WHERE case_id = ? AND burn_depth_id = ? AND anatomic_location_id = ?
                """,
                (payload.case_id, payload.burn_depth_id, payload.anatomic_location_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_burns data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association created but could not be read back")
    return dict(row)

@app.patch(
    "/case-burns/{case_id}/{burn_depth_id}/{anatomic_location_id}",
    tags=["case_burns"],
    response_model=CaseBurnsRead,
)
def patch_case_burn_association(
    case_id: int,
    burn_depth_id: int,
    anatomic_location_id: int,
    payload: CaseBurnsPatch,
) -> dict[str, Any]:
    """Partially update an association row by composite key."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"case_id", "burn_depth_id", "anatomic_location_id", "note"}
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
    values.extend([case_id, burn_depth_id, anatomic_location_id])
    
    query = (
        f"UPDATE case_burns SET {', '.join(assignments)} "
        "WHERE case_id = ? AND burn_depth_id = ? AND anatomic_location_id = ?"
    )

    new_case_id = updates.get("case_id", case_id)
    new_burn_depth_id = updates.get("burn_depth_id", burn_depth_id)
    new_anatomic_location_id = updates.get("anatomic_location_id", anatomic_location_id)

    try:
        with get_connection() as connection:
            get_case_burns_or_404(connection, case_id, burn_depth_id, anatomic_location_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT *
                FROM case_burns
                WHERE case_id = ? AND burn_depth_id = ? AND anatomic_location_id = ?
                """,
                (new_case_id, new_burn_depth_id, new_anatomic_location_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_burns data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association updated but could not be read back")
    return dict(row)

@app.delete("/case-burns/{case_id}/{burn_depth_id}/{anatomic_location_id}", tags=["case_burns"])
def delete_case_burn_association(case_id: int, burn_depth_id: int, anatomic_location_id: int) -> dict[str, str]:
    """Delete one case_burns association row by composite key."""
    with get_connection() as connection:
        get_case_burns_or_404(connection, case_id, burn_depth_id, anatomic_location_id)
        connection.execute(
            "DELETE FROM case_burns WHERE case_id = ? AND burn_depth_id = ? AND anatomic_location_id = ?",
            (case_id, burn_depth_id, anatomic_location_id),
        )

    return {"message": f"Association ({case_id}, {burn_depth_id}, {anatomic_location_id}) deleted"}


@app.get("/case-infections", tags=["case_infections"], response_model=list[CaseInfectionRead])
def get_case_infections(case_id: int | None = None) -> list[dict[str, Any]]:
    """Return case_infections optionally filtered by case_id."""
    with get_connection() as connection:
        if case_id is not None:
            rows = connection.execute(
                """
                SELECT *
                FROM case_infections
                WHERE case_id = ?
                ORDER BY case_id, infection_id
                """,
                (case_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM case_infections ORDER BY case_id, infection_id"
            ).fetchall()
    return [dict(row) for row in rows]


@app.get(
    "/case-infections/{case_id}/{infection_id}",
    tags=["case_infections"],
    response_model=CaseInfectionRead,
)
def get_case_infection(case_id: int, infection_id: int) -> dict[str, Any]:
    """Return one case_infections association by composite key."""
    with get_connection() as connection:
        return get_case_infection_or_404(connection, case_id, infection_id)


@app.post(
    "/case-infections",
    tags=["case_infections"],
    response_model=CaseInfectionRead,
    status_code=201,
)
def create_case_infection(payload: CaseInfectionCreate) -> dict[str, Any]:
    """Create a case_infections association and return the inserted row."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO case_infections (case_id, infection_id, date_of_infection, note)
                VALUES (?, ?, ?, ?)
                """,
                (
                    payload.case_id,
                    payload.infection_id,
                    payload.date_of_infection,
                    payload.note,
                ),
            )
            row = connection.execute(
                """
                SELECT *
                FROM case_infections
                WHERE case_id = ? AND infection_id = ?
                """,
                (payload.case_id, payload.infection_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_infections data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association created but could not be read back")
    return dict(row)


@app.patch(
    "/case-infections/{case_id}/{infection_id}",
    tags=["case_infections"],
    response_model=CaseInfectionRead,
)
def patch_case_infection(
    case_id: int,
    infection_id: int,
    payload: CaseInfectionPatch,
) -> dict[str, Any]:
    """Partially update a case_infections association row by composite key."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"case_id", "infection_id", "date_of_infection", "note"}
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
    values.extend([case_id, infection_id])

    query = f"UPDATE case_infections SET {', '.join(assignments)} WHERE case_id = ? AND infection_id = ?"

    new_case_id = updates.get("case_id", case_id)
    new_infection_id = updates.get("infection_id", infection_id)

    try:
        with get_connection() as connection:
            get_case_infection_or_404(connection, case_id, infection_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT *
                FROM case_infections
                WHERE case_id = ? AND infection_id = ?
                """,
                (new_case_id, new_infection_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_infections data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association updated but could not be read back")
    return dict(row)


@app.delete("/case-infections/{case_id}/{infection_id}", tags=["case_infections"])
def delete_case_infection(case_id: int, infection_id: int) -> dict[str, str]:
    """Delete one case_infections association row by composite key."""
    with get_connection() as connection:
        get_case_infection_or_404(connection, case_id, infection_id)
        connection.execute(
            "DELETE FROM case_infections WHERE case_id = ? AND infection_id = ?",
            (case_id, infection_id),
        )

    return {"message": f"Association ({case_id}, {infection_id}) deleted"}


@app.get("/case-antibiotics", tags=["case_antibiotics"], response_model=list[CaseAntibioticRead])
def get_case_antibiotics(case_id: int | None = None) -> list[dict[str, Any]]:
    """Return case_antibiotics optionally filtered by case_id."""
    with get_connection() as connection:
        if case_id is not None:
            rows = connection.execute(
                """
                SELECT *
                FROM case_antibiotics
                WHERE case_id = ?
                ORDER BY case_id, antibiotic_id
                """,
                (case_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM case_antibiotics ORDER BY case_id, antibiotic_id"
            ).fetchall()
    return [dict(row) for row in rows]


@app.get(
    "/case-antibiotics/{case_id}/{antibiotic_id}",
    tags=["case_antibiotics"],
    response_model=CaseAntibioticRead,
)
def get_case_antibiotic(case_id: int, antibiotic_id: int) -> dict[str, Any]:
    """Return one case_antibiotics association by composite key."""
    with get_connection() as connection:
        return get_case_antibiotic_or_404(connection, case_id, antibiotic_id)


@app.post(
    "/case-antibiotics",
    tags=["case_antibiotics"],
    response_model=CaseAntibioticRead,
    status_code=201,
)
def create_case_antibiotic(payload: CaseAntibioticCreate) -> dict[str, Any]:
    """Create a case_antibiotics association and return the inserted row."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO case_antibiotics (
                    case_id,
                    antibiotic_id,
                    indication,
                    date_started,
                    date_stopped,
                    note
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.case_id,
                    payload.antibiotic_id,
                    payload.indication,
                    payload.date_started,
                    payload.date_stopped,
                    payload.note,
                ),
            )
            row = connection.execute(
                """
                SELECT *
                FROM case_antibiotics
                WHERE case_id = ? AND antibiotic_id = ?
                """,
                (payload.case_id, payload.antibiotic_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_antibiotics data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association created but could not be read back")
    return dict(row)


@app.patch(
    "/case-antibiotics/{case_id}/{antibiotic_id}",
    tags=["case_antibiotics"],
    response_model=CaseAntibioticRead,
)
def patch_case_antibiotic(
    case_id: int,
    antibiotic_id: int,
    payload: CaseAntibioticPatch,
) -> dict[str, Any]:
    """Partially update a case_antibiotics association row by composite key."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {
        "case_id",
        "antibiotic_id",
        "indication",
        "date_started",
        "date_stopped",
        "note",
    }
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
    values.extend([case_id, antibiotic_id])

    query = f"UPDATE case_antibiotics SET {', '.join(assignments)} WHERE case_id = ? AND antibiotic_id = ?"

    new_case_id = updates.get("case_id", case_id)
    new_antibiotic_id = updates.get("antibiotic_id", antibiotic_id)

    try:
        with get_connection() as connection:
            get_case_antibiotic_or_404(connection, case_id, antibiotic_id)
            connection.execute(query, values)
            row = connection.execute(
                """
                SELECT *
                FROM case_antibiotics
                WHERE case_id = ? AND antibiotic_id = ?
                """,
                (new_case_id, new_antibiotic_id),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_antibiotics data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Association updated but could not be read back")
    return dict(row)


@app.delete("/case-antibiotics/{case_id}/{antibiotic_id}", tags=["case_antibiotics"])
def delete_case_antibiotic(case_id: int, antibiotic_id: int) -> dict[str, str]:
    """Delete one case_antibiotics association row by composite key."""
    with get_connection() as connection:
        get_case_antibiotic_or_404(connection, case_id, antibiotic_id)
        connection.execute(
            "DELETE FROM case_antibiotics WHERE case_id = ? AND antibiotic_id = ?",
            (case_id, antibiotic_id),
        )

    return {"message": f"Association ({case_id}, {antibiotic_id}) deleted"}



# ==========================================
# CASE ASSOCIATED INJURIES (case_associated_injuries)
# ==========================================

def get_case_associated_injury_or_404(connection: sqlite3.Connection, case_id: int, injury_id: int) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM case_associated_injuries WHERE case_id = ? AND injury_id = ?",
        (case_id, injury_id),
    ).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Association with case_id={case_id} and injury_id={injury_id} not found",
        )
    return row

@app.get("/case-associated-injuries", tags=["case_associated_injuries"], response_model=list[CaseAssociatedInjuryRead])
def get_all_case_associated_injuries() -> list[dict[str, Any]]:
    """Return every row from the case_associated_injuries table."""
    return fetch_all_rows("case_associated_injuries")

@app.get("/case-associated-injuries/{case_id}", tags=["case_associated_injuries"], response_model=list[CaseAssociatedInjuryRead])
def get_case_associated_injuries_by_case(case_id: int) -> list[dict[str, Any]]:
    """Return all case_associated_injuries rows for a particular case."""
    with get_connection() as connection:
        get_burn_unit_case_or_404(connection, case_id)
        rows = connection.execute(
            "SELECT * FROM case_associated_injuries WHERE case_id = ?", (case_id,)
        ).fetchall()
        return [dict(r) for r in rows]

@app.get("/case-associated-injuries/{case_id}/{injury_id}", tags=["case_associated_injuries"], response_model=CaseAssociatedInjuryRead)
def get_case_associated_injury_single(case_id: int, injury_id: int) -> dict[str, Any]:
    """Return one case_associated_injuries association row."""
    with get_connection() as connection:
        row = get_case_associated_injury_or_404(connection, case_id, injury_id)
        return dict(row)

@app.post("/case-associated-injuries", tags=["case_associated_injuries"], response_model=CaseAssociatedInjuryRead, status_code=201)
def create_case_associated_injury(payload: CaseAssociatedInjuryCreate) -> dict[str, Any]:
    """Create a new case_associated_injuries association row."""
    with get_connection() as connection:
        get_burn_unit_case_or_404(connection, payload.case_id)
        get_pathology_or_404(connection, payload.injury_id)

        existing = connection.execute(
            "SELECT 1 FROM case_associated_injuries WHERE case_id = ? AND injury_id = ?",
            (payload.case_id, payload.injury_id),
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Case associated injury association already exists for case_id={payload.case_id} and injury_id={payload.injury_id}"
            )

        connection.execute(
            """
            INSERT INTO case_associated_injuries (case_id, injury_id, date_of_injury, note)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.case_id,
                payload.injury_id,
                payload.date_of_injury.isoformat() if payload.date_of_injury else None,
                payload.note,
            ),
        )
        row = get_case_associated_injury_or_404(connection, payload.case_id, payload.injury_id)
        return dict(row)

@app.patch("/case-associated-injuries/{case_id}/{injury_id}", tags=["case_associated_injuries"], response_model=CaseAssociatedInjuryRead)
def update_case_associated_injury(case_id: int, injury_id: int, payload: CaseAssociatedInjuryPatch) -> dict[str, Any]:
    """Update an existing case_associated_injuries association row."""
    with get_connection() as connection:
        row = get_case_associated_injury_or_404(connection, case_id, injury_id)
        current_data = dict(row)

        update_data = payload.model_dump(exclude_unset=True)
        if "date_of_injury" in update_data and update_data["date_of_injury"] is not None:
            update_data["date_of_injury"] = update_data["date_of_injury"].isoformat()

        if not update_data:
            return current_data

        set_clauses = " , ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values())
        
        values.extend([case_id, injury_id])
        update_query = f"UPDATE case_associated_injuries SET {set_clauses}, updated_at = CURRENT_TIMESTAMP WHERE case_id = ? AND injury_id = ?"
        
        connection.execute(update_query, tuple(values))
        updated_row = get_case_associated_injury_or_404(connection, case_id, injury_id)
        return dict(updated_row)

@app.delete("/case-associated-injuries/{case_id}/{injury_id}", tags=["case_associated_injuries"])
def delete_case_associated_injury(case_id: int, injury_id: int) -> dict[str, str]:
    """Delete one case_associated_injuries association row."""
    with get_connection() as connection:
        get_case_associated_injury_or_404(connection, case_id, injury_id)
        connection.execute(
            "DELETE FROM case_associated_injuries WHERE case_id = ? AND injury_id = ?",
            (case_id, injury_id),
        )

    return {"message": f"Association ({case_id}, {injury_id}) deleted"}

class BurnDepthRead(BaseModel):
    id: int
    depth_new: str
    depth_old: str | None = None
    description: str | None = None

class AnatomicLocationRead(BaseModel):
    id: int
    name: str
    description: str | None = None

@app.get("/burn-depths", tags=["burn_depth"], response_model=list[BurnDepthRead])
def get_burn_depths() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM burn_depth ORDER BY id").fetchall()
    return [dict(row) for row in rows]

@app.get("/anatomic-locations", tags=["anatomic_locations"], response_model=list[AnatomicLocationRead])
def get_anatomic_locations() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM anatomic_locations ORDER BY id").fetchall()
    return [dict(row) for row in rows]

@app.get("/infections", tags=["infections"], response_model=list[InfectionRead])
def get_infections() -> list[dict[str, Any]]:
    """Return every infection row from the infections table."""
    return fetch_all_rows("infections")


@app.get("/infections/{infection_id}", tags=["infections"], response_model=InfectionRead)
def get_infection(infection_id: int) -> dict[str, Any]:
    """Return one infection row by id."""
    with get_connection() as connection:
        return get_infection_or_404(connection, infection_id)


@app.post("/infections", tags=["infections"], response_model=InfectionRead, status_code=201)
def create_infection(payload: InfectionCreate) -> dict[str, Any]:
    """Create a new infection row and return the inserted record."""
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO infections (id, name, description)
                VALUES (?, ?, ?)
                """,
                (
                    payload.id,
                    payload.name,
                    payload.description,
                ),
            )
            row = connection.execute(
                "SELECT * FROM infections WHERE id = ?",
                (payload.id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid infection data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Infection created but could not be read back")
    return dict(row)


@app.put("/infections/{infection_id}", tags=["infections"], response_model=InfectionRead)
def update_infection(infection_id: int, payload: InfectionWrite) -> dict[str, Any]:
    """Replace infection editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_infection_or_404(connection, infection_id)
            connection.execute(
                """
                UPDATE infections
                SET name = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.description,
                    infection_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM infections WHERE id = ?",
                (infection_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid infection data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Infection updated but could not be read back")
    return dict(row)


@app.delete("/infections/{infection_id}", tags=["infections"])
def delete_infection(infection_id: int) -> dict[str, str]:
    """Delete one infection by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_infection_or_404(connection, infection_id)
            connection.execute("DELETE FROM infections WHERE id = ?", (infection_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete infection because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Infection {infection_id} deleted"}


@app.get("/microbiology-specimens", tags=["microbiology_specimens"], response_model=list[MicrobiologySpecimenRead])
def get_microbiology_specimens() -> list[dict[str, Any]]:
    """Return every microbiology specimen row from the microbiology_specimens table."""
    return fetch_all_rows("microbiology_specimens")


@app.get(
    "/microbiology-specimens/{specimen_id}",
    tags=["microbiology_specimens"],
    response_model=MicrobiologySpecimenRead,
)
def get_microbiology_specimen(specimen_id: int) -> dict[str, Any]:
    """Return one microbiology specimen row by id."""
    with get_connection() as connection:
        return get_microbiology_specimen_or_404(connection, specimen_id)


@app.post(
    "/microbiology-specimens",
    tags=["microbiology_specimens"],
    response_model=MicrobiologySpecimenRead,
    status_code=201,
)
def create_microbiology_specimen(payload: MicrobiologySpecimenCreate) -> dict[str, Any]:
    """Create a new microbiology specimen row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO microbiology_specimens (loinc_code, specimen_type, note)
                VALUES (?, ?, ?)
                """,
                (
                    payload.loinc_code,
                    payload.specimen_type,
                    payload.note,
                ),
            )
            specimen_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM microbiology_specimens WHERE id = ?",
                (specimen_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid microbiology specimen data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Microbiology specimen created but could not be read back")
    return dict(row)


@app.put(
    "/microbiology-specimens/{specimen_id}",
    tags=["microbiology_specimens"],
    response_model=MicrobiologySpecimenRead,
)
def update_microbiology_specimen(specimen_id: int, payload: MicrobiologySpecimenWrite) -> dict[str, Any]:
    """Replace microbiology specimen editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_microbiology_specimen_or_404(connection, specimen_id)
            connection.execute(
                """
                UPDATE microbiology_specimens
                SET loinc_code = ?,
                    specimen_type = ?,
                    note = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.loinc_code,
                    payload.specimen_type,
                    payload.note,
                    specimen_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM microbiology_specimens WHERE id = ?",
                (specimen_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid microbiology specimen data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Microbiology specimen updated but could not be read back")
    return dict(row)


@app.patch(
    "/microbiology-specimens/{specimen_id}",
    tags=["microbiology_specimens"],
    response_model=MicrobiologySpecimenRead,
)
def patch_microbiology_specimen(specimen_id: int, payload: MicrobiologySpecimenPatch) -> dict[str, Any]:
    """Partially update microbiology specimen fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"loinc_code", "specimen_type", "note"}
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
    values.append(specimen_id)
    query = f"UPDATE microbiology_specimens SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_microbiology_specimen_or_404(connection, specimen_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM microbiology_specimens WHERE id = ?",
                (specimen_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid microbiology specimen data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Microbiology specimen updated but could not be read back")
    return dict(row)


@app.delete("/microbiology-specimens/{specimen_id}", tags=["microbiology_specimens"])
def delete_microbiology_specimen(specimen_id: int) -> dict[str, str]:
    """Delete one microbiology specimen by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_microbiology_specimen_or_404(connection, specimen_id)
            connection.execute("DELETE FROM microbiology_specimens WHERE id = ?", (specimen_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete microbiology specimen because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Microbiology specimen {specimen_id} deleted"}


@app.get("/microbiology-agents", tags=["microbiology_agents"], response_model=list[MicrobiologyAgentRead])
def get_microbiology_agents() -> list[dict[str, Any]]:
    """Return every microbiology agent row from the microbiology_agents table."""
    return fetch_all_rows("microbiology_agents")


@app.get(
    "/microbiology-agents/{microorganism_id}",
    tags=["microbiology_agents"],
    response_model=MicrobiologyAgentRead,
)
def get_microbiology_agent(microorganism_id: int) -> dict[str, Any]:
    """Return one microbiology agent row by id."""
    with get_connection() as connection:
        return get_microbiology_agent_or_404(connection, microorganism_id)


@app.post(
    "/microbiology-agents",
    tags=["microbiology_agents"],
    response_model=MicrobiologyAgentRead,
    status_code=201,
)
def create_microbiology_agent(payload: MicrobiologyAgentCreate) -> dict[str, Any]:
    """Create a new microbiology agent row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO microbiology_agents (snomed_ct_code, name, description)
                VALUES (?, ?, ?)
                """,
                (
                    payload.snomed_ct_code,
                    payload.name,
                    payload.description,
                ),
            )
            microorganism_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM microbiology_agents WHERE id = ?",
                (microorganism_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid microbiology agent data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Microbiology agent created but could not be read back")
    return dict(row)


@app.put(
    "/microbiology-agents/{microorganism_id}",
    tags=["microbiology_agents"],
    response_model=MicrobiologyAgentRead,
)
def update_microbiology_agent(microorganism_id: int, payload: MicrobiologyAgentWrite) -> dict[str, Any]:
    """Replace microbiology agent editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_microbiology_agent_or_404(connection, microorganism_id)
            connection.execute(
                """
                UPDATE microbiology_agents
                SET snomed_ct_code = ?,
                    name = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.snomed_ct_code,
                    payload.name,
                    payload.description,
                    microorganism_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM microbiology_agents WHERE id = ?",
                (microorganism_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid microbiology agent data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Microbiology agent updated but could not be read back")
    return dict(row)


@app.patch(
    "/microbiology-agents/{microorganism_id}",
    tags=["microbiology_agents"],
    response_model=MicrobiologyAgentRead,
)
def patch_microbiology_agent(microorganism_id: int, payload: MicrobiologyAgentPatch) -> dict[str, Any]:
    """Partially update microbiology agent fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {"snomed_ct_code", "name", "description"}
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
    values.append(microorganism_id)
    query = f"UPDATE microbiology_agents SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_microbiology_agent_or_404(connection, microorganism_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM microbiology_agents WHERE id = ?",
                (microorganism_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid microbiology agent data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Microbiology agent updated but could not be read back")
    return dict(row)


@app.delete("/microbiology-agents/{microorganism_id}", tags=["microbiology_agents"])
def delete_microbiology_agent(microorganism_id: int) -> dict[str, str]:
    """Delete one microbiology agent by id when no child rows block the operation."""
    try:
        with get_connection() as connection:
            get_microbiology_agent_or_404(connection, microorganism_id)
            connection.execute("DELETE FROM microbiology_agents WHERE id = ?", (microorganism_id,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete microbiology agent because it is referenced by related data: {exc}",
        ) from exc

    return {"message": f"Microbiology agent {microorganism_id} deleted"}


@app.get("/case-microbiology", tags=["case_microbiology"], response_model=list[CaseMicrobiologyRead])
def get_case_microbiology(case_id: int | None = None) -> list[dict[str, Any]]:
    """Return case_microbiology rows optionally filtered by case_id."""
    with get_connection() as connection:
        if case_id is not None:
            rows = connection.execute(
                "SELECT * FROM case_microbiology WHERE case_id = ? ORDER BY id",
                (case_id,),
            ).fetchall()
        else:
            rows = connection.execute("SELECT * FROM case_microbiology ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@app.get(
    "/case-microbiology/{case_microbiology_id}",
    tags=["case_microbiology"],
    response_model=CaseMicrobiologyRead,
)
def get_case_microbiology_row(case_microbiology_id: int) -> dict[str, Any]:
    """Return one case_microbiology row by id."""
    with get_connection() as connection:
        return get_case_microbiology_or_404(connection, case_microbiology_id)


@app.post(
    "/case-microbiology",
    tags=["case_microbiology"],
    response_model=CaseMicrobiologyRead,
    status_code=201,
)
def create_case_microbiology(payload: CaseMicrobiologyCreate) -> dict[str, Any]:
    """Create a new case_microbiology row and return the inserted record."""
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO case_microbiology (
                    case_id,
                    specimen_id,
                    microorganism_id,
                    hospital_test_id,
                    date_of_collection,
                    date_of_reporting,
                    note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.case_id,
                    payload.specimen_id,
                    payload.microorganism_id,
                    payload.hospital_test_id,
                    payload.date_of_collection,
                    payload.date_of_reporting,
                    payload.note,
                ),
            )
            case_microbiology_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM case_microbiology WHERE id = ?",
                (case_microbiology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_microbiology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Case microbiology row created but could not be read back")
    return dict(row)


@app.put(
    "/case-microbiology/{case_microbiology_id}",
    tags=["case_microbiology"],
    response_model=CaseMicrobiologyRead,
)
def update_case_microbiology(case_microbiology_id: int, payload: CaseMicrobiologyWrite) -> dict[str, Any]:
    """Replace case_microbiology editable fields by id and return the updated record."""
    try:
        with get_connection() as connection:
            get_case_microbiology_or_404(connection, case_microbiology_id)
            connection.execute(
                """
                UPDATE case_microbiology
                SET case_id = ?,
                    specimen_id = ?,
                    microorganism_id = ?,
                    hospital_test_id = ?,
                    date_of_collection = ?,
                    date_of_reporting = ?,
                    note = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload.case_id,
                    payload.specimen_id,
                    payload.microorganism_id,
                    payload.hospital_test_id,
                    payload.date_of_collection,
                    payload.date_of_reporting,
                    payload.note,
                    case_microbiology_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM case_microbiology WHERE id = ?",
                (case_microbiology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_microbiology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Case microbiology row updated but could not be read back")
    return dict(row)


@app.patch(
    "/case-microbiology/{case_microbiology_id}",
    tags=["case_microbiology"],
    response_model=CaseMicrobiologyRead,
)
def patch_case_microbiology(case_microbiology_id: int, payload: CaseMicrobiologyPatch) -> dict[str, Any]:
    """Partially update case_microbiology fields by id and return the updated record."""
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {
        "case_id",
        "specimen_id",
        "microorganism_id",
        "hospital_test_id",
        "date_of_collection",
        "date_of_reporting",
        "note",
    }
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
    values.append(case_microbiology_id)
    query = f"UPDATE case_microbiology SET {', '.join(assignments)} WHERE id = ?"

    try:
        with get_connection() as connection:
            get_case_microbiology_or_404(connection, case_microbiology_id)
            connection.execute(query, values)
            row = connection.execute(
                "SELECT * FROM case_microbiology WHERE id = ?",
                (case_microbiology_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid case_microbiology data: {exc}") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Case microbiology row updated but could not be read back")
    return dict(row)


@app.delete("/case-microbiology/{case_microbiology_id}", tags=["case_microbiology"])
def delete_case_microbiology(case_microbiology_id: int) -> dict[str, str]:
    """Delete one case_microbiology row by id."""
    with get_connection() as connection:
        get_case_microbiology_or_404(connection, case_microbiology_id)
        connection.execute("DELETE FROM case_microbiology WHERE id = ?", (case_microbiology_id,))

    return {"message": f"Case microbiology row {case_microbiology_id} deleted"}
