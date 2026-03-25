"""Streamlit frontend for managing patients via the FastAPI backend."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st
from case_export_module import render_case_export_module

ALLOWED_GENDERS = ["M", "F", "other"]
ALLOWED_PATHOLOGY_STATUSES = ["Active", "Inactive"]
ALLOWED_PROVENANCE_TYPES = ["hospital", "department", "emergency", "other"]
ALLOWED_BURN_MECANISMS = ["heat", "electrical_discharge", "friction", "chemical", "radiaton", "other"]
ALLOWED_ACCIDENT_TYPES = ["workplace", "domestic", "traffic", "war", "terrorism", "other"]
ALLOWED_SPECIAL_FORCES = ["army", "navy", "air_force", "firefighters", "police", "other"]
API_BASE_URL = os.getenv("BURN_API_URL", "http://127.0.0.1:8000").rstrip("/")

# Centralized visual tokens to simplify theme maintenance.
UI_THEME = {
    "bg": "#f3f8ff",
    "surface": "#ffffff",
    "surface_soft": "#f8fbff",
    "text": "#0f172a",
    "muted": "#5b6b82",
    "blue": "#2563eb",
    "blue_dark": "#1d4ed8",
    "green": "#16a34a",
    "border": "#d6e7ff",
}


def inject_style() -> None:
    """Apply a compact and consistent app style from centralized theme tokens."""
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {UI_THEME['bg']};
            --surface: {UI_THEME['surface']};
            --surface-soft: {UI_THEME['surface_soft']};
            --text: {UI_THEME['text']};
            --muted: {UI_THEME['muted']};
            --blue: {UI_THEME['blue']};
            --blue-dark: {UI_THEME['blue_dark']};
            --green: {UI_THEME['green']};
            --border: {UI_THEME['border']};
        }}

        .stApp {{
            background: linear-gradient(180deg, #eaf4ff 0%, var(--bg) 55%, #ffffff 100%);
            color: var(--text);
        }}

        .block-container {{
            max-width: 1100px;
            padding-top: 1.15rem;
            padding-bottom: 1.5rem;
        }}

        h1, h2, h3 {{
            color: #12233d;
            margin-bottom: 0.2rem;
            letter-spacing: 0.01em;
        }}

        .ui-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.7rem 0.85rem 0.35rem 0.85rem;
            margin: 0.5rem 0 0.8rem 0;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        }}

        .ui-card.compact {{
            padding-top: 0.45rem;
        }}

        .ui-badge {{
            display: inline-block;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            padding: 0.16rem 0.54rem;
            border-radius: 999px;
            background: #dbeafe;
            border: 1px solid #bfdbfe;
            color: #1e3a8a;
            font-size: 0.76rem;
            font-weight: 600;
        }}

        .stCaption {{
            color: var(--muted);
        }}

        div[data-testid="stForm"] {{
            background: var(--surface-soft);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.68rem 0.78rem;
        }}

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div,
        .stDateInput > div > div {{
            background: #ffffff !important;
            border: 1px solid #b7d2ff !important;
        }}

        .stButton > button,
        .stForm button {{
            background: linear-gradient(180deg, var(--blue) 0%, var(--blue-dark) 100%);
            color: #ffffff;
            border: 0;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.35rem 0.72rem;
        }}

        .stButton > button:hover,
        .stForm button:hover {{
            filter: brightness(1.05);
        }}

        .crud-title {{
            margin: 0.15rem 0 0.55rem 0;
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f2852;
        }}

        .stAlert {{
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def card_open(compact: bool = False) -> None:
    """Open a visual card container."""
    extra = " compact" if compact else ""
    st.markdown(f"<div class=\"ui-card{extra}\">", unsafe_allow_html=True)


def card_close() -> None:
    """Close the visual card container."""
    st.markdown("</div>", unsafe_allow_html=True)


def section_title(title: str) -> None:
    """Render unified section title text."""
    st.markdown(f"<div class='crud-title'>{title}</div>", unsafe_allow_html=True)


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    """Call backend API and return status code plus parsed JSON when available."""
    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.request(method=method, url=url, json=payload, timeout=15)
    except requests.RequestException as exc:
        return 503, {
            "detail": (
                f"Could not reach backend at {API_BASE_URL}. "
                "Start the API server or verify --api-url."
            ),
            "error": str(exc),
        }
    try:
        data = response.json()
    except ValueError:
        data = response.text
    return response.status_code, data


@st.cache_data(ttl=5)
def load_patients() -> list[dict[str, Any]]:
    """Load all patients from API."""
    status, data = request_json("GET", "/patients")
    if status != 200:
        raise RuntimeError(f"Could not load patients: {data}")
    return data


@st.cache_data(ttl=60)
def load_addresses() -> list[dict[str, Any]]:
    """Load all addresses from API."""
    status, data = request_json("GET", "/addresses")
    if status != 200:
        raise RuntimeError(f"Could not load addresses: {data}")
    return data


@st.cache_data(ttl=5)
def load_pathologies() -> list[dict[str, Any]]:
    """Load all pathologies from API."""
    status, data = request_json("GET", "/pathologies")
    if status != 200:
        raise RuntimeError(f"Could not load pathologies: {data}")
    return data


@st.cache_data(ttl=5)
def load_patient_pathologies() -> list[dict[str, Any]]:
    """Load all patient-pathology association rows from API."""
    status, data = request_json("GET", "/patient-pathologies")
    if status != 200:
        raise RuntimeError(f"Could not load patient-pathologies: {data}")
    return data


@st.cache_data(ttl=5)
def load_patient_medications() -> list[dict[str, Any]]:
    """Load all patient-medication association rows from API."""
    status, data = request_json("GET", "/patient-medications")
    if status != 200:
        raise RuntimeError(f"Could not load patient-medications: {data}")
    return data


@st.cache_data(ttl=5)
def load_medications() -> list[dict[str, Any]]:
    """Load all medications from API."""
    status, data = request_json("GET", "/medications")
    if status != 200:
        raise RuntimeError(f"Could not load medications: {data}")
    return data


@st.cache_data(ttl=5)
def load_antibiotics() -> list[dict[str, Any]]:
    """Load all antibiotics from API."""
    status, data = request_json("GET", "/antibiotics")
    if status != 200:
        raise RuntimeError(f"Could not load antibiotics: {data}")
    return data


@st.cache_data(ttl=5)
def load_provenance_destinations() -> list[dict[str, Any]]:
    """Load all provenance_destination rows from API."""
    status, data = request_json("GET", "/provenance-destinations")
    if status != 200:
        raise RuntimeError(f"Could not load provenance destinations: {data}")
    return data


@st.cache_data(ttl=5)
def load_burn_etiologies() -> list[dict[str, Any]]:
    """Load all burn_etiology rows from API."""
    status, data = request_json("GET", "/burn-etiologies")
    if status != 200:
        raise RuntimeError(f"Could not load burn etiologies: {data}")
    return data


@st.cache_data(ttl=5)
def load_inhalation_injuries() -> list[dict[str, Any]]:
    """Load all inhalation_injury rows from API."""
    status, data = request_json("GET", "/inhalation-injuries")
    if status != 200:
        raise RuntimeError(f"Could not load inhalation injuries: {data}")
    return data


@st.cache_data(ttl=5)
def load_burn_unit_cases() -> list[dict[str, Any]]:
    """Load all burn_unit_cases rows from API."""
    status, data = request_json("GET", "/burn-unit-cases")
    if status != 200:
        raise RuntimeError(f"Could not load burn unit cases: {data}")
    return data


def birth_date_text(value: Any) -> str:
    """Return birth date as ISO text for text-input fields."""
    if not value:
        return ""
    return str(value)


def parse_birth_date_input(value: str) -> str | None:
    """Validate YYYY-MM-DD input and return canonical ISO date text or None."""
    clean = value.strip()
    if not clean:
        return None
    parsed = datetime.strptime(clean, "%Y-%m-%d").date()
    return parsed.isoformat()


def parse_optional_float_input(value: str) -> float | None:
    """Validate optional float input and return float value or None."""
    clean = value.strip()
    if not clean:
        return None
    return float(clean)


def parse_optional_date_input(value: str) -> str | None:
    """Validate optional date input in YYYY-MM-DD format."""
    clean = value.strip()
    if not clean:
        return None
    return parse_birth_date_input(clean)


def address_options(addresses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build address options including empty choice."""
    options = [{"id": None, "label": "No address"}]
    for item in addresses:
        options.append(
            {
                "id": item.get("id"),
                "label": f"{item.get('municipio', 'Unknown municipio')} (id: {item.get('id')})",
            }
        )
    return options


def patient_label(patient: dict[str, Any]) -> str:
    """Build human-readable patient label for selectors."""
    return f"{patient.get('id')} - {patient.get('name')}"


def address_option_index(addr_opts: list[dict[str, Any]], address_id: int | None) -> int:
    """Resolve selected address option index from existing patient data."""
    for idx, option in enumerate(addr_opts):
        if option["id"] == address_id:
            return idx
    return 0


def pathology_label(pathology: dict[str, Any]) -> str:
    """Build human-readable pathology label for selectors."""
    return f"{pathology.get('id')} - {pathology.get('name')}"


def medication_label(medication: dict[str, Any]) -> str:
    """Build human-readable medication label for selectors."""
    atc_code = medication.get("atc_code") or "-"
    return f"{medication.get('id')} - {medication.get('name')} (ATC: {atc_code})"


def antibiotic_label(antibiotic: dict[str, Any]) -> str:
    """Build human-readable antibiotic label for selectors."""
    atc_code = antibiotic.get("atc_code") or "-"
    return f"{antibiotic.get('id')} - {antibiotic.get('name')} (ATC: {atc_code})"


def provenance_destination_label(item: dict[str, Any]) -> str:
    """Build human-readable provenance/destination label for selectors."""
    type_value = item.get("type") or "-"
    location_value = item.get("location") if item.get("location") is not None else "-"
    return f"{item.get('id')} - {item.get('name')} (type: {type_value}, location: {location_value})"


def burn_etiology_label(item: dict[str, Any]) -> str:
    """Build human-readable burn etiology label for selectors."""
    return f"{item.get('id')} - {item.get('name')}"


def inhalation_injury_label(item: dict[str, Any]) -> str:
    """Build human-readable inhalation injury label for selectors."""
    return f"{item.get('id')} - {item.get('name')}"


def burn_unit_case_label(case_row: dict[str, Any], patients_by_id: dict[int, dict[str, Any]]) -> str:
    """Build human-readable burn unit case label for selectors."""
    patient_id = case_row.get("patient_id")
    patient_name = patients_by_id.get(patient_id, {}).get("name", "Unknown patient")
    tbsa_value = case_row.get("TBSA_burned")
    tbsa_text = f"{tbsa_value}%" if tbsa_value is not None else "-"
    return f"case {case_row.get('id')} | patient {patient_id} ({patient_name}) | TBSA {tbsa_text}"


def normalize_optional_bool(value: Any) -> bool | None:
    """Normalize sqlite booleans represented as bool/int/None to bool/None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return None


def optional_text(value: str) -> str | None:
    """Normalize optional string input by mapping empty values to None."""
    clean = value.strip()
    return clean if clean else None


def show_api_result(status: int, data: Any) -> None:
    """Display API request result in a concise way."""
    if 200 <= status < 300:
        st.success(f"Success ({status})")
        st.json(data)
    else:
        st.error(f"Request failed ({status})")
        st.json(data)


def refresh_data() -> None:
    """Clear cached API data and rerun for immediate UI update."""
    load_patients.clear()
    load_addresses.clear()
    load_pathologies.clear()
    load_patient_pathologies.clear()
    load_patient_medications.clear()
    load_medications.clear()
    load_antibiotics.clear()
    load_provenance_destinations.clear()
    load_burn_etiologies.clear()
    load_inhalation_injuries.clear()
    load_burn_unit_cases.clear()
    load_infections.clear()
    load_case_infections.clear()
    load_case_antibiotics.clear()
    load_case_procedures.clear()
    load_case_surgical_interventions.clear()
    load_case_complications.clear()
    load_case_microbiology.clear()
    load_medical_procedures.clear()
    load_surgical_interventions.clear()
    load_complications.clear()
    load_microbiology_specimens.clear()
    load_microbiology_agents.clear()
    st.rerun()


def find_index_by_key(rows: list[dict[str, Any]], key: str, value: Any) -> int:
    """Resolve selected option index from a list of dictionaries and key/value."""
    for idx, row in enumerate(rows):
        if row.get(key) == value:
            return idx
    return 0


def render_overview(patients: list[dict[str, Any]], addresses: list[dict[str, Any]]) -> None:
    """Render compact overview and patient list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Patients: {len(patients)}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='ui-badge'>Addresses: {len(addresses)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Patients")
    if patients:
        st.dataframe(patients, width="stretch", hide_index=True)
    else:
        st.info("No patients available yet.")
    card_close()


def render_create_tab(addr_opts: list[dict[str, Any]]) -> None:
    """Render create patient operation."""
    with st.form("create_patient_form"):
        patient_id = st.number_input("Patient ID", min_value=1, step=1, format="%d")
        name = st.text_input("Name", placeholder="Patient full name")
        birth_date = st.text_input("Birth date (YYYY-MM-DD)", placeholder="e.g. 1985-07-23")
        gender = st.selectbox("Gender", options=ALLOWED_GENDERS)
        address = st.selectbox(
            "Address (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            key="create_address_select",
        )
        submitted = st.form_submit_button("Create patient", width="stretch")

        if submitted:
            try:
                birth_date_value = parse_birth_date_input(birth_date)
            except ValueError:
                st.error("Birth date must use format YYYY-MM-DD.")
                return

            payload = {
                "id": int(patient_id),
                "name": name.strip(),
                "birth_date": birth_date_value,
                "gender": gender,
                "address": address["id"],
            }
            status, data = request_json("POST", "/patients", payload)
            show_api_result(status, data)
            if 200 <= status < 300:
                refresh_data()


def render_read_tab(patients: list[dict[str, Any]]) -> None:
    """Render read single patient operation."""
    if not patients:
        st.info("Create at least one patient to use this operation.")
        return

    selected = st.selectbox(
        "Select patient",
        options=patients,
        format_func=patient_label,
        key="read_patient_select",
    )
    if st.button("Fetch patient", width="stretch"):
        status, data = request_json("GET", f"/patients/{selected['id']}")
        show_api_result(status, data)


def render_put_tab(patients: list[dict[str, Any]], addr_opts: list[dict[str, Any]]) -> None:
    """Render full replace operation."""
    if not patients:
        st.info("Create at least one patient to use this operation.")
        return

    selected = st.selectbox(
        "Patient to replace",
        options=patients,
        format_func=patient_label,
        key="put_patient_select",
    )

    with st.form("put_patient_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        birth = st.text_input(
            "Birth date (YYYY-MM-DD)",
            value=birth_date_text(selected.get("birth_date")),
        )
        gender = st.selectbox(
            "Gender",
            options=ALLOWED_GENDERS,
            index=ALLOWED_GENDERS.index(selected.get("gender")) if selected.get("gender") in ALLOWED_GENDERS else 0,
        )
        address = st.selectbox(
            "Address (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            index=address_option_index(addr_opts, selected.get("address")),
            key="put_address_select",
        )
        submitted = st.form_submit_button("Replace patient", width="stretch")

        if submitted:
            try:
                birth_value = parse_birth_date_input(birth)
            except ValueError:
                st.error("Birth date must use format YYYY-MM-DD.")
                return

            payload = {
                "name": name.strip(),
                "birth_date": birth_value,
                "gender": gender,
                "address": address["id"],
            }
            status, data = request_json("PUT", f"/patients/{selected['id']}", payload)
            show_api_result(status, data)
            if 200 <= status < 300:
                refresh_data()


def render_patch_tab(patients: list[dict[str, Any]], addr_opts: list[dict[str, Any]]) -> None:
    """Render partial update operation."""
    if not patients:
        st.info("Create at least one patient to use this operation.")
        return

    selected = st.selectbox(
        "Patient to patch",
        options=patients,
        format_func=patient_label,
        key="patch_patient_select",
    )
    selected_patient_id = int(selected.get("id"))

    with st.form("patch_patient_form"):
        use_name = st.checkbox("Update name", key=f"patch_patient_use_name_{selected_patient_id}")
        patch_name = st.text_input(
            "Name",
            value=str(selected.get("name", "")),
            key=f"patch_patient_name_{selected_patient_id}",
        )

        use_birth = st.checkbox("Update birth date", key=f"patch_patient_use_birth_{selected_patient_id}")
        patch_birth = st.text_input(
            "Birth date (YYYY-MM-DD)",
            value=birth_date_text(selected.get("birth_date")),
            key=f"patch_birth_date_{selected_patient_id}",
        )

        use_gender = st.checkbox("Update gender", key=f"patch_patient_use_gender_{selected_patient_id}")
        patch_gender = st.selectbox(
            "Gender",
            options=ALLOWED_GENDERS,
            index=ALLOWED_GENDERS.index(selected.get("gender")) if selected.get("gender") in ALLOWED_GENDERS else 0,
            key=f"patch_gender_{selected_patient_id}",
        )

        use_address = st.checkbox("Update address", key=f"patch_patient_use_address_{selected_patient_id}")
        patch_address = st.selectbox(
            "Address (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            index=address_option_index(addr_opts, selected.get("address")),
            key=f"patch_address_select_{selected_patient_id}",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_name:
                payload["name"] = patch_name.strip()
            if use_birth:
                try:
                    payload["birth_date"] = parse_birth_date_input(patch_birth)
                except ValueError:
                    st.error("Birth date must use format YYYY-MM-DD.")
                    return
            if use_gender:
                payload["gender"] = patch_gender
            if use_address:
                payload["address"] = patch_address["id"]

            if not payload:
                st.warning("Select at least one field to patch.")
                return

            status, data = request_json("PATCH", f"/patients/{selected['id']}", payload)
            show_api_result(status, data)
            if 200 <= status < 300:
                refresh_data()


def render_delete_tab(patients: list[dict[str, Any]]) -> None:
    """Render delete operation."""
    if not patients:
        st.info("Create at least one patient to use this operation.")
        return

    selected = st.selectbox(
        "Patient to delete",
        options=patients,
        format_func=patient_label,
        key="delete_patient_select",
    )
    confirm_delete = st.checkbox("I understand this action cannot be undone")
    if st.button("Delete patient", type="primary", disabled=not confirm_delete, width="stretch"):
        status, data = request_json("DELETE", f"/patients/{selected['id']}")
        show_api_result(status, data)
        if 200 <= status < 300:
            refresh_data()


def render_crud_workspace(patients: list[dict[str, Any]], addr_opts: list[dict[str, Any]]) -> None:
    """Render all CRUD operations in compact tabs."""
    card_open()
    section_title("CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_create_tab(addr_opts)
    with op_tabs[1]:
        render_read_tab(patients)
    with op_tabs[2]:
        render_put_tab(patients, addr_opts)
    with op_tabs[3]:
        render_patch_tab(patients, addr_opts)
    with op_tabs[4]:
        render_delete_tab(patients)

    card_close()


def patients_tab() -> None:
    """Render patients management UI."""
    st.subheader("Patients Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        patients = load_patients()
        addresses = load_addresses()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_overview(patients, addresses)
    render_crud_workspace(patients, address_options(addresses))


def render_pathologies_overview(pathologies: list[dict[str, Any]]) -> None:
    """Render compact overview and pathology list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Pathologies: {len(pathologies)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_pathologies"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Pathologies")
    if pathologies:
        st.dataframe(pathologies, width="stretch", hide_index=True)
    else:
        st.info("No pathologies available yet.")
    card_close()


def render_pathology_create_tab() -> None:
    """Render create pathology operation."""
    with st.form("create_pathology_form"):
        pathology_id = st.number_input("Pathology ID", min_value=1, step=1, format="%d")
        name = st.text_input("Name", placeholder="Pathology preferred term")
        fsn = st.text_input("FSN", placeholder="Fully specified name")
        semantic_tag = st.text_input("Semantic tag", placeholder="e.g. disorder")
        definition = st.text_area("Definition", placeholder="Clinical description")
        icd11_code = st.text_input("ICD-11 code", placeholder="Optional ICD-11 code")
        mesh_id = st.text_input("MeSH ID", placeholder="Optional MeSH id")
        status = st.selectbox("Status", options=ALLOWED_PATHOLOGY_STATUSES)
        submitted = st.form_submit_button("Create pathology", width="stretch")

        if submitted:
            payload = {
                "id": int(pathology_id),
                "name": name.strip(),
                "fsn": optional_text(fsn),
                "semantic_tag": optional_text(semantic_tag),
                "definition": optional_text(definition),
                "icd11_code": optional_text(icd11_code),
                "mesh_id": optional_text(mesh_id),
                "status": status,
            }
            status_code, data = request_json("POST", "/pathologies", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_pathology_read_tab(pathologies: list[dict[str, Any]]) -> None:
    """Render read single pathology operation."""
    if not pathologies:
        st.info("Create at least one pathology to use this operation.")
        return

    selected = st.selectbox(
        "Select pathology",
        options=pathologies,
        format_func=pathology_label,
        key="read_pathology_select",
    )
    if st.button("Fetch pathology", width="stretch"):
        status_code, data = request_json("GET", f"/pathologies/{selected['id']}")
        show_api_result(status_code, data)


def render_pathology_put_tab(pathologies: list[dict[str, Any]]) -> None:
    """Render full replace pathology operation."""
    if not pathologies:
        st.info("Create at least one pathology to use this operation.")
        return

    selected = st.selectbox(
        "Pathology to replace",
        options=pathologies,
        format_func=pathology_label,
        key="put_pathology_select",
    )

    with st.form("put_pathology_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        fsn = st.text_input("FSN", value=str(selected.get("fsn") or ""))
        semantic_tag = st.text_input("Semantic tag", value=str(selected.get("semantic_tag") or ""))
        definition = st.text_area("Definition", value=str(selected.get("definition") or ""))
        icd11_code = st.text_input("ICD-11 code", value=str(selected.get("icd11_code") or ""))
        mesh_id = st.text_input("MeSH ID", value=str(selected.get("mesh_id") or ""))
        current_status = selected.get("status")
        status = st.selectbox(
            "Status",
            options=ALLOWED_PATHOLOGY_STATUSES,
            index=ALLOWED_PATHOLOGY_STATUSES.index(current_status)
            if current_status in ALLOWED_PATHOLOGY_STATUSES
            else 0,
        )
        submitted = st.form_submit_button("Replace pathology", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "fsn": optional_text(fsn),
                "semantic_tag": optional_text(semantic_tag),
                "definition": optional_text(definition),
                "icd11_code": optional_text(icd11_code),
                "mesh_id": optional_text(mesh_id),
                "status": status,
            }
            status_code, data = request_json("PUT", f"/pathologies/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_pathology_patch_tab(pathologies: list[dict[str, Any]]) -> None:
    """Render partial update pathology operation."""
    if not pathologies:
        st.info("Create at least one pathology to use this operation.")
        return

    selected = st.selectbox(
        "Pathology to patch",
        options=pathologies,
        format_func=pathology_label,
        key="patch_pathology_select",
    )

    with st.form("patch_pathology_form"):
        use_name = st.checkbox("Update name", key="patch_pathology_use_name")
        patch_name = st.text_input("Name", value=str(selected.get("name", "")), key="patch_pathology_name")

        use_fsn = st.checkbox("Update FSN", key="patch_pathology_use_fsn")
        patch_fsn = st.text_input("FSN", value=str(selected.get("fsn") or ""), key="patch_pathology_fsn")

        use_semantic_tag = st.checkbox("Update semantic tag", key="patch_pathology_use_semantic_tag")
        patch_semantic_tag = st.text_input(
            "Semantic tag",
            value=str(selected.get("semantic_tag") or ""),
            key="patch_pathology_semantic_tag",
        )

        use_definition = st.checkbox("Update definition", key="patch_pathology_use_definition")
        patch_definition = st.text_area(
            "Definition",
            value=str(selected.get("definition") or ""),
            key="patch_pathology_definition",
        )

        use_icd11 = st.checkbox("Update ICD-11 code", key="patch_pathology_use_icd11")
        patch_icd11_code = st.text_input(
            "ICD-11 code",
            value=str(selected.get("icd11_code") or ""),
            key="patch_pathology_icd11_code",
        )

        use_mesh = st.checkbox("Update MeSH ID", key="patch_pathology_use_mesh")
        patch_mesh_id = st.text_input(
            "MeSH ID",
            value=str(selected.get("mesh_id") or ""),
            key="patch_pathology_mesh_id",
        )

        use_status = st.checkbox("Update status", key="patch_pathology_use_status")
        current_status = selected.get("status")
        patch_status = st.selectbox(
            "Status",
            options=ALLOWED_PATHOLOGY_STATUSES,
            index=ALLOWED_PATHOLOGY_STATUSES.index(current_status)
            if current_status in ALLOWED_PATHOLOGY_STATUSES
            else 0,
            key="patch_pathology_status",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_name:
                payload["name"] = patch_name.strip()
            if use_fsn:
                payload["fsn"] = optional_text(patch_fsn)
            if use_semantic_tag:
                payload["semantic_tag"] = optional_text(patch_semantic_tag)
            if use_definition:
                payload["definition"] = optional_text(patch_definition)
            if use_icd11:
                payload["icd11_code"] = optional_text(patch_icd11_code)
            if use_mesh:
                payload["mesh_id"] = optional_text(patch_mesh_id)
            if use_status:
                payload["status"] = patch_status

            status_code, data = request_json("PATCH", f"/pathologies/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_pathology_delete_tab(pathologies: list[dict[str, Any]]) -> None:
    """Render delete pathology operation."""
    if not pathologies:
        st.info("Create at least one pathology to use this operation.")
        return

    selected = st.selectbox(
        "Pathology to delete",
        options=pathologies,
        format_func=pathology_label,
        key="delete_pathology_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_pathology_confirm",
    )
    if st.button("Delete pathology", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/pathologies/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_pathology_crud_workspace(pathologies: list[dict[str, Any]]) -> None:
    """Render pathology CRUD operations in compact tabs."""
    card_open()
    section_title("Pathologies CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_pathology_create_tab()
    with op_tabs[1]:
        render_pathology_read_tab(pathologies)
    with op_tabs[2]:
        render_pathology_put_tab(pathologies)
    with op_tabs[3]:
        render_pathology_patch_tab(pathologies)
    with op_tabs[4]:
        render_pathology_delete_tab(pathologies)

    card_close()


def pathologies_tab() -> None:
    """Render pathologies management UI."""
    st.subheader("Pathologies Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        pathologies = load_pathologies()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_pathologies_overview(pathologies)
    render_pathology_crud_workspace(pathologies)


def render_medications_overview(medications: list[dict[str, Any]]) -> None:
    """Render compact overview and medication list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Medications: {len(medications)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_medications"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Medications")
    if medications:
        st.dataframe(medications, width="stretch", hide_index=True)
    else:
        st.info("No medications available yet.")
    card_close()


def render_medication_create_tab() -> None:
    """Render create medication operation."""
    with st.form("create_medication_form"):
        name = st.text_input("Name", placeholder="Medication name")
        atc_code = st.text_input("ATC code", placeholder="Unique ATC code")
        description = st.text_area("Description", placeholder="Optional description")
        submitted = st.form_submit_button("Create medication", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "atc_code": optional_text(atc_code),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/medications", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_medication_read_tab(medications: list[dict[str, Any]]) -> None:
    """Render read single medication operation."""
    if not medications:
        st.info("Create at least one medication to use this operation.")
        return

    selected = st.selectbox(
        "Select medication",
        options=medications,
        format_func=medication_label,
        key="read_medication_select",
    )
    if st.button("Fetch medication", width="stretch"):
        status_code, data = request_json("GET", f"/medications/{selected['id']}")
        show_api_result(status_code, data)


def render_medication_put_tab(medications: list[dict[str, Any]]) -> None:
    """Render full replace medication operation."""
    if not medications:
        st.info("Create at least one medication to use this operation.")
        return

    selected = st.selectbox(
        "Medication to replace",
        options=medications,
        format_func=medication_label,
        key="put_medication_select",
    )

    with st.form("put_medication_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        atc_code = st.text_input("ATC code", value=str(selected.get("atc_code") or ""))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace medication", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "atc_code": optional_text(atc_code),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/medications/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_medication_patch_tab(medications: list[dict[str, Any]]) -> None:
    """Render partial update medication operation."""
    if not medications:
        st.info("Create at least one medication to use this operation.")
        return

    selected = st.selectbox(
        "Medication to patch",
        options=medications,
        format_func=medication_label,
        key="patch_medication_select",
    )

    with st.form("patch_medication_form"):
        use_name = st.checkbox("Update name", key="patch_medication_use_name")
        patch_name = st.text_input("Name", value=str(selected.get("name", "")), key="patch_medication_name")

        use_atc_code = st.checkbox("Update ATC code", key="patch_medication_use_atc_code")
        patch_atc_code = st.text_input(
            "ATC code",
            value=str(selected.get("atc_code") or ""),
            key="patch_medication_atc_code",
        )

        use_description = st.checkbox("Update description", key="patch_medication_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_medication_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_name:
                payload["name"] = patch_name.strip()
            if use_atc_code:
                payload["atc_code"] = optional_text(patch_atc_code)
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/medications/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_medication_delete_tab(medications: list[dict[str, Any]]) -> None:
    """Render delete medication operation."""
    if not medications:
        st.info("Create at least one medication to use this operation.")
        return

    selected = st.selectbox(
        "Medication to delete",
        options=medications,
        format_func=medication_label,
        key="delete_medication_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_medication_confirm",
    )
    if st.button("Delete medication", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/medications/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_medication_crud_workspace(medications: list[dict[str, Any]]) -> None:
    """Render medication CRUD operations in compact tabs."""
    card_open()
    section_title("Medications CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_medication_create_tab()
    with op_tabs[1]:
        render_medication_read_tab(medications)
    with op_tabs[2]:
        render_medication_put_tab(medications)
    with op_tabs[3]:
        render_medication_patch_tab(medications)
    with op_tabs[4]:
        render_medication_delete_tab(medications)

    card_close()


def medications_tab() -> None:
    """Render medications management UI."""
    st.subheader("Medications Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        medications = load_medications()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_medications_overview(medications)
    render_medication_crud_workspace(medications)


def render_antibiotics_overview(antibiotics: list[dict[str, Any]]) -> None:
    """Render compact overview and antibiotic list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Antibiotics: {len(antibiotics)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_antibiotics"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Antibiotics")
    if antibiotics:
        st.dataframe(antibiotics, width="stretch", hide_index=True)
    else:
        st.info("No antibiotics available yet.")
    card_close()


def render_antibiotic_create_tab() -> None:
    """Render create antibiotic operation."""
    with st.form("create_antibiotic_form"):
        name = st.text_input("Name", placeholder="Antibiotic name")
        atc_code = st.text_input("ATC code", placeholder="ATC code")
        description = st.text_area("Description", placeholder="Optional description")
        submitted = st.form_submit_button("Create antibiotic", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "atc_code": atc_code.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/antibiotics", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_antibiotic_read_tab(antibiotics: list[dict[str, Any]]) -> None:
    """Render read single antibiotic operation."""
    if not antibiotics:
        st.info("Create at least one antibiotic to use this operation.")
        return

    selected = st.selectbox(
        "Select antibiotic",
        options=antibiotics,
        format_func=antibiotic_label,
        key="read_antibiotic_select",
    )
    if st.button("Fetch antibiotic", width="stretch"):
        status_code, data = request_json("GET", f"/antibiotics/{selected['id']}")
        show_api_result(status_code, data)


def render_antibiotic_put_tab(antibiotics: list[dict[str, Any]]) -> None:
    """Render full replace antibiotic operation."""
    if not antibiotics:
        st.info("Create at least one antibiotic to use this operation.")
        return

    selected = st.selectbox(
        "Antibiotic to replace",
        options=antibiotics,
        format_func=antibiotic_label,
        key="put_antibiotic_select",
    )

    with st.form("put_antibiotic_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        atc_code = st.text_input("ATC code", value=str(selected.get("atc_code") or ""))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace antibiotic", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "atc_code": atc_code.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/antibiotics/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_antibiotic_patch_tab(antibiotics: list[dict[str, Any]]) -> None:
    """Render partial update antibiotic operation."""
    if not antibiotics:
        st.info("Create at least one antibiotic to use this operation.")
        return

    selected = st.selectbox(
        "Antibiotic to patch",
        options=antibiotics,
        format_func=antibiotic_label,
        key="patch_antibiotic_select",
    )

    with st.form("patch_antibiotic_form"):
        use_name = st.checkbox("Update name", key="patch_antibiotic_use_name")
        patch_name = st.text_input("Name", value=str(selected.get("name", "")), key="patch_antibiotic_name")

        use_atc_code = st.checkbox("Update ATC code", key="patch_antibiotic_use_atc_code")
        patch_atc_code = st.text_input(
            "ATC code",
            value=str(selected.get("atc_code") or ""),
            key="patch_antibiotic_atc_code",
        )

        use_description = st.checkbox("Update description", key="patch_antibiotic_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_antibiotic_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_name:
                payload["name"] = patch_name.strip()
            if use_atc_code:
                payload["atc_code"] = patch_atc_code.strip()
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/antibiotics/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_antibiotic_delete_tab(antibiotics: list[dict[str, Any]]) -> None:
    """Render delete antibiotic operation."""
    if not antibiotics:
        st.info("Create at least one antibiotic to use this operation.")
        return

    selected = st.selectbox(
        "Antibiotic to delete",
        options=antibiotics,
        format_func=antibiotic_label,
        key="delete_antibiotic_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_antibiotic_confirm",
    )
    if st.button("Delete antibiotic", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/antibiotics/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_antibiotic_crud_workspace(antibiotics: list[dict[str, Any]]) -> None:
    """Render antibiotic CRUD operations in compact tabs."""
    card_open()
    section_title("Antibiotics CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_antibiotic_create_tab()
    with op_tabs[1]:
        render_antibiotic_read_tab(antibiotics)
    with op_tabs[2]:
        render_antibiotic_put_tab(antibiotics)
    with op_tabs[3]:
        render_antibiotic_patch_tab(antibiotics)
    with op_tabs[4]:
        render_antibiotic_delete_tab(antibiotics)

    card_close()


def antibiotics_tab() -> None:
    """Render antibiotics management UI."""
    st.subheader("Antibiotics Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        antibiotics = load_antibiotics()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_antibiotics_overview(antibiotics)
    render_antibiotic_crud_workspace(antibiotics)


def render_provenance_destinations_overview(
    provenance_destinations: list[dict[str, Any]],
    addresses: list[dict[str, Any]],
) -> None:
    """Render compact overview and provenance destination list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(
            f"<span class='ui-badge'>Provenance/Destination rows: {len(provenance_destinations)}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<span class='ui-badge'>Addresses: {len(addresses)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_provenance_destinations"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Provenance/Destination Rows")
    if provenance_destinations:
        st.dataframe(provenance_destinations, width="stretch", hide_index=True)
    else:
        st.info("No provenance/destination rows available yet.")
    card_close()


def render_provenance_destination_create_tab(addr_opts: list[dict[str, Any]]) -> None:
    """Render create provenance destination operation."""
    type_options: list[str | None] = [None, *ALLOWED_PROVENANCE_TYPES]

    with st.form("create_provenance_destination_form"):
        name = st.text_input("Name", placeholder="Provenance or destination name")
        type_value = st.selectbox(
            "Type",
            options=type_options,
            format_func=lambda value: "No type" if value is None else value,
        )
        location = st.selectbox(
            "Location (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            key="create_provenance_destination_location",
        )
        submitted = st.form_submit_button("Create provenance/destination", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "type": type_value,
                "location": location["id"],
            }
            status_code, data = request_json("POST", "/provenance-destinations", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_provenance_destination_read_tab(provenance_destinations: list[dict[str, Any]]) -> None:
    """Render read single provenance destination operation."""
    if not provenance_destinations:
        st.info("Create at least one provenance/destination row to use this operation.")
        return

    selected = st.selectbox(
        "Select provenance/destination",
        options=provenance_destinations,
        format_func=provenance_destination_label,
        key="read_provenance_destination_select",
    )
    if st.button("Fetch provenance/destination", width="stretch", key="read_provenance_destination_button"):
        status_code, data = request_json("GET", f"/provenance-destinations/{selected['id']}")
        show_api_result(status_code, data)


def render_provenance_destination_put_tab(
    provenance_destinations: list[dict[str, Any]],
    addr_opts: list[dict[str, Any]],
) -> None:
    """Render full replace provenance destination operation."""
    if not provenance_destinations:
        st.info("Create at least one provenance/destination row to use this operation.")
        return

    type_options: list[str | None] = [None, *ALLOWED_PROVENANCE_TYPES]
    selected = st.selectbox(
        "Provenance/destination to replace",
        options=provenance_destinations,
        format_func=provenance_destination_label,
        key="put_provenance_destination_select",
    )

    with st.form("put_provenance_destination_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        type_value = st.selectbox(
            "Type",
            options=type_options,
            index=type_options.index(selected.get("type")) if selected.get("type") in type_options else 0,
            format_func=lambda value: "No type" if value is None else value,
            key="put_provenance_destination_type",
        )
        location = st.selectbox(
            "Location (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            index=address_option_index(addr_opts, selected.get("location")),
            key="put_provenance_destination_location",
        )
        submitted = st.form_submit_button("Replace provenance/destination", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "type": type_value,
                "location": location["id"],
            }
            status_code, data = request_json("PUT", f"/provenance-destinations/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_provenance_destination_patch_tab(
    provenance_destinations: list[dict[str, Any]],
    addr_opts: list[dict[str, Any]],
) -> None:
    """Render partial update provenance destination operation."""
    if not provenance_destinations:
        st.info("Create at least one provenance/destination row to use this operation.")
        return

    type_options: list[str | None] = [None, *ALLOWED_PROVENANCE_TYPES]
    selected = st.selectbox(
        "Provenance/destination to patch",
        options=provenance_destinations,
        format_func=provenance_destination_label,
        key="patch_provenance_destination_select",
    )

    with st.form("patch_provenance_destination_form"):
        use_name = st.checkbox("Update name", key="patch_provenance_destination_use_name")
        patch_name = st.text_input(
            "Name",
            value=str(selected.get("name", "")),
            key="patch_provenance_destination_name",
        )

        use_type = st.checkbox("Update type", key="patch_provenance_destination_use_type")
        patch_type = st.selectbox(
            "Type",
            options=type_options,
            index=type_options.index(selected.get("type")) if selected.get("type") in type_options else 0,
            format_func=lambda value: "No type" if value is None else value,
            key="patch_provenance_destination_type",
        )

        use_location = st.checkbox("Update location", key="patch_provenance_destination_use_location")
        patch_location = st.selectbox(
            "Location (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            index=address_option_index(addr_opts, selected.get("location")),
            key="patch_provenance_destination_location",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_name:
                payload["name"] = patch_name.strip()
            if use_type:
                payload["type"] = patch_type
            if use_location:
                payload["location"] = patch_location["id"]

            status_code, data = request_json("PATCH", f"/provenance-destinations/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_provenance_destination_delete_tab(provenance_destinations: list[dict[str, Any]]) -> None:
    """Render delete provenance destination operation."""
    if not provenance_destinations:
        st.info("Create at least one provenance/destination row to use this operation.")
        return

    selected = st.selectbox(
        "Provenance/destination to delete",
        options=provenance_destinations,
        format_func=provenance_destination_label,
        key="delete_provenance_destination_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_provenance_destination_confirm",
    )
    if st.button(
        "Delete provenance/destination",
        type="primary",
        disabled=not confirm_delete,
        width="stretch",
        key="delete_provenance_destination_button",
    ):
        status_code, data = request_json("DELETE", f"/provenance-destinations/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_provenance_destination_crud_workspace(
    provenance_destinations: list[dict[str, Any]],
    addr_opts: list[dict[str, Any]],
) -> None:
    """Render provenance destination CRUD operations in compact tabs."""
    card_open()
    section_title("Provenance/Destination CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_provenance_destination_create_tab(addr_opts)
    with op_tabs[1]:
        render_provenance_destination_read_tab(provenance_destinations)
    with op_tabs[2]:
        render_provenance_destination_put_tab(provenance_destinations, addr_opts)
    with op_tabs[3]:
        render_provenance_destination_patch_tab(provenance_destinations, addr_opts)
    with op_tabs[4]:
        render_provenance_destination_delete_tab(provenance_destinations)

    card_close()


def provenance_destinations_tab() -> None:
    """Render provenance destination management UI."""
    st.subheader("Provenance/Destination Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        provenance_destinations = load_provenance_destinations()
        addresses = load_addresses()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_provenance_destinations_overview(provenance_destinations, addresses)
    render_provenance_destination_crud_workspace(provenance_destinations, address_options(addresses))


def render_burn_etiologies_overview(burn_etiologies: list[dict[str, Any]]) -> None:
    """Render compact overview and burn etiology list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Burn etiologies: {len(burn_etiologies)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_burn_etiologies"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Burn Etiologies")
    if burn_etiologies:
        st.dataframe(burn_etiologies, width="stretch", hide_index=True)
    else:
        st.info("No burn etiologies available yet.")
    card_close()


def render_burn_etiology_create_tab() -> None:
    """Render create burn etiology operation."""
    with st.form("create_burn_etiology_form"):
        name = st.text_input("Name", placeholder="Burn etiology name")
        description = st.text_area("Description", placeholder="Optional description")
        submitted = st.form_submit_button("Create burn etiology", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/burn-etiologies", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_burn_etiology_read_tab(burn_etiologies: list[dict[str, Any]]) -> None:
    """Render read single burn etiology operation."""
    if not burn_etiologies:
        st.info("Create at least one burn etiology row to use this operation.")
        return

    selected = st.selectbox(
        "Select burn etiology",
        options=burn_etiologies,
        format_func=burn_etiology_label,
        key="read_burn_etiology_select",
    )
    if st.button("Fetch burn etiology", width="stretch", key="read_burn_etiology_button"):
        status_code, data = request_json("GET", f"/burn-etiologies/{selected['id']}")
        show_api_result(status_code, data)


def render_burn_etiology_put_tab(burn_etiologies: list[dict[str, Any]]) -> None:
    """Render full replace burn etiology operation."""
    if not burn_etiologies:
        st.info("Create at least one burn etiology row to use this operation.")
        return

    selected = st.selectbox(
        "Burn etiology to replace",
        options=burn_etiologies,
        format_func=burn_etiology_label,
        key="put_burn_etiology_select",
    )

    with st.form("put_burn_etiology_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace burn etiology", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/burn-etiologies/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_burn_etiology_patch_tab(burn_etiologies: list[dict[str, Any]]) -> None:
    """Render partial update burn etiology operation."""
    if not burn_etiologies:
        st.info("Create at least one burn etiology row to use this operation.")
        return

    selected = st.selectbox(
        "Burn etiology to patch",
        options=burn_etiologies,
        format_func=burn_etiology_label,
        key="patch_burn_etiology_select",
    )

    with st.form("patch_burn_etiology_form"):
        use_name = st.checkbox("Update name", key="patch_burn_etiology_use_name")
        patch_name = st.text_input("Name", value=str(selected.get("name", "")), key="patch_burn_etiology_name")

        use_description = st.checkbox("Update description", key="patch_burn_etiology_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_burn_etiology_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_name:
                payload["name"] = patch_name.strip()
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/burn-etiologies/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_burn_etiology_delete_tab(burn_etiologies: list[dict[str, Any]]) -> None:
    """Render delete burn etiology operation."""
    if not burn_etiologies:
        st.info("Create at least one burn etiology row to use this operation.")
        return

    selected = st.selectbox(
        "Burn etiology to delete",
        options=burn_etiologies,
        format_func=burn_etiology_label,
        key="delete_burn_etiology_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_burn_etiology_confirm",
    )
    if st.button(
        "Delete burn etiology",
        type="primary",
        disabled=not confirm_delete,
        width="stretch",
        key="delete_burn_etiology_button",
    ):
        status_code, data = request_json("DELETE", f"/burn-etiologies/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_burn_etiology_crud_workspace(burn_etiologies: list[dict[str, Any]]) -> None:
    """Render burn etiology CRUD operations in compact tabs."""
    card_open()
    section_title("Burn Etiology CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_burn_etiology_create_tab()
    with op_tabs[1]:
        render_burn_etiology_read_tab(burn_etiologies)
    with op_tabs[2]:
        render_burn_etiology_put_tab(burn_etiologies)
    with op_tabs[3]:
        render_burn_etiology_patch_tab(burn_etiologies)
    with op_tabs[4]:
        render_burn_etiology_delete_tab(burn_etiologies)

    card_close()


def burn_etiologies_tab() -> None:
    """Render burn etiology management UI."""
    st.subheader("Burn Etiologies Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        burn_etiologies = load_burn_etiologies()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_burn_etiologies_overview(burn_etiologies)
    render_burn_etiology_crud_workspace(burn_etiologies)


def render_burn_unit_cases_overview(
    burn_unit_cases: list[dict[str, Any]],
    patients: list[dict[str, Any]],
    provenance_destinations: list[dict[str, Any]],
    burn_etiologies: list[dict[str, Any]],
    inhalation_injuries: list[dict[str, Any]],
) -> None:
    """Render compact overview and burn unit case list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Burn unit cases: {len(burn_unit_cases)}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='ui-badge'>Patients: {len(patients)}</span>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='ui-badge'>Provenance/Destination rows: {len(provenance_destinations)}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<span class='ui-badge'>Burn etiologies: {len(burn_etiologies)}</span>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='ui-badge'>Inhalation injuries: {len(inhalation_injuries)}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_burn_unit_cases"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Burn Unit Cases")
    if burn_unit_cases:
        st.dataframe(burn_unit_cases, width="stretch", hide_index=True)
    else:
        st.info("No burn unit cases available yet.")
    card_close()


def render_burn_unit_case_create_tab(
    patients: list[dict[str, Any]],
    provenance_destinations: list[dict[str, Any]],
    burn_etiologies: list[dict[str, Any]],
    inhalation_injuries: list[dict[str, Any]],
) -> None:
    """Render create burn unit case operation."""
    if not patients:
        st.info("No patients available. Create patients first in the Patients tab.")
        return

    patient_options = [None] + sorted(patients, key=lambda row: int(row.get("id", 0)))
    provenance_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": provenance_destination_label(row)}
        for row in sorted(provenance_destinations, key=lambda item: int(item.get("id", 0)))
    ]
    burn_etiology_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": burn_etiology_label(row)}
        for row in sorted(burn_etiologies, key=lambda item: int(item.get("id", 0)))
    ]
    inhalation_injury_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": inhalation_injury_label(row)}
        for row in sorted(inhalation_injuries, key=lambda item: int(item.get("id", 0)))
    ]
    optional_bool_options = ["Not set", "Yes", "No"]
    optional_bool_map: dict[str, bool | None] = {"Not set": None, "Yes": True, "No": False}

    with st.form("create_burn_unit_case_form", clear_on_submit=True):
        case_id = st.text_input("Case ID", placeholder="Required integer")
        patient = st.selectbox(
            "Patient",
            options=patient_options,
            format_func=lambda row: "Select patient" if row is None else patient_label(row),
            key="create_burn_case_patient",
        )
        tbsa_burned = st.text_input("TBSA burned (%)", placeholder="Optional numeric value")
        admission_date = st.text_input("Admission date (YYYY-MM-DD)", placeholder="Optional")
        burn_date = st.text_input("Burn date (YYYY-MM-DD)", placeholder="Optional")
        release_date = st.text_input("Release date (YYYY-MM-DD)", placeholder="Optional")
        admission_provenance = st.selectbox(
            "Admission provenance",
            options=provenance_options,
            format_func=lambda option: option["label"],
            key="create_burn_case_admission_provenance",
        )
        release_destination = st.selectbox(
            "Release destination",
            options=provenance_options,
            format_func=lambda option: option["label"],
            key="create_burn_case_release_destination",
        )
        burn_mecanism = st.selectbox(
            "Burn mecanism",
            options=[None, *ALLOWED_BURN_MECANISMS],
            format_func=lambda value: "Not set" if value is None else value,
            key="create_burn_case_mecanism",
        )
        burn_etiology = st.selectbox(
            "Burn etiology",
            options=burn_etiology_options,
            format_func=lambda option: option["label"],
            key="create_burn_case_etiology",
        )
        inhalation_injury = st.selectbox(
            "Inhalation injury",
            options=inhalation_injury_options,
            format_func=lambda option: option["label"],
            key="create_burn_case_inhalation_injury",
        )
        violence_related_label = st.radio(
            "Violence related",
            options=optional_bool_options,
            index=0,
            horizontal=True,
            key="create_burn_case_violence",
        )
        suicide_attempt_label = st.radio(
            "Suicide attempt",
            options=optional_bool_options,
            index=0,
            horizontal=True,
            key="create_burn_case_suicide",
        )
        accident_type = st.selectbox(
            "Accident type",
            options=[None, *ALLOWED_ACCIDENT_TYPES],
            format_func=lambda value: "Not set" if value is None else value,
            key="create_burn_case_accident_type",
        )
        wildfire_label = st.radio(
            "Wildfire",
            options=optional_bool_options,
            index=0,
            horizontal=True,
            key="create_burn_case_wildfire",
        )
        bonfire_fogueira_label = st.radio(
            "Bonfire/Fogueira",
            options=optional_bool_options,
            index=0,
            horizontal=True,
            key="create_burn_case_bonfire",
        )
        fireplace_lareira_label = st.radio(
            "Fireplace/Lareira",
            options=optional_bool_options,
            index=0,
            horizontal=True,
            key="create_burn_case_fireplace",
        )
        note = st.text_area("Note", placeholder="Optional note")
        special_forces = st.selectbox(
            "Special forces",
            options=[None, *ALLOWED_SPECIAL_FORCES],
            format_func=lambda value: "Not set" if value is None else value,
            key="create_burn_case_special_forces",
        )
        submitted = st.form_submit_button("Create burn unit case", width="stretch")

        if submitted:
            violence_related = optional_bool_map[violence_related_label]
            suicide_attempt = optional_bool_map[suicide_attempt_label]
            wildfire = optional_bool_map[wildfire_label]
            bonfire_fogueira = optional_bool_map[bonfire_fogueira_label]
            fireplace_lareira = optional_bool_map[fireplace_lareira_label]

            if not case_id.strip():
                st.error("Case ID is required.")
                return
            if patient is None:
                st.error("Patient is required.")
                return

            try:
                payload = {
                    "id": int(case_id.strip()),
                    "patient_id": int(patient["id"]),
                    "TBSA_burned": parse_optional_float_input(tbsa_burned),
                    "admission_date": parse_optional_date_input(admission_date),
                    "burn_date": parse_optional_date_input(burn_date),
                    "release_date": parse_optional_date_input(release_date),
                    "admission_provenance": admission_provenance["id"],
                    "release_destination": release_destination["id"],
                    "burn_mecanism": burn_mecanism,
                    "burn_etiology": burn_etiology["id"],
                    "inhalation_injury": inhalation_injury["id"],
                    "violence_related": violence_related,
                    "suicide_attempt": suicide_attempt,
                    "accident_type": accident_type,
                    "wildfire": wildfire,
                    "bonfire_fogueira": bonfire_fogueira,
                    "fireplace_lareira": fireplace_lareira,
                    "note": optional_text(note),
                    "special_forces": special_forces,
                }
            except ValueError:
                st.error("TBSA burned must be a valid number and dates must use YYYY-MM-DD format.")
                return

            status_code, data = request_json("POST", "/burn-unit-cases", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_burn_unit_case_read_tab(
    burn_unit_cases: list[dict[str, Any]],
    patients_by_id: dict[int, dict[str, Any]],
) -> None:
    """Render read single burn unit case operation."""
    if not burn_unit_cases:
        st.info("Create at least one burn unit case to use this operation.")
        return

    selected = st.selectbox(
        "Select burn unit case",
        options=burn_unit_cases,
        format_func=lambda row: burn_unit_case_label(row, patients_by_id),
        key="read_burn_unit_case_select",
    )
    if st.button("Fetch burn unit case", width="stretch", key="read_burn_unit_case_button"):
        status_code, data = request_json("GET", f"/burn-unit-cases/{selected['id']}")
        show_api_result(status_code, data)


def render_burn_unit_case_put_tab(
    burn_unit_cases: list[dict[str, Any]],
    patients: list[dict[str, Any]],
    provenance_destinations: list[dict[str, Any]],
    burn_etiologies: list[dict[str, Any]],
    inhalation_injuries: list[dict[str, Any]],
    patients_by_id: dict[int, dict[str, Any]],
) -> None:
    """Render full replace burn unit case operation."""
    if not burn_unit_cases:
        st.info("Create at least one burn unit case to use this operation.")
        return
    if not patients:
        st.info("No patients available. Create patients first in the Patients tab.")
        return

    patient_options = sorted(patients, key=lambda row: int(row.get("id", 0)))
    provenance_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": provenance_destination_label(row)}
        for row in sorted(provenance_destinations, key=lambda item: int(item.get("id", 0)))
    ]
    burn_etiology_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": burn_etiology_label(row)}
        for row in sorted(burn_etiologies, key=lambda item: int(item.get("id", 0)))
    ]
    inhalation_injury_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": inhalation_injury_label(row)}
        for row in sorted(inhalation_injuries, key=lambda item: int(item.get("id", 0)))
    ]
    optional_bools: list[bool | None] = [None, True, False]

    selected = st.selectbox(
        "Burn unit case to replace",
        options=burn_unit_cases,
        format_func=lambda row: burn_unit_case_label(row, patients_by_id),
        key="put_burn_unit_case_select",
    )

    with st.form("put_burn_unit_case_form"):
        patient = st.selectbox(
            "Patient",
            options=patient_options,
            format_func=patient_label,
            index=find_index_by_key(patient_options, "id", selected.get("patient_id")),
            key="put_burn_case_patient",
        )
        tbsa_burned = st.text_input("TBSA burned (%)", value=str(selected.get("TBSA_burned") or ""))
        admission_date = st.text_input(
            "Admission date (YYYY-MM-DD)",
            value=str(selected.get("admission_date") or ""),
        )
        burn_date = st.text_input("Burn date (YYYY-MM-DD)", value=str(selected.get("burn_date") or ""))
        release_date = st.text_input("Release date (YYYY-MM-DD)", value=str(selected.get("release_date") or ""))
        admission_provenance = st.selectbox(
            "Admission provenance",
            options=provenance_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(provenance_options, "id", selected.get("admission_provenance")),
            key="put_burn_case_admission_provenance",
        )
        release_destination = st.selectbox(
            "Release destination",
            options=provenance_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(provenance_options, "id", selected.get("release_destination")),
            key="put_burn_case_release_destination",
        )
        burn_mecanism_options: list[str | None] = [None, *ALLOWED_BURN_MECANISMS]
        burn_mecanism = st.selectbox(
            "Burn mecanism",
            options=burn_mecanism_options,
            format_func=lambda value: "Not set" if value is None else value,
            index=burn_mecanism_options.index(selected.get("burn_mecanism"))
            if selected.get("burn_mecanism") in burn_mecanism_options
            else 0,
            key="put_burn_case_mecanism",
        )
        burn_etiology = st.selectbox(
            "Burn etiology",
            options=burn_etiology_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(burn_etiology_options, "id", selected.get("burn_etiology")),
            key="put_burn_case_etiology",
        )
        inhalation_injury = st.selectbox(
            "Inhalation injury",
            options=inhalation_injury_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(inhalation_injury_options, "id", selected.get("inhalation_injury")),
            key="put_burn_case_inhalation_injury",
        )
        normalized_violence = normalize_optional_bool(selected.get("violence_related"))
        violence_related = st.selectbox(
            "Violence related",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalized_violence) if normalized_violence in optional_bools else 0,
            key="put_burn_case_violence",
        )
        normalized_suicide = normalize_optional_bool(selected.get("suicide_attempt"))
        suicide_attempt = st.selectbox(
            "Suicide attempt",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalized_suicide) if normalized_suicide in optional_bools else 0,
            key="put_burn_case_suicide",
        )
        accident_type_options: list[str | None] = [None, *ALLOWED_ACCIDENT_TYPES]
        accident_type = st.selectbox(
            "Accident type",
            options=accident_type_options,
            format_func=lambda value: "Not set" if value is None else value,
            index=accident_type_options.index(selected.get("accident_type"))
            if selected.get("accident_type") in accident_type_options
            else 0,
            key="put_burn_case_accident_type",
        )
        normalized_wildfire = normalize_optional_bool(selected.get("wildfire"))
        wildfire = st.selectbox(
            "Wildfire",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalized_wildfire) if normalized_wildfire in optional_bools else 0,
            key="put_burn_case_wildfire",
        )
        normalized_bonfire = normalize_optional_bool(selected.get("bonfire_fogueira"))
        bonfire_fogueira = st.selectbox(
            "Bonfire/Fogueira",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalized_bonfire) if normalized_bonfire in optional_bools else 0,
            key="put_burn_case_bonfire",
        )
        normalized_fireplace = normalize_optional_bool(selected.get("fireplace_lareira"))
        fireplace_lareira = st.selectbox(
            "Fireplace/Lareira",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalized_fireplace) if normalized_fireplace in optional_bools else 0,
            key="put_burn_case_fireplace",
        )
        note = st.text_area("Note", value=str(selected.get("note") or ""))
        special_forces_options: list[str | None] = [None, *ALLOWED_SPECIAL_FORCES]
        special_forces = st.selectbox(
            "Special forces",
            options=special_forces_options,
            format_func=lambda value: "Not set" if value is None else value,
            index=special_forces_options.index(selected.get("special_forces"))
            if selected.get("special_forces") in special_forces_options
            else 0,
            key="put_burn_case_special_forces",
        )
        submitted = st.form_submit_button("Replace burn unit case", width="stretch")

        if submitted:
            try:
                payload = {
                    "patient_id": int(patient["id"]),
                    "TBSA_burned": parse_optional_float_input(tbsa_burned),
                    "admission_date": parse_optional_date_input(admission_date),
                    "burn_date": parse_optional_date_input(burn_date),
                    "release_date": parse_optional_date_input(release_date),
                    "admission_provenance": admission_provenance["id"],
                    "release_destination": release_destination["id"],
                    "burn_mecanism": burn_mecanism,
                    "burn_etiology": burn_etiology["id"],
                    "inhalation_injury": inhalation_injury["id"],
                    "violence_related": violence_related,
                    "suicide_attempt": suicide_attempt,
                    "accident_type": accident_type,
                    "wildfire": wildfire,
                    "bonfire_fogueira": bonfire_fogueira,
                    "fireplace_lareira": fireplace_lareira,
                    "note": optional_text(note),
                    "special_forces": special_forces,
                }
            except ValueError:
                st.error("TBSA burned must be a valid number and dates must use YYYY-MM-DD format.")
                return

            status_code, data = request_json("PUT", f"/burn-unit-cases/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_burn_unit_case_patch_tab(
    burn_unit_cases: list[dict[str, Any]],
    patients: list[dict[str, Any]],
    provenance_destinations: list[dict[str, Any]],
    burn_etiologies: list[dict[str, Any]],
    inhalation_injuries: list[dict[str, Any]],
    patients_by_id: dict[int, dict[str, Any]],
) -> None:
    """Render partial update burn unit case operation."""
    if not burn_unit_cases:
        st.info("Create at least one burn unit case to use this operation.")
        return

    selected = st.selectbox(
        "Burn unit case to patch",
        options=burn_unit_cases,
        format_func=lambda row: burn_unit_case_label(row, patients_by_id),
        key="patch_burn_unit_case_select",
    )
    selected_case_id = int(selected.get("id"))

    patient_options = sorted(patients, key=lambda item: int(item.get("id", 0)))
    if not patient_options:
        patient_options = [{"id": selected.get("patient_id"), "name": "Unknown patient"}]
    provenance_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": provenance_destination_label(row)}
        for row in sorted(provenance_destinations, key=lambda item: int(item.get("id", 0)))
    ]
    burn_etiology_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": burn_etiology_label(row)}
        for row in sorted(burn_etiologies, key=lambda item: int(item.get("id", 0)))
    ]
    inhalation_injury_options = [{"id": None, "label": "Not set"}] + [
        {"id": row.get("id"), "label": inhalation_injury_label(row)}
        for row in sorted(inhalation_injuries, key=lambda item: int(item.get("id", 0)))
    ]
    optional_bools: list[bool | None] = [None, True, False]
    burn_mecanism_options: list[str | None] = [None, *ALLOWED_BURN_MECANISMS]
    accident_type_options: list[str | None] = [None, *ALLOWED_ACCIDENT_TYPES]
    special_forces_options: list[str | None] = [None, *ALLOWED_SPECIAL_FORCES]

    with st.form("patch_burn_unit_case_form"):
        use_patient = st.checkbox("Update patient", key=f"patch_burn_case_use_patient_{selected_case_id}")
        patch_patient = st.selectbox(
            "Patient",
            options=patient_options,
            format_func=patient_label,
            index=find_index_by_key(patient_options, "id", selected.get("patient_id")),
            key=f"patch_burn_case_patient_{selected_case_id}",
        )

        use_tbsa = st.checkbox("Update TBSA burned", key=f"patch_burn_case_use_tbsa_{selected_case_id}")
        patch_tbsa_burned = st.text_input(
            "TBSA burned (%)",
            value=str(selected.get("TBSA_burned") or ""),
            key=f"patch_burn_case_tbsa_{selected_case_id}",
        )

        use_admission_date = st.checkbox(
            "Update admission date",
            key=f"patch_burn_case_use_admission_date_{selected_case_id}",
        )
        patch_admission_date = st.text_input(
            "Admission date (YYYY-MM-DD)",
            value=str(selected.get("admission_date") or ""),
            key=f"patch_burn_case_admission_date_{selected_case_id}",
        )

        use_burn_date = st.checkbox("Update burn date", key=f"patch_burn_case_use_burn_date_{selected_case_id}")
        patch_burn_date = st.text_input(
            "Burn date (YYYY-MM-DD)",
            value=str(selected.get("burn_date") or ""),
            key=f"patch_burn_case_burn_date_{selected_case_id}",
        )

        use_release_date = st.checkbox("Update release date", key=f"patch_burn_case_use_release_date_{selected_case_id}")
        patch_release_date = st.text_input(
            "Release date (YYYY-MM-DD)",
            value=str(selected.get("release_date") or ""),
            key=f"patch_burn_case_release_date_{selected_case_id}",
        )

        use_admission_provenance = st.checkbox(
            "Update admission provenance",
            key=f"patch_burn_case_use_admission_provenance_{selected_case_id}",
        )
        patch_admission_provenance = st.selectbox(
            "Admission provenance",
            options=provenance_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(provenance_options, "id", selected.get("admission_provenance")),
            key=f"patch_burn_case_admission_provenance_{selected_case_id}",
        )

        use_release_destination = st.checkbox(
            "Update release destination",
            key=f"patch_burn_case_use_release_destination_{selected_case_id}",
        )
        patch_release_destination = st.selectbox(
            "Release destination",
            options=provenance_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(provenance_options, "id", selected.get("release_destination")),
            key=f"patch_burn_case_release_destination_{selected_case_id}",
        )

        use_burn_mecanism = st.checkbox("Update burn mecanism", key=f"patch_burn_case_use_mecanism_{selected_case_id}")
        patch_burn_mecanism = st.selectbox(
            "Burn mecanism",
            options=burn_mecanism_options,
            format_func=lambda value: "Not set" if value is None else value,
            index=burn_mecanism_options.index(selected.get("burn_mecanism"))
            if selected.get("burn_mecanism") in burn_mecanism_options
            else 0,
            key=f"patch_burn_case_mecanism_{selected_case_id}",
        )

        use_burn_etiology = st.checkbox("Update burn etiology", key=f"patch_burn_case_use_etiology_{selected_case_id}")
        patch_burn_etiology = st.selectbox(
            "Burn etiology",
            options=burn_etiology_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(burn_etiology_options, "id", selected.get("burn_etiology")),
            key=f"patch_burn_case_etiology_{selected_case_id}",
        )

        use_inhalation_injury = st.checkbox(
            "Update inhalation injury",
            key=f"patch_burn_case_use_inhalation_injury_{selected_case_id}",
        )
        patch_inhalation_injury = st.selectbox(
            "Inhalation injury",
            options=inhalation_injury_options,
            format_func=lambda option: option["label"],
            index=find_index_by_key(inhalation_injury_options, "id", selected.get("inhalation_injury")),
            key=f"patch_burn_case_inhalation_injury_{selected_case_id}",
        )

        use_violence_related = st.checkbox(
            "Update violence related",
            key=f"patch_burn_case_use_violence_{selected_case_id}",
        )
        patch_violence_related = st.selectbox(
            "Violence related",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalize_optional_bool(selected.get("violence_related")))
            if normalize_optional_bool(selected.get("violence_related")) in optional_bools
            else 0,
            key=f"patch_burn_case_violence_{selected_case_id}",
        )

        use_suicide_attempt = st.checkbox(
            "Update suicide attempt",
            key=f"patch_burn_case_use_suicide_{selected_case_id}",
        )
        patch_suicide_attempt = st.selectbox(
            "Suicide attempt",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalize_optional_bool(selected.get("suicide_attempt")))
            if normalize_optional_bool(selected.get("suicide_attempt")) in optional_bools
            else 0,
            key=f"patch_burn_case_suicide_{selected_case_id}",
        )

        use_accident_type = st.checkbox(
            "Update accident type",
            key=f"patch_burn_case_use_accident_type_{selected_case_id}",
        )
        patch_accident_type = st.selectbox(
            "Accident type",
            options=accident_type_options,
            format_func=lambda value: "Not set" if value is None else value,
            index=accident_type_options.index(selected.get("accident_type"))
            if selected.get("accident_type") in accident_type_options
            else 0,
            key=f"patch_burn_case_accident_type_{selected_case_id}",
        )

        use_wildfire = st.checkbox("Update wildfire", key=f"patch_burn_case_use_wildfire_{selected_case_id}")
        patch_wildfire = st.selectbox(
            "Wildfire",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalize_optional_bool(selected.get("wildfire")))
            if normalize_optional_bool(selected.get("wildfire")) in optional_bools
            else 0,
            key=f"patch_burn_case_wildfire_{selected_case_id}",
        )

        use_bonfire = st.checkbox("Update bonfire/fogueira", key=f"patch_burn_case_use_bonfire_{selected_case_id}")
        patch_bonfire_fogueira = st.selectbox(
            "Bonfire/Fogueira",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalize_optional_bool(selected.get("bonfire_fogueira")))
            if normalize_optional_bool(selected.get("bonfire_fogueira")) in optional_bools
            else 0,
            key=f"patch_burn_case_bonfire_{selected_case_id}",
        )

        use_fireplace = st.checkbox("Update fireplace/lareira", key=f"patch_burn_case_use_fireplace_{selected_case_id}")
        patch_fireplace_lareira = st.selectbox(
            "Fireplace/Lareira",
            options=optional_bools,
            format_func=lambda value: "Unknown" if value is None else ("Yes" if value else "No"),
            index=optional_bools.index(normalize_optional_bool(selected.get("fireplace_lareira")))
            if normalize_optional_bool(selected.get("fireplace_lareira")) in optional_bools
            else 0,
            key=f"patch_burn_case_fireplace_{selected_case_id}",
        )

        use_note = st.checkbox("Update note", key=f"patch_burn_case_use_note_{selected_case_id}")
        patch_note = st.text_area(
            "Note",
            value=str(selected.get("note") or ""),
            key=f"patch_burn_case_note_{selected_case_id}",
        )

        use_special_forces = st.checkbox(
            "Update special forces",
            key=f"patch_burn_case_use_special_forces_{selected_case_id}",
        )
        patch_special_forces = st.selectbox(
            "Special forces",
            options=special_forces_options,
            format_func=lambda value: "Not set" if value is None else value,
            index=special_forces_options.index(selected.get("special_forces"))
            if selected.get("special_forces") in special_forces_options
            else 0,
            key=f"patch_burn_case_special_forces_{selected_case_id}",
        )
        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            try:
                if use_patient:
                    payload["patient_id"] = int(patch_patient["id"])
                if use_tbsa:
                    payload["TBSA_burned"] = parse_optional_float_input(patch_tbsa_burned)
                if use_admission_date:
                    payload["admission_date"] = parse_optional_date_input(patch_admission_date)
                if use_burn_date:
                    payload["burn_date"] = parse_optional_date_input(patch_burn_date)
                if use_release_date:
                    payload["release_date"] = parse_optional_date_input(patch_release_date)
            except ValueError:
                st.error("TBSA burned must be a valid number and dates must use YYYY-MM-DD format.")
                return

            if use_admission_provenance:
                payload["admission_provenance"] = patch_admission_provenance["id"]
            if use_release_destination:
                payload["release_destination"] = patch_release_destination["id"]
            if use_burn_mecanism:
                payload["burn_mecanism"] = patch_burn_mecanism
            if use_burn_etiology:
                payload["burn_etiology"] = patch_burn_etiology["id"]
            if use_inhalation_injury:
                payload["inhalation_injury"] = patch_inhalation_injury["id"]
            if use_violence_related:
                payload["violence_related"] = patch_violence_related
            if use_suicide_attempt:
                payload["suicide_attempt"] = patch_suicide_attempt
            if use_accident_type:
                payload["accident_type"] = patch_accident_type
            if use_wildfire:
                payload["wildfire"] = patch_wildfire
            if use_bonfire:
                payload["bonfire_fogueira"] = patch_bonfire_fogueira
            if use_fireplace:
                payload["fireplace_lareira"] = patch_fireplace_lareira
            if use_note:
                payload["note"] = optional_text(patch_note)
            if use_special_forces:
                payload["special_forces"] = patch_special_forces

            if not payload:
                st.warning("Select at least one field to patch.")
                return

            status_code, data = request_json("PATCH", f"/burn-unit-cases/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_burn_unit_case_delete_tab(
    burn_unit_cases: list[dict[str, Any]],
    patients_by_id: dict[int, dict[str, Any]],
) -> None:
    """Render delete burn unit case operation."""
    if not burn_unit_cases:
        st.info("Create at least one burn unit case to use this operation.")
        return

    selected = st.selectbox(
        "Burn unit case to delete",
        options=burn_unit_cases,
        format_func=lambda row: burn_unit_case_label(row, patients_by_id),
        key="delete_burn_unit_case_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_burn_unit_case_confirm",
    )
    if st.button(
        "Delete burn unit case",
        type="primary",
        disabled=not confirm_delete,
        width="stretch",
        key="delete_burn_unit_case_button",
    ):
        status_code, data = request_json("DELETE", f"/burn-unit-cases/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_burn_unit_case_crud_workspace(
    burn_unit_cases: list[dict[str, Any]],
    patients: list[dict[str, Any]],
    provenance_destinations: list[dict[str, Any]],
    burn_etiologies: list[dict[str, Any]],
    inhalation_injuries: list[dict[str, Any]],
) -> None:
    """Render burn unit case CRUD operations in compact tabs."""
    patients_by_id = {int(row["id"]): row for row in patients if row.get("id") is not None}

    card_open()
    section_title("Burn Unit Cases CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_burn_unit_case_create_tab(
            patients,
            provenance_destinations,
            burn_etiologies,
            inhalation_injuries,
        )
    with op_tabs[1]:
        render_burn_unit_case_read_tab(burn_unit_cases, patients_by_id)
    with op_tabs[2]:
        render_burn_unit_case_put_tab(
            burn_unit_cases,
            patients,
            provenance_destinations,
            burn_etiologies,
            inhalation_injuries,
            patients_by_id,
        )
    with op_tabs[3]:
        render_burn_unit_case_patch_tab(
            burn_unit_cases,
            patients,
            provenance_destinations,
            burn_etiologies,
            inhalation_injuries,
            patients_by_id,
        )
    with op_tabs[4]:
        render_burn_unit_case_delete_tab(burn_unit_cases, patients_by_id)

    card_close()


def burn_unit_cases_tab() -> None:
    """Render burn unit cases management UI."""
    st.subheader("Burn Unit Cases Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        burn_unit_cases = load_burn_unit_cases()
        patients = load_patients()
        provenance_destinations = load_provenance_destinations()
        burn_etiologies = load_burn_etiologies()
        inhalation_injuries = load_inhalation_injuries()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_burn_unit_cases_overview(
        burn_unit_cases,
        patients,
        provenance_destinations,
        burn_etiologies,
        inhalation_injuries,
    )
    render_burn_unit_case_crud_workspace(
        burn_unit_cases,
        patients,
        provenance_destinations,
        burn_etiologies,
        inhalation_injuries,
    )


@st.cache_data(ttl=5)
def load_pathologies() -> list[dict[str, Any]]:
    status, data = request_json("GET", "/pathologies")
    if status != 200:
        return []
    return data

@st.cache_data(ttl=5)
def load_case_associated_injuries(case_id: int) -> list[dict[str, Any]]:
    status, data = request_json("GET", f"/case-associated-injuries/{case_id}")
    if status != 200:
        return []
    return data

@st.cache_data(ttl=5)
def load_case_burns(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_burns from API optionally filtered by case_id."""
    path = f"/case-burns?case_id={case_id}" if case_id is not None else "/case-burns"
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case burns: {data}")
    return data


@st.cache_data(ttl=5)
def load_case_infections(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_infections from API optionally filtered by case_id."""
    path = f"/case-infections?case_id={case_id}" if case_id is not None else "/case-infections"
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case infections: {data}")
    return data


@st.cache_data(ttl=5)
def load_case_antibiotics(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_antibiotics from API optionally filtered by case_id."""
    path = f"/case-antibiotics?case_id={case_id}" if case_id is not None else "/case-antibiotics"
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case antibiotics: {data}")
    return data


@st.cache_data(ttl=5)
def load_case_microbiology(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_microbiology from API optionally filtered by case_id."""
    path = f"/case-microbiology?case_id={case_id}" if case_id is not None else "/case-microbiology"
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case microbiology: {data}")
    return data


@st.cache_data(ttl=5)
def load_case_procedures(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_procedures from API optionally filtered by case_id."""
    path = f"/case-procedures?case_id={case_id}" if case_id is not None else "/case-procedures"
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case procedures: {data}")
    return data


@st.cache_data(ttl=5)
def load_case_surgical_interventions(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_surgical_interventions from API optionally filtered by case_id."""
    path = (
        f"/case-surgical-interventions?case_id={case_id}"
        if case_id is not None
        else "/case-surgical-interventions"
    )
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case surgical interventions: {data}")
    return data


@st.cache_data(ttl=5)
def load_case_complications(case_id: int | None = None) -> list[dict[str, Any]]:
    """Load case_complications from API optionally filtered by case_id."""
    path = f"/case-complications?case_id={case_id}" if case_id is not None else "/case-complications"
    status, data = request_json("GET", path)
    if status != 200:
        raise RuntimeError(f"Could not load case complications: {data}")
    return data

@st.cache_data(ttl=5)
def load_burn_depths() -> list[dict[str, Any]]:
    status, data = request_json("GET", "/burn-depths")
    if status != 200:
        return []
    return data

@st.cache_data(ttl=5)
def load_anatomic_locations() -> list[dict[str, Any]]:
    status, data = request_json("GET", "/anatomic-locations")
    if status != 200:
        return []
    return data


def render_case_burns_section(selected_case: dict[str, Any]) -> None:
    """Render the Case Burns Section linked to an open Burn Unit Case"""
    card_open()
    section_title("Case Burns")
    case_id = selected_case["id"]
    try:
        case_burns = load_case_burns(case_id=case_id)
        burn_depths = load_burn_depths()
        anatomic_locations = load_anatomic_locations()
    except Exception as e:
        st.error(str(e))
        card_close()
        return

    depth_by_id = {row["id"]: row for row in burn_depths}
    loc_by_id = {row["id"]: row for row in anatomic_locations}

    if not case_burns:
        st.info("No case burns recorded for this case.")
    else:
        # Build enriched view for dataframe
        enriched_cbs = []
        for cb in case_burns:
            d_name = depth_by_id.get(cb.get("burn_depth_id"), {}).get("depth_new", "?")
            l_name = loc_by_id.get(cb.get("anatomic_location_id"), {}).get("name", "?")
            enriched_cbs.append({
                "Depth": f"[{cb.get('burn_depth_id')}] {d_name}",
                "Location": f"[{cb.get('anatomic_location_id')}] {l_name}",
                "Note": cb.get("note", "")
            })
        st.dataframe(enriched_cbs, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])
    
    with op_tabs[0]:
        with st.form("create_case_burn_form"):
            bd_options = [{"id": d["id"], "label": f"{d['id']} - {d['depth_new']}"} for d in burn_depths]
            loc_options = [{"id": l["id"], "label": f"{l['id']} - {l['name']}"} for l in anatomic_locations]
            
            if not bd_options: bd_options = [{"id": 0, "label": "No depths available"}]
            if not loc_options: loc_options = [{"id": 0, "label": "No locations available"}]

            sel_depth = st.selectbox("Burn Depth", options=bd_options, format_func=lambda x: x["label"])
            sel_loc = st.selectbox("Anatomic Location", options=loc_options, format_func=lambda x: x["label"])
            note = st.text_area("Note", placeholder="Optional")
            
            if st.form_submit_button("Add Case Burn"):
                payload = {
                    "case_id": case_id,
                    "burn_depth_id": sel_depth["id"],
                    "anatomic_location_id": sel_loc["id"],
                    "note": optional_text(note),
                }
                status_code, data = request_json("POST", "/case-burns", payload)
                show_api_result(status_code, data)
                if 200 <= status_code < 300:
                    load_case_burns.clear()
                    st.rerun()

    with op_tabs[1]:
        if case_burns:
            with st.form("edit_case_burn_form"):
                burn_opts = []
                for cb in case_burns:
                    d_name = depth_by_id.get(cb.get("burn_depth_id"), {}).get("depth_new", "?")
                    l_name = loc_by_id.get(cb.get("anatomic_location_id"), {}).get("name", "?")
                    burn_opts.append({
                        "depth_id": cb['burn_depth_id'],
                        "loc_id": cb['anatomic_location_id'],
                        "label": f"{cb['burn_depth_id']} / {cb['anatomic_location_id']} | {d_name} @ {l_name}",
                        "note": cb.get("note", "")
                    })
                selected_opt = st.selectbox("Select (Depth ID / Location ID)", options=burn_opts, format_func=lambda x: x["label"])
                
                target_depth = selected_opt["depth_id"] if selected_opt else 1
                target_loc = selected_opt["loc_id"] if selected_opt else 1
                target_note = selected_opt["note"] if selected_opt else ""
                
                patch_note = st.text_area("Update Note", value=target_note)
                
                if st.form_submit_button("Update Case Burn"):
                    payload = {"note": patch_note}
                    status_code, data = request_json("PATCH", f"/case-burns/{case_id}/{target_depth}/{target_loc}", payload)
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_burns.clear()
                        st.rerun()

    with op_tabs[2]:
        if case_burns:
            with st.form("delete_case_burn_form"):
                burn_opts = []
                for cb in case_burns:
                    d_name = depth_by_id.get(cb.get("burn_depth_id"), {}).get("depth_new", "?")
                    l_name = loc_by_id.get(cb.get("anatomic_location_id"), {}).get("name", "?")
                    burn_opts.append({
                        "depth_id": cb['burn_depth_id'],
                        "loc_id": cb['anatomic_location_id'],
                        "label": f"{cb['burn_depth_id']} / {cb['anatomic_location_id']} | {d_name} @ {l_name}"
                    })
                selected_opt = st.selectbox("Select (Depth ID / Location ID)", options=burn_opts, format_func=lambda x: x["label"], key="del_cb")
                
                if st.form_submit_button("Delete Case Burn", type="primary"):
                    target_depth = selected_opt["depth_id"] if selected_opt else 1
                    target_loc = selected_opt["loc_id"] if selected_opt else 1
                    status_code, data = request_json("DELETE", f"/case-burns/{case_id}/{target_depth}/{target_loc}")
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_burns.clear()
                        st.rerun()
                        
    card_close()



def render_case_associated_injuries_section(selected_case: dict[str, Any]) -> None:
    """Render the Case Associated Injuries Section linked to an open Burn Unit Case"""
    card_open()
    section_title("Associated Injuries")
    case_id = selected_case["id"]
    try:
        associated_injuries = load_case_associated_injuries(case_id=case_id)
        pathologies = load_pathologies()
    except Exception as e:
        st.error(str(e))
        card_close()
        return

    path_by_id = {row["id"]: row for row in pathologies}

    if not associated_injuries:
        st.info("No associated injuries recorded for this case.")
    else:
        # Build enriched view for dataframe
        enriched_injuries = []
        for inj in associated_injuries:
            path_name = path_by_id.get(inj.get("injury_id"), {}).get("name", "Unknown Pathology")
            enriched_injuries.append({
                "Injury": f"[{inj.get('injury_id')}] {path_name}",
                "Date of Injury": inj.get("date_of_injury", ""),
                "Note": inj.get("note", "")
            })
        st.dataframe(enriched_injuries, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])
    
    with op_tabs[0]:
        with st.form("create_case_associated_injury_form"):
            path_options = [{"id": p["id"], "label": f"{p['id']} - {p['name']}"} for p in pathologies]
            
            if not path_options: path_options = [{"id": 0, "label": "No pathologies available"}]

            sel_injury = st.selectbox("Associated Injury (Pathology)", options=path_options, format_func=lambda x: x["label"])
            # The schema allows date_of_injury, let's use date_input with a default to today
            import datetime
            date_of_injury = st.date_input("Date of Injury", value=None)
            note = st.text_area("Note", placeholder="Optional")
            
            if st.form_submit_button("Add Associated Injury"):
                payload = {
                    "case_id": case_id,
                    "injury_id": sel_injury["id"],
                    "date_of_injury": date_of_injury.isoformat() if date_of_injury else None,
                    "note": optional_text(note),
                }
                status_code, data = request_json("POST", "/case-associated-injuries", payload)
                show_api_result(status_code, data)
                if 200 <= status_code < 300:
                    load_case_associated_injuries.clear()
                    st.rerun()

    with op_tabs[1]:
        if associated_injuries:
            with st.form("edit_case_associated_injury_form"):
                inj_opts = []
                for inj in associated_injuries:
                    path_name = path_by_id.get(inj.get("injury_id"), {}).get("name", "Unknown Pathology")
                    inj_opts.append({
                        "injury_id": inj['injury_id'],
                        "label": f"{inj['injury_id']} | {path_name}",
                        "note": inj.get("note", ""),
                        "date_of_injury": inj.get("date_of_injury", None)
                    })
                selected_opt = st.selectbox("Select Associated Injury", options=inj_opts, format_func=lambda x: x["label"])
                
                target_injury_id = selected_opt["injury_id"] if selected_opt else 1
                target_note = selected_opt["note"] if selected_opt else ""
                target_date_str = selected_opt["date_of_injury"] if selected_opt else None

                import datetime
                try: # try to parse the existing date string if any
                    default_date = datetime.date.fromisoformat(target_date_str) if target_date_str else None
                except Exception:
                    default_date = None
                
                patch_date = st.date_input("Update Date of Injury", value=default_date)
                patch_note = st.text_area("Update Note", value=target_note)
                
                if st.form_submit_button("Update Associated Injury"):
                    payload = {
                        "date_of_injury": patch_date.isoformat() if patch_date else None,
                        "note": patch_note
                    }
                    status_code, data = request_json("PATCH", f"/case-associated-injuries/{case_id}/{target_injury_id}", payload)
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_associated_injuries.clear()
                        st.rerun()

    with op_tabs[2]:
        if associated_injuries:
            with st.form("delete_case_associated_injury_form"):
                inj_opts = []
                for inj in associated_injuries:
                    path_name = path_by_id.get(inj.get("injury_id"), {}).get("name", "Unknown Pathology")
                    inj_opts.append({
                        "injury_id": inj['injury_id'],
                        "label": f"{inj['injury_id']} | {path_name}"
                    })
                selected_opt = st.selectbox("Select Associated Injury to Delete", options=inj_opts, format_func=lambda x: x["label"], key="del_inj")
                
                if st.form_submit_button("Delete Associated Injury", type="primary"):
                    target_injury_id = selected_opt["injury_id"] if selected_opt else 1
                    status_code, data = request_json("DELETE", f"/case-associated-injuries/{case_id}/{target_injury_id}")
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_associated_injuries.clear()
                        st.rerun()
                        
    card_close()


def render_case_infections_section(selected_case: dict[str, Any]) -> None:
    """Render case-specific CRUD for case_infections linked to selected burn unit case."""
    card_open()
    section_title("Case Infections")
    case_id = selected_case["id"]
    try:
        case_infections = load_case_infections(case_id=case_id)
        infections = load_infections()
    except Exception as exc:
        st.error(str(exc))
        card_close()
        return

    infections_by_id = {row["id"]: row for row in infections if row.get("id") is not None}

    if not case_infections:
        st.info("No infections recorded for this case.")
    else:
        enriched_rows: list[dict[str, Any]] = []
        for row in case_infections:
            infection = infections_by_id.get(row.get("infection_id"), {})
            enriched_rows.append(
                {
                    "Infection": f"[{row.get('infection_id')}] {infection.get('name', 'Unknown infection')}",
                    "Date of infection": row.get("date_of_infection") or "",
                    "Note": row.get("note") or "",
                }
            )
        st.dataframe(enriched_rows, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])

    with op_tabs[0]:
        with st.form("create_case_infection_form"):
            infection_options = [
                {"id": row["id"], "label": f"{row['id']} - {row.get('name', 'Unnamed infection')}"}
                for row in infections
                if row.get("id") is not None
            ]
            if not infection_options:
                st.info("No infections available. Create infections first in the Infections tab.")
            else:
                selected_infection = st.selectbox(
                    "Infection",
                    options=infection_options,
                    format_func=lambda option: option["label"],
                )
                date_of_infection = st.text_input("Date of infection (YYYY-MM-DD)", placeholder="Optional")
                note = st.text_area("Note", placeholder="Optional")

                if st.form_submit_button("Add Case Infection"):
                    try:
                        parsed_date = parse_optional_date_input(date_of_infection)
                    except ValueError:
                        st.error("Date of infection must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "case_id": case_id,
                            "infection_id": selected_infection["id"],
                            "date_of_infection": parsed_date,
                            "note": optional_text(note),
                        }
                        status_code, data = request_json("POST", "/case-infections", payload)
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_infections.clear()
                            st.rerun()

    with op_tabs[1]:
        if case_infections:
            with st.form("edit_case_infection_form"):
                infection_assoc_options = [
                    {
                        "infection_id": row["infection_id"],
                        "label": (
                            f"{row['infection_id']} - "
                            f"{infections_by_id.get(row['infection_id'], {}).get('name', 'Unknown infection')}"
                        ),
                        "date_of_infection": row.get("date_of_infection") or "",
                        "note": row.get("note") or "",
                    }
                    for row in case_infections
                ]

                selected_assoc = st.selectbox(
                    "Select case infection",
                    options=infection_assoc_options,
                    format_func=lambda option: option["label"],
                )
                patch_date_of_infection = st.text_input(
                    "Update date of infection (YYYY-MM-DD)",
                    value=selected_assoc.get("date_of_infection", ""),
                )
                patch_note = st.text_area("Update note", value=selected_assoc.get("note", ""))

                if st.form_submit_button("Update Case Infection"):
                    try:
                        parsed_date = parse_optional_date_input(patch_date_of_infection)
                    except ValueError:
                        st.error("Date of infection must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "date_of_infection": parsed_date,
                            "note": optional_text(patch_note),
                        }
                        target_infection_id = selected_assoc["infection_id"]
                        status_code, data = request_json(
                            "PATCH",
                            f"/case-infections/{case_id}/{target_infection_id}",
                            payload,
                        )
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_infections.clear()
                            st.rerun()

    with op_tabs[2]:
        if case_infections:
            with st.form("delete_case_infection_form"):
                infection_assoc_options = [
                    {
                        "infection_id": row["infection_id"],
                        "label": (
                            f"{row['infection_id']} - "
                            f"{infections_by_id.get(row['infection_id'], {}).get('name', 'Unknown infection')}"
                        ),
                    }
                    for row in case_infections
                ]
                selected_assoc = st.selectbox(
                    "Select case infection to delete",
                    options=infection_assoc_options,
                    format_func=lambda option: option["label"],
                    key="delete_case_infection_select",
                )

                if st.form_submit_button("Delete Case Infection", type="primary"):
                    target_infection_id = selected_assoc["infection_id"]
                    status_code, data = request_json(
                        "DELETE",
                        f"/case-infections/{case_id}/{target_infection_id}",
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_infections.clear()
                        st.rerun()

    card_close()


def render_case_antibiotics_section(selected_case: dict[str, Any]) -> None:
    """Render case-specific CRUD for case_antibiotics linked to selected burn unit case."""
    card_open()
    section_title("Case Antibiotics")
    selected_case_id = selected_case["id"]
    try:
        case_antibiotics = load_case_antibiotics(case_id=selected_case_id)
        antibiotics = load_antibiotics()
        infections = load_infections()
    except Exception as exc:
        st.error(str(exc))
        card_close()
        return
    antibiotics_by_id = {row["id"]: row for row in antibiotics if row.get("id") is not None}
    antibiotic_options = [
        {"id": row["id"], "label": antibiotic_label(row)}
        for row in antibiotics
        if row.get("id") is not None
    ]
    infections_by_id = {row["id"]: row for row in infections if row.get("id") is not None}
    indication_options = [{"id": None, "label": "No indication"}] + [
        {"id": row["id"], "label": f"{row['id']} - {row.get('name', 'Unnamed infection')}"}
        for row in infections
        if row.get("id") is not None
    ]

    if not case_antibiotics:
        st.info("No antibiotics recorded for this case.")
    else:
        enriched_rows: list[dict[str, Any]] = []
        for row in case_antibiotics:
            antibiotic = antibiotics_by_id.get(row.get("antibiotic_id"), {})
            indication = infections_by_id.get(row.get("indication"), {})
            enriched_rows.append(
                {
                    "Antibiotic": (
                        f"[{row.get('antibiotic_id')}] "
                        f"{antibiotic.get('name', 'Unknown antibiotic')}"
                    ),
                    "Indication": (
                        ""
                        if row.get("indication") is None
                        else f"[{row.get('indication')}] {indication.get('name', 'Unknown infection')}"
                    ),
                    "Date started": row.get("date_started") or "",
                    "Date stopped": row.get("date_stopped") or "",
                    "Note": row.get("note") or "",
                }
            )
        st.dataframe(enriched_rows, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])

    with op_tabs[0]:
        with st.form("create_case_antibiotic_form"):
            if not antibiotic_options:
                st.info("No antibiotics available. Create antibiotics first in the Antibiotics tab.")
            else:
                selected_antibiotic = st.selectbox(
                    "Antibiotic",
                    options=antibiotic_options,
                    format_func=lambda option: option["label"],
                    key="create_case_antibiotic_antibiotic_select",
                )
                selected_indication = st.selectbox(
                    "Indication",
                    options=indication_options,
                    format_func=lambda option: option["label"],
                    key="create_case_antibiotic_indication_select",
                )
                date_started = st.text_input("Date started (YYYY-MM-DD)", placeholder="Optional")
                date_stopped = st.text_input("Date stopped (YYYY-MM-DD)", placeholder="Optional")
                note = st.text_area("Note", placeholder="Optional")

                if st.form_submit_button("Add Case Antibiotic"):
                    try:
                        parsed_date_started = parse_optional_date_input(date_started)
                        parsed_date_stopped = parse_optional_date_input(date_stopped)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "case_id": selected_case_id,
                            "antibiotic_id": selected_antibiotic["id"],
                            "indication": selected_indication["id"],
                            "date_started": parsed_date_started,
                            "date_stopped": parsed_date_stopped,
                            "note": optional_text(note),
                        }
                        status_code, data = request_json("POST", "/case-antibiotics", payload)
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_antibiotics.clear()
                            st.rerun()

    with op_tabs[1]:
        if case_antibiotics:
            with st.form("edit_case_antibiotic_form"):
                assoc_options = [
                    {
                        "case_id": row["case_id"],
                        "antibiotic_id": row["antibiotic_id"],
                        "indication": row.get("indication"),
                        "date_started": row.get("date_started") or "",
                        "date_stopped": row.get("date_stopped") or "",
                        "note": row.get("note") or "",
                        "label": (
                            f"{row['case_id']} / {row['antibiotic_id']} - "
                            f"{antibiotics_by_id.get(row['antibiotic_id'], {}).get('name', 'Unknown antibiotic')}"
                        ),
                    }
                    for row in case_antibiotics
                ]
                selected_assoc = st.selectbox(
                    "Select case antibiotic",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="edit_case_antibiotic_target_select",
                )

                edit_antibiotic_index = find_index_by_key(
                    antibiotic_options,
                    "id",
                    selected_assoc["antibiotic_id"],
                )
                edit_indication_index = find_index_by_key(
                    indication_options,
                    "id",
                    selected_assoc.get("indication"),
                )

                edited_antibiotic = st.selectbox(
                    "Antibiotic",
                    options=antibiotic_options,
                    format_func=lambda option: option["label"],
                    index=edit_antibiotic_index,
                    key="edit_case_antibiotic_antibiotic_select",
                )
                edited_indication = st.selectbox(
                    "Indication",
                    options=indication_options,
                    format_func=lambda option: option["label"],
                    index=edit_indication_index,
                    key="edit_case_antibiotic_indication_select",
                )
                patch_date_started = st.text_input(
                    "Update date started (YYYY-MM-DD)",
                    value=selected_assoc.get("date_started", ""),
                )
                patch_date_stopped = st.text_input(
                    "Update date stopped (YYYY-MM-DD)",
                    value=selected_assoc.get("date_stopped", ""),
                )
                patch_note = st.text_area("Update note", value=selected_assoc.get("note", ""))

                if st.form_submit_button("Update Case Antibiotic"):
                    try:
                        parsed_date_started = parse_optional_date_input(patch_date_started)
                        parsed_date_stopped = parse_optional_date_input(patch_date_stopped)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "antibiotic_id": edited_antibiotic["id"],
                            "indication": edited_indication["id"],
                            "date_started": parsed_date_started,
                            "date_stopped": parsed_date_stopped,
                            "note": optional_text(patch_note),
                        }
                        status_code, data = request_json(
                            "PATCH",
                            f"/case-antibiotics/{selected_assoc['case_id']}/{selected_assoc['antibiotic_id']}",
                            payload,
                        )
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_antibiotics.clear()
                            st.rerun()

    with op_tabs[2]:
        if case_antibiotics:
            with st.form("delete_case_antibiotic_form"):
                assoc_options = [
                    {
                        "case_id": row["case_id"],
                        "antibiotic_id": row["antibiotic_id"],
                        "label": (
                            f"{row['case_id']} / {row['antibiotic_id']} - "
                            f"{antibiotics_by_id.get(row['antibiotic_id'], {}).get('name', 'Unknown antibiotic')}"
                        ),
                    }
                    for row in case_antibiotics
                ]
                selected_assoc = st.selectbox(
                    "Select case antibiotic to delete",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="delete_case_antibiotic_select",
                )

                if st.form_submit_button("Delete Case Antibiotic", type="primary"):
                    status_code, data = request_json(
                        "DELETE",
                        f"/case-antibiotics/{selected_assoc['case_id']}/{selected_assoc['antibiotic_id']}",
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_antibiotics.clear()
                        st.rerun()

    card_close()


def render_case_microbiology_section(selected_case: dict[str, Any]) -> None:
    """Render case-specific CRUD for case_microbiology linked to selected burn unit case."""
    card_open()
    section_title("Case Microbiology")
    selected_case_id = selected_case["id"]
    try:
        case_microbiology_rows = load_case_microbiology(case_id=selected_case_id)
        specimens = load_microbiology_specimens()
        agents = load_microbiology_agents()
    except Exception as exc:
        st.error(str(exc))
        card_close()
        return

    specimens_by_id = {row["id"]: row for row in specimens if row.get("id") is not None}
    agents_by_id = {row["id"]: row for row in agents if row.get("id") is not None}
    specimen_options = [
        {"id": row["id"], "label": microbiology_specimen_label(row)}
        for row in specimens
        if row.get("id") is not None
    ]
    agent_options = [
        {"id": row["id"], "label": microbiology_agent_label(row)}
        for row in agents
        if row.get("id") is not None
    ]

    if not case_microbiology_rows:
        st.info("No microbiology rows recorded for this case.")
    else:
        enriched_rows: list[dict[str, Any]] = []
        for row in case_microbiology_rows:
            specimen = specimens_by_id.get(row.get("specimen_id"), {})
            agent = agents_by_id.get(row.get("microorganism_id"), {})
            enriched_rows.append(
                {
                    "ID": row.get("id"),
                    "Specimen": (
                        f"[{row.get('specimen_id')}] "
                        f"{specimen.get('specimen_type', 'Unknown specimen')}"
                    ),
                    "Microorganism": (
                        f"[{row.get('microorganism_id')}] "
                        f"{agent.get('name', 'Unknown microorganism')}"
                    ),
                    "Hospital test id": row.get("hospital_test_id") or "",
                    "Collection date": row.get("date_of_collection") or "",
                    "Reporting date": row.get("date_of_reporting") or "",
                    "Note": row.get("note") or "",
                }
            )
        st.dataframe(enriched_rows, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])

    with op_tabs[0]:
        with st.form("create_case_microbiology_form"):
            if not specimen_options:
                st.info("No microbiology specimens available. Create them in Microbiology Specimens.")
                st.form_submit_button("Add Case Microbiology", disabled=True)
            elif not agent_options:
                st.info("No microbiology agents available. Create them in Microbiology Agents.")
                st.form_submit_button("Add Case Microbiology", disabled=True)
            else:
                selected_specimen = st.selectbox(
                    "Specimen",
                    options=specimen_options,
                    format_func=lambda option: option["label"],
                    key="create_case_microbiology_specimen_select",
                )
                selected_agent = st.selectbox(
                    "Microorganism",
                    options=agent_options,
                    format_func=lambda option: option["label"],
                    key="create_case_microbiology_agent_select",
                )
                hospital_test_id = st.text_input("Hospital test id", placeholder="Optional")
                date_of_collection = st.text_input("Date of collection (YYYY-MM-DD)", placeholder="Optional")
                date_of_reporting = st.text_input("Date of reporting (YYYY-MM-DD)", placeholder="Optional")
                note = st.text_area("Note", placeholder="Optional")

                submitted = st.form_submit_button("Add Case Microbiology")
                if submitted:
                    try:
                        parsed_collection_date = parse_optional_date_input(date_of_collection)
                        parsed_reporting_date = parse_optional_date_input(date_of_reporting)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "case_id": selected_case_id,
                            "specimen_id": selected_specimen["id"],
                            "microorganism_id": selected_agent["id"],
                            "hospital_test_id": optional_text(hospital_test_id),
                            "date_of_collection": parsed_collection_date,
                            "date_of_reporting": parsed_reporting_date,
                            "note": optional_text(note),
                        }
                        status_code, data = request_json("POST", "/case-microbiology", payload)
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_microbiology.clear()
                            st.rerun()

    with op_tabs[1]:
        if case_microbiology_rows:
            with st.form("edit_case_microbiology_form"):
                row_options = [
                    {
                        "id": row["id"],
                        "specimen_id": row["specimen_id"],
                        "microorganism_id": row["microorganism_id"],
                        "hospital_test_id": row.get("hospital_test_id") or "",
                        "date_of_collection": row.get("date_of_collection") or "",
                        "date_of_reporting": row.get("date_of_reporting") or "",
                        "note": row.get("note") or "",
                        "label": (
                            f"{row['id']} - "
                            f"{agents_by_id.get(row['microorganism_id'], {}).get('name', 'Unknown microorganism')}"
                        ),
                    }
                    for row in case_microbiology_rows
                ]
                selected_row = st.selectbox(
                    "Select case microbiology row",
                    options=row_options,
                    format_func=lambda option: option["label"],
                    key="edit_case_microbiology_target_select",
                )

                edit_specimen_index = find_index_by_key(specimen_options, "id", selected_row["specimen_id"])
                edit_agent_index = find_index_by_key(agent_options, "id", selected_row["microorganism_id"])

                edited_specimen = st.selectbox(
                    "Specimen",
                    options=specimen_options,
                    format_func=lambda option: option["label"],
                    index=edit_specimen_index,
                    key="edit_case_microbiology_specimen_select",
                )
                edited_agent = st.selectbox(
                    "Microorganism",
                    options=agent_options,
                    format_func=lambda option: option["label"],
                    index=edit_agent_index,
                    key="edit_case_microbiology_agent_select",
                )
                patch_hospital_test_id = st.text_input(
                    "Hospital test id",
                    value=selected_row.get("hospital_test_id", ""),
                )
                patch_date_of_collection = st.text_input(
                    "Update date of collection (YYYY-MM-DD)",
                    value=selected_row.get("date_of_collection", ""),
                )
                patch_date_of_reporting = st.text_input(
                    "Update date of reporting (YYYY-MM-DD)",
                    value=selected_row.get("date_of_reporting", ""),
                )
                patch_note = st.text_area("Update note", value=selected_row.get("note", ""))

                if st.form_submit_button("Update Case Microbiology"):
                    try:
                        parsed_collection_date = parse_optional_date_input(patch_date_of_collection)
                        parsed_reporting_date = parse_optional_date_input(patch_date_of_reporting)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "specimen_id": edited_specimen["id"],
                            "microorganism_id": edited_agent["id"],
                            "hospital_test_id": optional_text(patch_hospital_test_id),
                            "date_of_collection": parsed_collection_date,
                            "date_of_reporting": parsed_reporting_date,
                            "note": optional_text(patch_note),
                        }
                        status_code, data = request_json(
                            "PATCH",
                            f"/case-microbiology/{selected_row['id']}",
                            payload,
                        )
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_microbiology.clear()
                            st.rerun()

    with op_tabs[2]:
        if case_microbiology_rows:
            with st.form("delete_case_microbiology_form"):
                row_options = [
                    {
                        "id": row["id"],
                        "label": (
                            f"{row['id']} - "
                            f"{agents_by_id.get(row['microorganism_id'], {}).get('name', 'Unknown microorganism')}"
                        ),
                    }
                    for row in case_microbiology_rows
                ]
                selected_row = st.selectbox(
                    "Select case microbiology row to delete",
                    options=row_options,
                    format_func=lambda option: option["label"],
                    key="delete_case_microbiology_select",
                )

                if st.form_submit_button("Delete Case Microbiology", type="primary"):
                    status_code, data = request_json(
                        "DELETE",
                        f"/case-microbiology/{selected_row['id']}",
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_microbiology.clear()
                        st.rerun()

    card_close()


def render_case_procedures_section(selected_case: dict[str, Any]) -> None:
    """Render case-specific CRUD for case_procedures linked to selected burn unit case."""
    card_open()
    section_title("Case Procedures")
    selected_case_id = selected_case["id"]
    try:
        case_procedures = load_case_procedures(case_id=selected_case_id)
        medical_procedures = load_medical_procedures()
    except Exception as exc:
        st.error(str(exc))
        card_close()
        return

    procedures_by_id = {row["id"]: row for row in medical_procedures if row.get("id") is not None}
    procedure_options = [
        {"id": row["id"], "label": medical_procedure_label(row)}
        for row in medical_procedures
        if row.get("id") is not None
    ]

    if not case_procedures:
        st.info("No procedures recorded for this case.")
    else:
        enriched_rows: list[dict[str, Any]] = []
        for row in case_procedures:
            procedure = procedures_by_id.get(row.get("procedure_id"), {})
            enriched_rows.append(
                {
                    "Procedure": (
                        f"[{row.get('procedure_id')}] "
                        f"{procedure.get('name', 'Unknown procedure')}"
                    ),
                    "Date started": row.get("date_started") or "",
                    "Date stopped": row.get("date_stopped") or "",
                    "Before admission": "Yes" if bool(row.get("before_admission")) else "No",
                    "Note": row.get("note") or "",
                }
            )
        st.dataframe(enriched_rows, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])

    with op_tabs[0]:
        with st.form("create_case_procedure_form"):
            if not procedure_options:
                st.info("No medical procedures available. Create them in Medical Procedures.")
                st.form_submit_button("Add Case Procedure", disabled=True)
            else:
                selected_procedure = st.selectbox(
                    "Procedure",
                    options=procedure_options,
                    format_func=lambda option: option["label"],
                    key="create_case_procedure_procedure_select",
                )
                date_started = st.text_input("Date started (YYYY-MM-DD)", placeholder="Optional")
                date_stopped = st.text_input("Date stopped (YYYY-MM-DD)", placeholder="Optional")
                before_admission = st.checkbox(
                    "Procedure was done before admission",
                    value=False,
                )
                note = st.text_area("Note", placeholder="Optional")

                if st.form_submit_button("Add Case Procedure"):
                    try:
                        parsed_date_started = parse_optional_date_input(date_started)
                        parsed_date_stopped = parse_optional_date_input(date_stopped)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "case_id": selected_case_id,
                            "procedure_id": selected_procedure["id"],
                            "date_started": parsed_date_started,
                            "date_stopped": parsed_date_stopped,
                            "before_admission": before_admission,
                            "note": optional_text(note),
                        }
                        status_code, data = request_json("POST", "/case-procedures", payload)
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_procedures.clear()
                            st.rerun()

    with op_tabs[1]:
        if case_procedures:
            with st.form("edit_case_procedure_form"):
                assoc_options = [
                    {
                        "id": row["id"],
                        "case_id": row["case_id"],
                        "procedure_id": row["procedure_id"],
                        "date_started": row.get("date_started") or "",
                        "date_stopped": row.get("date_stopped") or "",
                        "before_admission": bool(row.get("before_admission")),
                        "note": row.get("note") or "",
                        "label": (
                            f"#{row['id']} | {row['case_id']} / {row['procedure_id']} - "
                            f"{procedures_by_id.get(row['procedure_id'], {}).get('name', 'Unknown procedure')}"
                        ),
                    }
                    for row in case_procedures
                ]
                selected_assoc = st.selectbox(
                    "Select case procedure",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="edit_case_procedure_target_select",
                )

                edit_procedure_index = find_index_by_key(
                    procedure_options,
                    "id",
                    selected_assoc["procedure_id"],
                )

                edited_procedure = st.selectbox(
                    "Procedure",
                    options=procedure_options,
                    format_func=lambda option: option["label"],
                    index=edit_procedure_index,
                    key="edit_case_procedure_procedure_select",
                )
                patch_date_started = st.text_input(
                    "Update date started (YYYY-MM-DD)",
                    value=selected_assoc.get("date_started", ""),
                )
                patch_date_stopped = st.text_input(
                    "Update date stopped (YYYY-MM-DD)",
                    value=selected_assoc.get("date_stopped", ""),
                )
                patch_before_admission = st.checkbox(
                    "Procedure was done before admission",
                    value=selected_assoc.get("before_admission", False),
                )
                patch_note = st.text_area("Update note", value=selected_assoc.get("note", ""))

                if st.form_submit_button("Update Case Procedure"):
                    try:
                        parsed_date_started = parse_optional_date_input(patch_date_started)
                        parsed_date_stopped = parse_optional_date_input(patch_date_stopped)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "procedure_id": edited_procedure["id"],
                            "date_started": parsed_date_started,
                            "date_stopped": parsed_date_stopped,
                            "before_admission": patch_before_admission,
                            "note": optional_text(patch_note),
                        }
                        status_code, data = request_json(
                            "PATCH",
                            f"/case-procedures/{selected_assoc['id']}",
                            payload,
                        )
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_procedures.clear()
                            st.rerun()

    with op_tabs[2]:
        if case_procedures:
            with st.form("delete_case_procedure_form"):
                assoc_options = [
                    {
                        "id": row["id"],
                        "case_id": row["case_id"],
                        "procedure_id": row["procedure_id"],
                        "label": (
                            f"#{row['id']} | {row['case_id']} / {row['procedure_id']} - "
                            f"{procedures_by_id.get(row['procedure_id'], {}).get('name', 'Unknown procedure')}"
                        ),
                    }
                    for row in case_procedures
                ]
                selected_assoc = st.selectbox(
                    "Select case procedure to delete",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="delete_case_procedure_select",
                )

                if st.form_submit_button("Delete Case Procedure", type="primary"):
                    status_code, data = request_json(
                        "DELETE",
                        f"/case-procedures/{selected_assoc['id']}",
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_procedures.clear()
                        st.rerun()

    card_close()


def render_case_surgical_interventions_section(selected_case: dict[str, Any]) -> None:
    """Render case-specific CRUD for case_surgical_interventions linked to selected burn unit case."""
    card_open()
    section_title("Case Surgical Interventions")
    selected_case_id = selected_case["id"]
    try:
        case_interventions = load_case_surgical_interventions(case_id=selected_case_id)
        interventions = load_surgical_interventions()
    except Exception as exc:
        st.error(str(exc))
        card_close()
        return

    interventions_by_id = {row["id"]: row for row in interventions if row.get("id") is not None}
    intervention_options = [
        {"id": row["id"], "label": surgical_intervention_label(row)}
        for row in interventions
        if row.get("id") is not None
    ]

    if not case_interventions:
        st.info("No surgical interventions recorded for this case.")
    else:
        enriched_rows: list[dict[str, Any]] = []
        for row in case_interventions:
            intervention = interventions_by_id.get(row.get("intervention_id"), {})
            enriched_rows.append(
                {
                    "Intervention": (
                        f"[{row.get('intervention_id')}] "
                        f"{intervention.get('name', 'Unknown intervention')}"
                    ),
                    "Date started": row.get("date_started") or "",
                    "Date stopped": row.get("date_stopped") or "",
                    "Note": row.get("note") or "",
                }
            )
        st.dataframe(enriched_rows, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])

    with op_tabs[0]:
        with st.form("create_case_surgical_intervention_form"):
            if not intervention_options:
                st.info("No surgical interventions available. Create them in Surgical Interventions.")
                st.form_submit_button("Add Case Surgical Intervention", disabled=True)
            else:
                selected_intervention = st.selectbox(
                    "Intervention",
                    options=intervention_options,
                    format_func=lambda option: option["label"],
                    key="create_case_surgical_intervention_select",
                )
                date_started = st.text_input("Date started (YYYY-MM-DD)", placeholder="Optional")
                date_stopped = st.text_input("Date stopped (YYYY-MM-DD)", placeholder="Optional")
                note = st.text_area("Note", placeholder="Optional")

                if st.form_submit_button("Add Case Surgical Intervention"):
                    try:
                        parsed_date_started = parse_optional_date_input(date_started)
                        parsed_date_stopped = parse_optional_date_input(date_stopped)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "case_id": selected_case_id,
                            "intervention_id": selected_intervention["id"],
                            "date_started": parsed_date_started,
                            "date_stopped": parsed_date_stopped,
                            "note": optional_text(note),
                        }
                        status_code, data = request_json("POST", "/case-surgical-interventions", payload)
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_surgical_interventions.clear()
                            st.rerun()

    with op_tabs[1]:
        if case_interventions:
            with st.form("edit_case_surgical_intervention_form"):
                assoc_options = [
                    {
                        "id": row["id"],
                        "case_id": row["case_id"],
                        "intervention_id": row["intervention_id"],
                        "date_started": row.get("date_started") or "",
                        "date_stopped": row.get("date_stopped") or "",
                        "note": row.get("note") or "",
                        "label": (
                            f"#{row['id']} | {row['case_id']} / {row['intervention_id']} - "
                            f"{interventions_by_id.get(row['intervention_id'], {}).get('name', 'Unknown intervention')}"
                        ),
                    }
                    for row in case_interventions
                ]
                selected_assoc = st.selectbox(
                    "Select case intervention",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="edit_case_surgical_intervention_target_select",
                )

                edit_intervention_index = find_index_by_key(
                    intervention_options,
                    "id",
                    selected_assoc["intervention_id"],
                )

                edited_intervention = st.selectbox(
                    "Intervention",
                    options=intervention_options,
                    format_func=lambda option: option["label"],
                    index=edit_intervention_index,
                    key="edit_case_surgical_intervention_select",
                )
                patch_date_started = st.text_input(
                    "Update date started (YYYY-MM-DD)",
                    value=selected_assoc.get("date_started", ""),
                )
                patch_date_stopped = st.text_input(
                    "Update date stopped (YYYY-MM-DD)",
                    value=selected_assoc.get("date_stopped", ""),
                )
                patch_note = st.text_area("Update note", value=selected_assoc.get("note", ""))

                if st.form_submit_button("Update Case Surgical Intervention"):
                    try:
                        parsed_date_started = parse_optional_date_input(patch_date_started)
                        parsed_date_stopped = parse_optional_date_input(patch_date_stopped)
                    except ValueError:
                        st.error("Dates must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "intervention_id": edited_intervention["id"],
                            "date_started": parsed_date_started,
                            "date_stopped": parsed_date_stopped,
                            "note": optional_text(patch_note),
                        }
                        status_code, data = request_json(
                            "PATCH",
                            f"/case-surgical-interventions/{selected_assoc['id']}",
                            payload,
                        )
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_surgical_interventions.clear()
                            st.rerun()

    with op_tabs[2]:
        if case_interventions:
            with st.form("delete_case_surgical_intervention_form"):
                assoc_options = [
                    {
                        "id": row["id"],
                        "case_id": row["case_id"],
                        "intervention_id": row["intervention_id"],
                        "label": (
                            f"#{row['id']} | {row['case_id']} / {row['intervention_id']} - "
                            f"{interventions_by_id.get(row['intervention_id'], {}).get('name', 'Unknown intervention')}"
                        ),
                    }
                    for row in case_interventions
                ]
                selected_assoc = st.selectbox(
                    "Select case intervention to delete",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="delete_case_surgical_intervention_select",
                )

                if st.form_submit_button("Delete Case Surgical Intervention", type="primary"):
                    status_code, data = request_json(
                        "DELETE",
                        f"/case-surgical-interventions/{selected_assoc['id']}",
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_surgical_interventions.clear()
                        st.rerun()

    card_close()


def render_case_complications_section(selected_case: dict[str, Any]) -> None:
    """Render case-specific CRUD for case_complications linked to selected burn unit case."""
    card_open()
    section_title("Case Complications")
    selected_case_id = selected_case["id"]
    try:
        case_complications = load_case_complications(case_id=selected_case_id)
        complications = load_complications()
    except Exception as exc:
        st.error(str(exc))
        card_close()
        return

    complications_by_id = {row["id"]: row for row in complications if row.get("id") is not None}
    complication_options = [
        {"id": row["id"], "label": complication_label(row)}
        for row in complications
        if row.get("id") is not None
    ]

    if not case_complications:
        st.info("No complications recorded for this case.")
    else:
        enriched_rows: list[dict[str, Any]] = []
        for row in case_complications:
            complication = complications_by_id.get(row.get("complication_id"), {})
            enriched_rows.append(
                {
                    "Complication": (
                        f"[{row.get('complication_id')}] "
                        f"{complication.get('name', 'Unknown complication')}"
                    ),
                    "Date started": row.get("date_started") or "",
                    "Note": row.get("note") or "",
                }
            )
        st.dataframe(enriched_rows, hide_index=True, width="stretch")

    op_tabs = st.tabs(["Add", "Edit", "Delete"])

    with op_tabs[0]:
        with st.form("create_case_complication_form"):
            if not complication_options:
                st.info("No complications available. Create them in Complications.")
                st.form_submit_button("Add Case Complication", disabled=True)
            else:
                selected_complication = st.selectbox(
                    "Complication",
                    options=complication_options,
                    format_func=lambda option: option["label"],
                    key="create_case_complication_select",
                )
                date_started = st.text_input("Date started (YYYY-MM-DD)", placeholder="Optional")
                note = st.text_area("Note", placeholder="Optional")

                if st.form_submit_button("Add Case Complication"):
                    try:
                        parsed_date_started = parse_optional_date_input(date_started)
                    except ValueError:
                        st.error("Date must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "case_id": selected_case_id,
                            "complication_id": selected_complication["id"],
                            "date_started": parsed_date_started,
                            "note": optional_text(note),
                        }
                        status_code, data = request_json("POST", "/case-complications", payload)
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_complications.clear()
                            st.rerun()

    with op_tabs[1]:
        if case_complications:
            with st.form("edit_case_complication_form"):
                assoc_options = [
                    {
                        "case_id": row["case_id"],
                        "complication_id": row["complication_id"],
                        "date_started": row.get("date_started") or "",
                        "note": row.get("note") or "",
                        "label": (
                            f"{row['case_id']} / {row['complication_id']} - "
                            f"{complications_by_id.get(row['complication_id'], {}).get('name', 'Unknown complication')}"
                        ),
                    }
                    for row in case_complications
                ]
                selected_assoc = st.selectbox(
                    "Select case complication",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="edit_case_complication_target_select",
                )

                edit_complication_index = find_index_by_key(
                    complication_options,
                    "id",
                    selected_assoc["complication_id"],
                )

                edited_complication = st.selectbox(
                    "Complication",
                    options=complication_options,
                    format_func=lambda option: option["label"],
                    index=edit_complication_index,
                    key="edit_case_complication_select",
                )
                patch_date_started = st.text_input(
                    "Update date started (YYYY-MM-DD)",
                    value=selected_assoc.get("date_started", ""),
                )
                patch_note = st.text_area("Update note", value=selected_assoc.get("note", ""))

                if st.form_submit_button("Update Case Complication"):
                    try:
                        parsed_date_started = parse_optional_date_input(patch_date_started)
                    except ValueError:
                        st.error("Date must use YYYY-MM-DD format.")
                    else:
                        payload = {
                            "complication_id": edited_complication["id"],
                            "date_started": parsed_date_started,
                            "note": optional_text(patch_note),
                        }
                        status_code, data = request_json(
                            "PATCH",
                            f"/case-complications/{selected_assoc['case_id']}/{selected_assoc['complication_id']}",
                            payload,
                        )
                        show_api_result(status_code, data)
                        if 200 <= status_code < 300:
                            load_case_complications.clear()
                            st.rerun()

    with op_tabs[2]:
        if case_complications:
            with st.form("delete_case_complication_form"):
                assoc_options = [
                    {
                        "case_id": row["case_id"],
                        "complication_id": row["complication_id"],
                        "label": (
                            f"{row['case_id']} / {row['complication_id']} - "
                            f"{complications_by_id.get(row['complication_id'], {}).get('name', 'Unknown complication')}"
                        ),
                    }
                    for row in case_complications
                ]
                selected_assoc = st.selectbox(
                    "Select case complication to delete",
                    options=assoc_options,
                    format_func=lambda option: option["label"],
                    key="delete_case_complication_select",
                )

                if st.form_submit_button("Delete Case Complication", type="primary"):
                    status_code, data = request_json(
                        "DELETE",
                        f"/case-complications/{selected_assoc['case_id']}/{selected_assoc['complication_id']}",
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        load_case_complications.clear()
                        st.rerun()

    card_close()

def render_burn_unit_case_future_associations_placeholder() -> None:
    """Reserve space for future burn-case association tables."""
    card_open(compact=True)
    section_title("Future Burn Case Modules")
    st.info(
        "This Burn Unit Case Overview is prepared for additional future association tables."
    )
    card_close()


def burn_unit_case_overview_tab() -> None:
    """Render burn-case-centric overview prepared for future association modules."""
    st.subheader("Burn Unit Case Overview")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        burn_unit_cases = load_burn_unit_cases()
        patients = load_patients()
        provenance_destinations = load_provenance_destinations()
        burn_etiologies = load_burn_etiologies()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not burn_unit_cases:
        st.info("No burn unit cases found. Create cases first in the Burn Unit Cases tab.")
        return

    patients_by_id = {int(row["id"]): row for row in patients if row.get("id") is not None}
    provenance_by_id = {int(row["id"]): row for row in provenance_destinations if row.get("id") is not None}
    etiology_by_id = {int(row["id"]): row for row in burn_etiologies if row.get("id") is not None}

    selected_case = st.selectbox(
        "Select burn unit case",
        options=burn_unit_cases,
        format_func=lambda row: burn_unit_case_label(row, patients_by_id),
        key="burn_case_overview_case_select",
    )

    card_open(compact=True)
    section_title("Selected Burn Unit Case")
    st.json(selected_case)
    card_close()

    card_open(compact=True)
    section_title("Resolved References")
    patient_name = patients_by_id.get(selected_case.get("patient_id"), {}).get("name", "Unknown patient")
    admission_name = provenance_by_id.get(selected_case.get("admission_provenance"), {}).get("name", "Not set")
    release_name = provenance_by_id.get(selected_case.get("release_destination"), {}).get("name", "Not set")
    etiology_name = etiology_by_id.get(selected_case.get("burn_etiology"), {}).get("name", "Not set")
    st.markdown(
        f"<span class='ui-badge'>Patient: {selected_case.get('patient_id')} - {patient_name}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span class='ui-badge'>Admission provenance: {selected_case.get('admission_provenance')} - {admission_name}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span class='ui-badge'>Release destination: {selected_case.get('release_destination')} - {release_name}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span class='ui-badge'>Burn etiology: {selected_case.get('burn_etiology')} - {etiology_name}</span>",
        unsafe_allow_html=True,
    )
    card_close()

    render_case_burns_section(selected_case)
    render_case_associated_injuries_section(selected_case)
    render_case_infections_section(selected_case)
    render_case_antibiotics_section(selected_case)
    render_case_procedures_section(selected_case)
    render_case_surgical_interventions_section(selected_case)
    render_case_complications_section(selected_case)
    render_case_microbiology_section(selected_case)

    render_burn_unit_case_future_associations_placeholder()


def patient_pathology_row_label(row: dict[str, Any], pathologies_by_id: dict[int, dict[str, Any]]) -> str:
    """Build readable association label for patient overview selectors."""
    pathology_id = row.get("pathology_id")
    pathology_name = pathologies_by_id.get(pathology_id, {}).get("name", "Unknown pathology")
    severity = row.get("severity") or "-"
    diagnosed_date = row.get("diagnosed_date") or "-"
    return f"pathology {pathology_id} ({pathology_name}) | severity={severity} | diagnosed={diagnosed_date}"


def patient_medication_row_label(row: dict[str, Any], medications_by_id: dict[int, dict[str, Any]]) -> str:
    """Build readable medication association label for patient overview selectors."""
    medication_id = row.get("medication_id")
    medication_name = medications_by_id.get(medication_id, {}).get("name", "Unknown medication")
    dosage = row.get("dosage") or "-"
    prescribed_date = row.get("prescribed_date") or "-"
    return f"medication {medication_id} ({medication_name}) | dosage={dosage} | prescribed={prescribed_date}"


def render_patient_pathologies_section(
    selected_patient: dict[str, Any],
    pathologies: list[dict[str, Any]],
    associations: list[dict[str, Any]],
) -> None:
    """Render CRED controls for patient_pathologies scoped to one selected patient."""
    patient_id = selected_patient["id"]
    pathologies_by_id = {int(item["id"]): item for item in pathologies if item.get("id") is not None}
    rows_for_patient = [row for row in associations if row.get("patient_id") == patient_id]

    card_open()
    section_title("Patient Pathologies")

    st.markdown(
        f"<span class='ui-badge'>Associations for patient {patient_id}: {len(rows_for_patient)}</span>",
        unsafe_allow_html=True,
    )

    if rows_for_patient:
        st.dataframe(rows_for_patient, width="stretch", hide_index=True)
    else:
        st.info("This patient has no associated pathologies yet.")

    op_tabs = st.tabs(["Create", "Read", "Edit", "Delete"])

    with op_tabs[0]:
        if not pathologies:
            st.info("No pathologies available. Create pathologies first in the Pathologies tab.")
        else:
            pathology_options = sorted(pathologies, key=lambda p: int(p.get("id", 0)))
            with st.form("patient_overview_assoc_create_form"):
                pathology = st.selectbox(
                    "Pathology",
                    options=pathology_options,
                    format_func=pathology_label,
                )
                diagnosed_date = st.text_input("Diagnosed date (YYYY-MM-DD)", placeholder="Optional")
                severity = st.text_input("Severity", placeholder="Optional")
                submitted = st.form_submit_button("Create association", width="stretch")

                if submitted:
                    diagnosed_date_value = optional_text(diagnosed_date)
                    if diagnosed_date_value:
                        try:
                            diagnosed_date_value = parse_birth_date_input(diagnosed_date_value)
                        except ValueError:
                            st.error("Diagnosed date must use format YYYY-MM-DD.")
                            return

                    payload = {
                        "patient_id": patient_id,
                        "pathology_id": int(pathology["id"]),
                        "diagnosed_date": diagnosed_date_value,
                        "severity": optional_text(severity),
                    }
                    status_code, data = request_json("POST", "/patient-pathologies", payload)
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        refresh_data()

    with op_tabs[1]:
        if not rows_for_patient:
            st.info("No association rows to read for this patient.")
        else:
            selected_row = st.selectbox(
                "Association row",
                options=rows_for_patient,
                format_func=lambda row: patient_pathology_row_label(row, pathologies_by_id),
                key="patient_overview_assoc_read_select",
            )
            if st.button("Show association details", width="stretch", key="patient_overview_assoc_read_btn"):
                st.json(selected_row)

    with op_tabs[2]:
        if not rows_for_patient:
            st.info("No association rows to edit for this patient.")
        else:
            selected_row = st.selectbox(
                "Association row to edit",
                options=rows_for_patient,
                format_func=lambda row: patient_pathology_row_label(row, pathologies_by_id),
                key="patient_overview_assoc_patch_select",
            )

            pathology_options = sorted(pathologies, key=lambda p: int(p.get("id", 0))) if pathologies else []

            with st.form("patient_overview_assoc_patch_form"):
                use_pathology = st.checkbox("Update pathology", key="patient_overview_assoc_patch_use_pathology")
                if pathology_options:
                    patch_pathology = st.selectbox(
                        "Pathology",
                        options=pathology_options,
                        format_func=pathology_label,
                        index=find_index_by_key(pathology_options, "id", selected_row.get("pathology_id")),
                    )
                else:
                    patch_pathology = None
                    st.info("No pathologies available to switch to.")

                use_diagnosed_date = st.checkbox(
                    "Update diagnosed date",
                    key="patient_overview_assoc_patch_use_diagnosed_date",
                )
                patch_diagnosed_date = st.text_input(
                    "Diagnosed date (YYYY-MM-DD)",
                    value=str(selected_row.get("diagnosed_date") or ""),
                )

                use_severity = st.checkbox("Update severity", key="patient_overview_assoc_patch_use_severity")
                patch_severity = st.text_input("Severity", value=str(selected_row.get("severity") or ""))

                submitted = st.form_submit_button("Apply edit", width="stretch")

                if submitted:
                    payload: dict[str, Any] = {}
                    if use_pathology and patch_pathology is not None:
                        payload["pathology_id"] = int(patch_pathology["id"])
                    if use_diagnosed_date:
                        diagnosed_date_value = optional_text(patch_diagnosed_date)
                        if diagnosed_date_value:
                            try:
                                diagnosed_date_value = parse_birth_date_input(diagnosed_date_value)
                            except ValueError:
                                st.error("Diagnosed date must use format YYYY-MM-DD.")
                                return
                        payload["diagnosed_date"] = diagnosed_date_value
                    if use_severity:
                        payload["severity"] = optional_text(patch_severity)

                    status_code, data = request_json(
                        "PATCH",
                        f"/patient-pathologies/{patient_id}/{selected_row['pathology_id']}",
                        payload,
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        refresh_data()

    with op_tabs[3]:
        if not rows_for_patient:
            st.info("No association rows to delete for this patient.")
        else:
            selected_row = st.selectbox(
                "Association row to delete",
                options=rows_for_patient,
                format_func=lambda row: patient_pathology_row_label(row, pathologies_by_id),
                key="patient_overview_assoc_delete_select",
            )
            confirm_delete = st.checkbox(
                "I understand this action cannot be undone",
                key="patient_overview_assoc_delete_confirm",
            )
            if st.button(
                "Delete association",
                type="primary",
                disabled=not confirm_delete,
                width="stretch",
                key="patient_overview_assoc_delete_btn",
            ):
                status_code, data = request_json(
                    "DELETE",
                    f"/patient-pathologies/{patient_id}/{selected_row['pathology_id']}",
                )
                show_api_result(status_code, data)
                if 200 <= status_code < 300:
                    refresh_data()

    card_close()


def render_patient_medications_section(
    selected_patient: dict[str, Any],
    medications: list[dict[str, Any]],
    associations: list[dict[str, Any]],
) -> None:
    """Render CRED controls for patient_medications scoped to one selected patient."""
    patient_id = selected_patient["id"]
    medications_by_id = {int(item["id"]): item for item in medications if item.get("id") is not None}
    rows_for_patient = [row for row in associations if row.get("patient_id") == patient_id]

    card_open()
    section_title("Patient Medications")

    st.markdown(
        f"<span class='ui-badge'>Associations for patient {patient_id}: {len(rows_for_patient)}</span>",
        unsafe_allow_html=True,
    )

    if rows_for_patient:
        st.dataframe(rows_for_patient, width="stretch", hide_index=True)
    else:
        st.info("This patient has no associated medications yet.")

    op_tabs = st.tabs(["Create", "Read", "Edit", "Delete"])

    with op_tabs[0]:
        if not medications:
            st.info("No medications available. Create medications first in the Medications tab.")
        else:
            medication_options = sorted(medications, key=lambda m: int(m.get("id", 0)))
            with st.form("patient_overview_med_assoc_create_form"):
                medication = st.selectbox(
                    "Medication",
                    options=medication_options,
                    format_func=medication_label,
                )
                prescribed_date = st.text_input("Prescribed date (YYYY-MM-DD)", placeholder="Optional")
                dosage = st.text_input("Dosage", placeholder="Optional")
                submitted = st.form_submit_button("Create association", width="stretch")

                if submitted:
                    prescribed_date_value = optional_text(prescribed_date)
                    if prescribed_date_value:
                        try:
                            prescribed_date_value = parse_birth_date_input(prescribed_date_value)
                        except ValueError:
                            st.error("Prescribed date must use format YYYY-MM-DD.")
                            return

                    payload = {
                        "patient_id": patient_id,
                        "medication_id": int(medication["id"]),
                        "prescribed_date": prescribed_date_value,
                        "dosage": optional_text(dosage),
                    }
                    status_code, data = request_json("POST", "/patient-medications", payload)
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        refresh_data()

    with op_tabs[1]:
        if not rows_for_patient:
            st.info("No association rows to read for this patient.")
        else:
            selected_row = st.selectbox(
                "Association row",
                options=rows_for_patient,
                format_func=lambda row: patient_medication_row_label(row, medications_by_id),
                key="patient_overview_med_assoc_read_select",
            )
            if st.button("Show association details", width="stretch", key="patient_overview_med_assoc_read_btn"):
                st.json(selected_row)

    with op_tabs[2]:
        if not rows_for_patient:
            st.info("No association rows to edit for this patient.")
        else:
            selected_row = st.selectbox(
                "Association row to edit",
                options=rows_for_patient,
                format_func=lambda row: patient_medication_row_label(row, medications_by_id),
                key="patient_overview_med_assoc_patch_select",
            )

            medication_options = sorted(medications, key=lambda m: int(m.get("id", 0))) if medications else []

            with st.form("patient_overview_med_assoc_patch_form"):
                use_medication = st.checkbox("Update medication", key="patient_overview_med_assoc_patch_use_medication")
                if medication_options:
                    patch_medication = st.selectbox(
                        "Medication",
                        options=medication_options,
                        format_func=medication_label,
                        index=find_index_by_key(medication_options, "id", selected_row.get("medication_id")),
                    )
                else:
                    patch_medication = None
                    st.info("No medications available to switch to.")

                use_prescribed_date = st.checkbox(
                    "Update prescribed date",
                    key="patient_overview_med_assoc_patch_use_prescribed_date",
                )
                patch_prescribed_date = st.text_input(
                    "Prescribed date (YYYY-MM-DD)",
                    value=str(selected_row.get("prescribed_date") or ""),
                )

                use_dosage = st.checkbox("Update dosage", key="patient_overview_med_assoc_patch_use_dosage")
                patch_dosage = st.text_input("Dosage", value=str(selected_row.get("dosage") or ""))

                submitted = st.form_submit_button("Apply edit", width="stretch")

                if submitted:
                    payload: dict[str, Any] = {}
                    if use_medication and patch_medication is not None:
                        payload["medication_id"] = int(patch_medication["id"])
                    if use_prescribed_date:
                        prescribed_date_value = optional_text(patch_prescribed_date)
                        if prescribed_date_value:
                            try:
                                prescribed_date_value = parse_birth_date_input(prescribed_date_value)
                            except ValueError:
                                st.error("Prescribed date must use format YYYY-MM-DD.")
                                return
                        payload["prescribed_date"] = prescribed_date_value
                    if use_dosage:
                        payload["dosage"] = optional_text(patch_dosage)

                    status_code, data = request_json(
                        "PATCH",
                        f"/patient-medications/{patient_id}/{selected_row['medication_id']}",
                        payload,
                    )
                    show_api_result(status_code, data)
                    if 200 <= status_code < 300:
                        refresh_data()

    with op_tabs[3]:
        if not rows_for_patient:
            st.info("No association rows to delete for this patient.")
        else:
            selected_row = st.selectbox(
                "Association row to delete",
                options=rows_for_patient,
                format_func=lambda row: patient_medication_row_label(row, medications_by_id),
                key="patient_overview_med_assoc_delete_select",
            )
            confirm_delete = st.checkbox(
                "I understand this action cannot be undone",
                key="patient_overview_med_assoc_delete_confirm",
            )
            if st.button(
                "Delete association",
                type="primary",
                disabled=not confirm_delete,
                width="stretch",
                key="patient_overview_med_assoc_delete_btn",
            ):
                status_code, data = request_json(
                    "DELETE",
                    f"/patient-medications/{patient_id}/{selected_row['medication_id']}",
                )
                show_api_result(status_code, data)
                if 200 <= status_code < 300:
                    refresh_data()

    card_close()


def render_future_associations_placeholder() -> None:
    """Reserve space for future patient-linked association tables."""
    card_open(compact=True)
    section_title("Future Association Modules")
    st.info(
        "This Patient Overview layout is prepared to add more patient-linked modules "
        "(e.g., medications, surgeries) while keeping one selected patient context."
    )
    card_close()


def patient_overview_tab() -> None:
    """Render patient-centric overview with association controls."""
    st.subheader("Patient Overview")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        patients = load_patients()
        pathologies = load_pathologies()
        pathology_associations = load_patient_pathologies()
        medications = load_medications()
        medication_associations = load_patient_medications()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not patients:
        st.info("No patients found. Create patients first in the Patients tab.")
        return

    selected_patient = st.selectbox(
        "Select patient",
        options=patients,
        format_func=patient_label,
        key="patient_overview_patient_select",
    )

    card_open(compact=True)
    section_title("Selected Patient")
    st.json(selected_patient)
    card_close()

    cols = st.columns(2)
    with cols[0]:
        render_patient_pathologies_section(selected_patient, pathologies, pathology_associations)
    with cols[1]:
        render_patient_medications_section(selected_patient, medications, medication_associations)

    render_future_associations_placeholder()



@st.cache_data(ttl=5)
def load_infections() -> list[dict[str, Any]]:
    """Load all infections from API."""
    status, data = request_json("GET", "/infections")
    if status != 200:
        raise RuntimeError(f"Could not load infections: {data}")
    return data


@st.cache_data(ttl=5)
def load_microbiology_specimens() -> list[dict[str, Any]]:
    """Load all microbiology specimens from API."""
    status, data = request_json("GET", "/microbiology-specimens")
    if status != 200:
        raise RuntimeError(f"Could not load microbiology specimens: {data}")
    return data


@st.cache_data(ttl=5)
def load_microbiology_agents() -> list[dict[str, Any]]:
    """Load all microbiology agents from API."""
    status, data = request_json("GET", "/microbiology-agents")
    if status != 200:
        raise RuntimeError(f"Could not load microbiology agents: {data}")
    return data


@st.cache_data(ttl=5)
def load_medical_procedures() -> list[dict[str, Any]]:
    """Load all medical procedures from API."""
    status, data = request_json("GET", "/medical-procedures")
    if status != 200:
        raise RuntimeError(f"Could not load medical procedures: {data}")
    return data


@st.cache_data(ttl=5)
def load_surgical_interventions() -> list[dict[str, Any]]:
    """Load all surgical interventions from API."""
    status, data = request_json("GET", "/surgical-interventions")
    if status != 200:
        raise RuntimeError(f"Could not load surgical interventions: {data}")
    return data


@st.cache_data(ttl=5)
def load_complications() -> list[dict[str, Any]]:
    """Load all complications from API."""
    status, data = request_json("GET", "/complications")
    if status != 200:
        raise RuntimeError(f"Could not load complications: {data}")
    return data


def infection_label(infection: dict[str, Any]) -> str:
    """Format an infection for display in selectboxes."""
    return f"{infection['name']} ({infection['id']})"


def microbiology_specimen_label(specimen: dict[str, Any]) -> str:
    """Format a microbiology specimen for display in selectboxes."""
    loinc_code = specimen.get("loinc_code") or "-"
    return f"{specimen.get('id')} - {specimen.get('specimen_type')} (LOINC: {loinc_code})"


def microbiology_agent_label(agent: dict[str, Any]) -> str:
    """Format a microbiology agent for display in selectboxes."""
    snomed_code = agent.get("snomed_ct_code") or "-"
    return f"{agent.get('id')} - {agent.get('name')} (SNOMED-CT: {snomed_code})"


def medical_procedure_label(procedure: dict[str, Any]) -> str:
    """Format a medical procedure for display in selectboxes."""
    snomed_code = procedure.get("snomed_ct_code") or "-"
    return f"{procedure.get('id')} - {procedure.get('name')} (SNOMED-CT: {snomed_code})"


def surgical_intervention_label(intervention: dict[str, Any]) -> str:
    """Format a surgical intervention for display in selectboxes."""
    snomed_code = intervention.get("snomed_ct_code") or "-"
    return f"{intervention.get('id')} - {intervention.get('name')} (SNOMED-CT: {snomed_code})"


def complication_label(complication: dict[str, Any]) -> str:
    """Format a complication for display in selectboxes."""
    snomed_code = complication.get("snomed_ct_code") or "-"
    return f"{complication.get('id')} - {complication.get('name')} (SNOMED-CT: {snomed_code})"


def render_infections_overview(infections: list[dict[str, Any]]) -> None:
    """Render compact overview and infection list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Infections: {len(infections)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_infections"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Infections")
    if infections:
        st.dataframe(infections, width="stretch", hide_index=True)
    else:
        st.info("No infections available yet.")
    card_close()


def render_infection_create_tab() -> None:
    """Render create infection operation."""
    with st.form("create_infection_form"):
        infection_id = st.number_input("Infection ID", min_value=1, step=1, format="%d")
        name = st.text_input("Name", placeholder="Infection name")
        description = st.text_area("Description", placeholder="Optional description")
        submitted = st.form_submit_button("Create infection", width="stretch")

        if submitted:
            payload = {
                "id": int(infection_id),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/infections", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_infection_read_tab(infections: list[dict[str, Any]]) -> None:
    """Render read single infection operation."""
    if not infections:
        st.info("Create at least one infection to use this operation.")
        return

    selected = st.selectbox(
        "Select infection",
        options=infections,
        format_func=infection_label,
        key="read_infection_select",
    )
    if st.button("Fetch infection", width="stretch"):
        status_code, data = request_json("GET", f"/infections/{selected['id']}")
        show_api_result(status_code, data)


def render_infection_put_tab(infections: list[dict[str, Any]]) -> None:
    """Render full replace infection operation."""
    if not infections:
        st.info("Create at least one infection to use this operation.")
        return

    selected = st.selectbox(
        "Infection to replace",
        options=infections,
        format_func=infection_label,
        key="put_infection_select",
    )

    with st.form("put_infection_form"):
        name = st.text_input("Name", value=str(selected.get("name", "")))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace infection", width="stretch")

        if submitted:
            payload = {
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/infections/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_infection_delete_tab(infections: list[dict[str, Any]]) -> None:
    """Render delete infection operation."""
    if not infections:
        st.info("Create at least one infection to use this operation.")
        return

    selected = st.selectbox(
        "Infection to delete",
        options=infections,
        format_func=infection_label,
        key="delete_infection_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_infection_confirm",
    )
    if st.button("Delete infection", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/infections/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_infections_crud_workspace(infections: list[dict[str, Any]]) -> None:
    """Render infection CRUD operations in compact tabs."""
    card_open()
    section_title("Infections CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_infection_create_tab()
    with op_tabs[1]:
        render_infection_read_tab(infections)
    with op_tabs[2]:
        render_infection_put_tab(infections)
    with op_tabs[3]:
        render_infection_delete_tab(infections)

    card_close()


def infections_tab() -> None:
    """Render infections management UI."""
    st.subheader("Infections Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        infections = load_infections()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_infections_overview(infections)
    render_infections_crud_workspace(infections)


def render_microbiology_specimens_overview(specimens: list[dict[str, Any]]) -> None:
    """Render compact overview and microbiology specimen list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Specimens: {len(specimens)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_microbiology_specimens"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Microbiology Specimens")
    if specimens:
        st.dataframe(specimens, width="stretch", hide_index=True)
    else:
        st.info("No microbiology specimens available yet.")
    card_close()


def render_microbiology_specimen_create_tab() -> None:
    """Render create microbiology specimen operation."""
    with st.form("create_microbiology_specimen_form"):
        loinc_code = st.text_input("LOINC code", placeholder="LOINC code")
        specimen_type = st.text_input("Specimen type", placeholder="e.g. blood culture")
        note = st.text_area("Note", placeholder="Optional")
        submitted = st.form_submit_button("Create microbiology specimen", width="stretch")

        if submitted:
            payload = {
                "loinc_code": loinc_code.strip(),
                "specimen_type": specimen_type.strip(),
                "note": optional_text(note),
            }
            status_code, data = request_json("POST", "/microbiology-specimens", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_microbiology_specimen_read_tab(specimens: list[dict[str, Any]]) -> None:
    """Render read single microbiology specimen operation."""
    if not specimens:
        st.info("Create at least one microbiology specimen to use this operation.")
        return

    selected = st.selectbox(
        "Select microbiology specimen",
        options=specimens,
        format_func=microbiology_specimen_label,
        key="read_microbiology_specimen_select",
    )
    if st.button("Fetch microbiology specimen", width="stretch"):
        status_code, data = request_json("GET", f"/microbiology-specimens/{selected['id']}")
        show_api_result(status_code, data)


def render_microbiology_specimen_put_tab(specimens: list[dict[str, Any]]) -> None:
    """Render full replace microbiology specimen operation."""
    if not specimens:
        st.info("Create at least one microbiology specimen to use this operation.")
        return

    selected = st.selectbox(
        "Microbiology specimen to replace",
        options=specimens,
        format_func=microbiology_specimen_label,
        key="put_microbiology_specimen_select",
    )

    with st.form("put_microbiology_specimen_form"):
        loinc_code = st.text_input("LOINC code", value=str(selected.get("loinc_code") or ""))
        specimen_type = st.text_input("Specimen type", value=str(selected.get("specimen_type") or ""))
        note = st.text_area("Note", value=str(selected.get("note") or ""))
        submitted = st.form_submit_button("Replace microbiology specimen", width="stretch")

        if submitted:
            payload = {
                "loinc_code": loinc_code.strip(),
                "specimen_type": specimen_type.strip(),
                "note": optional_text(note),
            }
            status_code, data = request_json("PUT", f"/microbiology-specimens/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_microbiology_specimen_patch_tab(specimens: list[dict[str, Any]]) -> None:
    """Render partial update microbiology specimen operation."""
    if not specimens:
        st.info("Create at least one microbiology specimen to use this operation.")
        return

    selected = st.selectbox(
        "Microbiology specimen to patch",
        options=specimens,
        format_func=microbiology_specimen_label,
        key="patch_microbiology_specimen_select",
    )

    with st.form("patch_microbiology_specimen_form"):
        use_loinc_code = st.checkbox("Update LOINC code", key="patch_microbiology_specimen_use_loinc")
        patch_loinc_code = st.text_input(
            "LOINC code",
            value=str(selected.get("loinc_code") or ""),
            key="patch_microbiology_specimen_loinc",
        )

        use_specimen_type = st.checkbox("Update specimen type", key="patch_microbiology_specimen_use_type")
        patch_specimen_type = st.text_input(
            "Specimen type",
            value=str(selected.get("specimen_type") or ""),
            key="patch_microbiology_specimen_type",
        )

        use_note = st.checkbox("Update note", key="patch_microbiology_specimen_use_note")
        patch_note = st.text_area(
            "Note",
            value=str(selected.get("note") or ""),
            key="patch_microbiology_specimen_note",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_loinc_code:
                payload["loinc_code"] = patch_loinc_code.strip()
            if use_specimen_type:
                payload["specimen_type"] = patch_specimen_type.strip()
            if use_note:
                payload["note"] = optional_text(patch_note)

            status_code, data = request_json("PATCH", f"/microbiology-specimens/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_microbiology_specimen_delete_tab(specimens: list[dict[str, Any]]) -> None:
    """Render delete microbiology specimen operation."""
    if not specimens:
        st.info("Create at least one microbiology specimen to use this operation.")
        return

    selected = st.selectbox(
        "Microbiology specimen to delete",
        options=specimens,
        format_func=microbiology_specimen_label,
        key="delete_microbiology_specimen_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_microbiology_specimen_confirm",
    )
    if st.button("Delete microbiology specimen", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/microbiology-specimens/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_microbiology_specimen_crud_workspace(specimens: list[dict[str, Any]]) -> None:
    """Render microbiology specimen CRUD operations in compact tabs."""
    card_open()
    section_title("Microbiology Specimens CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_microbiology_specimen_create_tab()
    with op_tabs[1]:
        render_microbiology_specimen_read_tab(specimens)
    with op_tabs[2]:
        render_microbiology_specimen_put_tab(specimens)
    with op_tabs[3]:
        render_microbiology_specimen_patch_tab(specimens)
    with op_tabs[4]:
        render_microbiology_specimen_delete_tab(specimens)

    card_close()


def microbiology_specimens_tab() -> None:
    """Render microbiology specimens management UI."""
    st.subheader("Microbiology Specimens Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        specimens = load_microbiology_specimens()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_microbiology_specimens_overview(specimens)
    render_microbiology_specimen_crud_workspace(specimens)


def render_microbiology_agents_overview(agents: list[dict[str, Any]]) -> None:
    """Render compact overview and microbiology agent list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Agents: {len(agents)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_microbiology_agents"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Microbiology Agents")
    if agents:
        st.dataframe(agents, width="stretch", hide_index=True)
    else:
        st.info("No microbiology agents available yet.")
    card_close()


def render_microbiology_agent_create_tab() -> None:
    """Render create microbiology agent operation."""
    with st.form("create_microbiology_agent_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", placeholder="SNOMED-CT concept id")
        name = st.text_input("Name", placeholder="Microorganism name")
        description = st.text_area("Description", placeholder="Optional")
        submitted = st.form_submit_button("Create microbiology agent", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/microbiology-agents", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_microbiology_agent_read_tab(agents: list[dict[str, Any]]) -> None:
    """Render read single microbiology agent operation."""
    if not agents:
        st.info("Create at least one microbiology agent to use this operation.")
        return

    selected = st.selectbox(
        "Select microbiology agent",
        options=agents,
        format_func=microbiology_agent_label,
        key="read_microbiology_agent_select",
    )
    if st.button("Fetch microbiology agent", width="stretch"):
        status_code, data = request_json("GET", f"/microbiology-agents/{selected['id']}")
        show_api_result(status_code, data)


def render_microbiology_agent_put_tab(agents: list[dict[str, Any]]) -> None:
    """Render full replace microbiology agent operation."""
    if not agents:
        st.info("Create at least one microbiology agent to use this operation.")
        return

    selected = st.selectbox(
        "Microbiology agent to replace",
        options=agents,
        format_func=microbiology_agent_label,
        key="put_microbiology_agent_select",
    )

    with st.form("put_microbiology_agent_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", value=str(selected.get("snomed_ct_code") or ""))
        name = st.text_input("Name", value=str(selected.get("name") or ""))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace microbiology agent", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/microbiology-agents/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_microbiology_agent_patch_tab(agents: list[dict[str, Any]]) -> None:
    """Render partial update microbiology agent operation."""
    if not agents:
        st.info("Create at least one microbiology agent to use this operation.")
        return

    selected = st.selectbox(
        "Microbiology agent to patch",
        options=agents,
        format_func=microbiology_agent_label,
        key="patch_microbiology_agent_select",
    )

    with st.form("patch_microbiology_agent_form"):
        use_snomed_code = st.checkbox("Update SNOMED-CT code", key="patch_microbiology_agent_use_code")
        patch_snomed_code = st.text_input(
            "SNOMED-CT code",
            value=str(selected.get("snomed_ct_code") or ""),
            key="patch_microbiology_agent_code",
        )

        use_name = st.checkbox("Update name", key="patch_microbiology_agent_use_name")
        patch_name = st.text_input(
            "Name",
            value=str(selected.get("name") or ""),
            key="patch_microbiology_agent_name",
        )

        use_description = st.checkbox("Update description", key="patch_microbiology_agent_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_microbiology_agent_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_snomed_code:
                payload["snomed_ct_code"] = patch_snomed_code.strip()
            if use_name:
                payload["name"] = patch_name.strip()
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/microbiology-agents/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_microbiology_agent_delete_tab(agents: list[dict[str, Any]]) -> None:
    """Render delete microbiology agent operation."""
    if not agents:
        st.info("Create at least one microbiology agent to use this operation.")
        return

    selected = st.selectbox(
        "Microbiology agent to delete",
        options=agents,
        format_func=microbiology_agent_label,
        key="delete_microbiology_agent_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_microbiology_agent_confirm",
    )
    if st.button("Delete microbiology agent", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/microbiology-agents/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_microbiology_agent_crud_workspace(agents: list[dict[str, Any]]) -> None:
    """Render microbiology agent CRUD operations in compact tabs."""
    card_open()
    section_title("Microbiology Agents CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_microbiology_agent_create_tab()
    with op_tabs[1]:
        render_microbiology_agent_read_tab(agents)
    with op_tabs[2]:
        render_microbiology_agent_put_tab(agents)
    with op_tabs[3]:
        render_microbiology_agent_patch_tab(agents)
    with op_tabs[4]:
        render_microbiology_agent_delete_tab(agents)

    card_close()


def microbiology_agents_tab() -> None:
    """Render microbiology agents management UI."""
    st.subheader("Microbiology Agents Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        agents = load_microbiology_agents()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_microbiology_agents_overview(agents)
    render_microbiology_agent_crud_workspace(agents)


def render_medical_procedures_overview(procedures: list[dict[str, Any]]) -> None:
    """Render compact overview and medical procedure list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Medical Procedures: {len(procedures)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_medical_procedures"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Medical Procedures")
    if procedures:
        st.dataframe(procedures, width="stretch", hide_index=True)
    else:
        st.info("No medical procedures available yet.")
    card_close()


def render_medical_procedure_create_tab() -> None:
    """Render create medical procedure operation."""
    with st.form("create_medical_procedure_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", placeholder="SNOMED-CT concept id")
        name = st.text_input("Name", placeholder="Procedure name")
        description = st.text_area("Description", placeholder="Optional")
        submitted = st.form_submit_button("Create medical procedure", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/medical-procedures", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_medical_procedure_read_tab(procedures: list[dict[str, Any]]) -> None:
    """Render read single medical procedure operation."""
    if not procedures:
        st.info("Create at least one medical procedure to use this operation.")
        return

    selected = st.selectbox(
        "Select medical procedure",
        options=procedures,
        format_func=medical_procedure_label,
        key="read_medical_procedure_select",
    )
    if st.button("Fetch medical procedure", width="stretch"):
        status_code, data = request_json("GET", f"/medical-procedures/{selected['id']}")
        show_api_result(status_code, data)


def render_medical_procedure_put_tab(procedures: list[dict[str, Any]]) -> None:
    """Render full replace medical procedure operation."""
    if not procedures:
        st.info("Create at least one medical procedure to use this operation.")
        return

    selected = st.selectbox(
        "Medical procedure to replace",
        options=procedures,
        format_func=medical_procedure_label,
        key="put_medical_procedure_select",
    )

    with st.form("put_medical_procedure_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", value=str(selected.get("snomed_ct_code") or ""))
        name = st.text_input("Name", value=str(selected.get("name") or ""))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace medical procedure", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/medical-procedures/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_medical_procedure_patch_tab(procedures: list[dict[str, Any]]) -> None:
    """Render partial update medical procedure operation."""
    if not procedures:
        st.info("Create at least one medical procedure to use this operation.")
        return

    selected = st.selectbox(
        "Medical procedure to patch",
        options=procedures,
        format_func=medical_procedure_label,
        key="patch_medical_procedure_select",
    )

    with st.form("patch_medical_procedure_form"):
        use_snomed_code = st.checkbox("Update SNOMED-CT code", key="patch_medical_procedure_use_code")
        patch_snomed_code = st.text_input(
            "SNOMED-CT code",
            value=str(selected.get("snomed_ct_code") or ""),
            key="patch_medical_procedure_code",
        )

        use_name = st.checkbox("Update name", key="patch_medical_procedure_use_name")
        patch_name = st.text_input(
            "Name",
            value=str(selected.get("name") or ""),
            key="patch_medical_procedure_name",
        )

        use_description = st.checkbox("Update description", key="patch_medical_procedure_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_medical_procedure_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_snomed_code:
                payload["snomed_ct_code"] = patch_snomed_code.strip()
            if use_name:
                payload["name"] = patch_name.strip()
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/medical-procedures/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_medical_procedure_delete_tab(procedures: list[dict[str, Any]]) -> None:
    """Render delete medical procedure operation."""
    if not procedures:
        st.info("Create at least one medical procedure to use this operation.")
        return

    selected = st.selectbox(
        "Medical procedure to delete",
        options=procedures,
        format_func=medical_procedure_label,
        key="delete_medical_procedure_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_medical_procedure_confirm",
    )
    if st.button("Delete medical procedure", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/medical-procedures/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_medical_procedure_crud_workspace(procedures: list[dict[str, Any]]) -> None:
    """Render medical procedure CRUD operations in compact tabs."""
    card_open()
    section_title("Medical Procedures CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_medical_procedure_create_tab()
    with op_tabs[1]:
        render_medical_procedure_read_tab(procedures)
    with op_tabs[2]:
        render_medical_procedure_put_tab(procedures)
    with op_tabs[3]:
        render_medical_procedure_patch_tab(procedures)
    with op_tabs[4]:
        render_medical_procedure_delete_tab(procedures)

    card_close()


def medical_procedures_tab() -> None:
    """Render medical procedures management UI."""
    st.subheader("Medical Procedures Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        procedures = load_medical_procedures()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_medical_procedures_overview(procedures)
    render_medical_procedure_crud_workspace(procedures)


def render_surgical_interventions_overview(interventions: list[dict[str, Any]]) -> None:
    """Render compact overview and surgical intervention list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(
            f"<span class='ui-badge'>Surgical Interventions: {len(interventions)}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_surgical_interventions"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Surgical Interventions")
    if interventions:
        st.dataframe(interventions, width="stretch", hide_index=True)
    else:
        st.info("No surgical interventions available yet.")
    card_close()


def render_surgical_intervention_create_tab() -> None:
    """Render create surgical intervention operation."""
    with st.form("create_surgical_intervention_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", placeholder="SNOMED-CT concept id")
        name = st.text_input("Name", placeholder="Intervention name")
        description = st.text_area("Description", placeholder="Optional")
        submitted = st.form_submit_button("Create surgical intervention", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/surgical-interventions", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_surgical_intervention_read_tab(interventions: list[dict[str, Any]]) -> None:
    """Render read single surgical intervention operation."""
    if not interventions:
        st.info("Create at least one surgical intervention to use this operation.")
        return

    selected = st.selectbox(
        "Select surgical intervention",
        options=interventions,
        format_func=surgical_intervention_label,
        key="read_surgical_intervention_select",
    )
    if st.button("Fetch surgical intervention", width="stretch"):
        status_code, data = request_json("GET", f"/surgical-interventions/{selected['id']}")
        show_api_result(status_code, data)


def render_surgical_intervention_put_tab(interventions: list[dict[str, Any]]) -> None:
    """Render full replace surgical intervention operation."""
    if not interventions:
        st.info("Create at least one surgical intervention to use this operation.")
        return

    selected = st.selectbox(
        "Surgical intervention to replace",
        options=interventions,
        format_func=surgical_intervention_label,
        key="put_surgical_intervention_select",
    )

    with st.form("put_surgical_intervention_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", value=str(selected.get("snomed_ct_code") or ""))
        name = st.text_input("Name", value=str(selected.get("name") or ""))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace surgical intervention", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/surgical-interventions/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_surgical_intervention_patch_tab(interventions: list[dict[str, Any]]) -> None:
    """Render partial update surgical intervention operation."""
    if not interventions:
        st.info("Create at least one surgical intervention to use this operation.")
        return

    selected = st.selectbox(
        "Surgical intervention to patch",
        options=interventions,
        format_func=surgical_intervention_label,
        key="patch_surgical_intervention_select",
    )

    with st.form("patch_surgical_intervention_form"):
        use_snomed_code = st.checkbox("Update SNOMED-CT code", key="patch_surgical_intervention_use_code")
        patch_snomed_code = st.text_input(
            "SNOMED-CT code",
            value=str(selected.get("snomed_ct_code") or ""),
            key="patch_surgical_intervention_code",
        )

        use_name = st.checkbox("Update name", key="patch_surgical_intervention_use_name")
        patch_name = st.text_input(
            "Name",
            value=str(selected.get("name") or ""),
            key="patch_surgical_intervention_name",
        )

        use_description = st.checkbox("Update description", key="patch_surgical_intervention_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_surgical_intervention_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_snomed_code:
                payload["snomed_ct_code"] = patch_snomed_code.strip()
            if use_name:
                payload["name"] = patch_name.strip()
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/surgical-interventions/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_surgical_intervention_delete_tab(interventions: list[dict[str, Any]]) -> None:
    """Render delete surgical intervention operation."""
    if not interventions:
        st.info("Create at least one surgical intervention to use this operation.")
        return

    selected = st.selectbox(
        "Surgical intervention to delete",
        options=interventions,
        format_func=surgical_intervention_label,
        key="delete_surgical_intervention_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_surgical_intervention_confirm",
    )
    if st.button("Delete surgical intervention", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/surgical-interventions/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_surgical_intervention_crud_workspace(interventions: list[dict[str, Any]]) -> None:
    """Render surgical intervention CRUD operations in compact tabs."""
    card_open()
    section_title("Surgical Interventions CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_surgical_intervention_create_tab()
    with op_tabs[1]:
        render_surgical_intervention_read_tab(interventions)
    with op_tabs[2]:
        render_surgical_intervention_put_tab(interventions)
    with op_tabs[3]:
        render_surgical_intervention_patch_tab(interventions)
    with op_tabs[4]:
        render_surgical_intervention_delete_tab(interventions)

    card_close()


def surgical_interventions_tab() -> None:
    """Render surgical interventions management UI."""
    st.subheader("Surgical Interventions Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        interventions = load_surgical_interventions()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_surgical_interventions_overview(interventions)
    render_surgical_intervention_crud_workspace(interventions)


def render_complications_overview(complications: list[dict[str, Any]]) -> None:
    """Render compact overview and complication list."""
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"<span class='ui-badge'>Complications: {len(complications)}</span>", unsafe_allow_html=True)
        st.markdown("<span class='ui-badge'>Operations: GET, POST, PUT, PATCH, DELETE</span>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Refresh now", width="stretch", key="refresh_complications"):
            refresh_data()

    card_open(compact=True)
    section_title("Current Complications")
    if complications:
        st.dataframe(complications, width="stretch", hide_index=True)
    else:
        st.info("No complications available yet.")
    card_close()


def render_complication_create_tab() -> None:
    """Render create complication operation."""
    with st.form("create_complication_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", placeholder="SNOMED-CT concept id")
        name = st.text_input("Name", placeholder="Complication name")
        description = st.text_area("Description", placeholder="Optional")
        submitted = st.form_submit_button("Create complication", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("POST", "/complications", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_complication_read_tab(complications: list[dict[str, Any]]) -> None:
    """Render read single complication operation."""
    if not complications:
        st.info("Create at least one complication to use this operation.")
        return

    selected = st.selectbox(
        "Select complication",
        options=complications,
        format_func=complication_label,
        key="read_complication_select",
    )
    if st.button("Fetch complication", width="stretch"):
        status_code, data = request_json("GET", f"/complications/{selected['id']}")
        show_api_result(status_code, data)


def render_complication_put_tab(complications: list[dict[str, Any]]) -> None:
    """Render full replace complication operation."""
    if not complications:
        st.info("Create at least one complication to use this operation.")
        return

    selected = st.selectbox(
        "Complication to replace",
        options=complications,
        format_func=complication_label,
        key="put_complication_select",
    )

    with st.form("put_complication_form"):
        snomed_ct_code = st.text_input("SNOMED-CT code", value=str(selected.get("snomed_ct_code") or ""))
        name = st.text_input("Name", value=str(selected.get("name") or ""))
        description = st.text_area("Description", value=str(selected.get("description") or ""))
        submitted = st.form_submit_button("Replace complication", width="stretch")

        if submitted:
            payload = {
                "snomed_ct_code": snomed_ct_code.strip(),
                "name": name.strip(),
                "description": optional_text(description),
            }
            status_code, data = request_json("PUT", f"/complications/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_complication_patch_tab(complications: list[dict[str, Any]]) -> None:
    """Render partial update complication operation."""
    if not complications:
        st.info("Create at least one complication to use this operation.")
        return

    selected = st.selectbox(
        "Complication to patch",
        options=complications,
        format_func=complication_label,
        key="patch_complication_select",
    )

    with st.form("patch_complication_form"):
        use_snomed_code = st.checkbox("Update SNOMED-CT code", key="patch_complication_use_code")
        patch_snomed_code = st.text_input(
            "SNOMED-CT code",
            value=str(selected.get("snomed_ct_code") or ""),
            key="patch_complication_code",
        )

        use_name = st.checkbox("Update name", key="patch_complication_use_name")
        patch_name = st.text_input(
            "Name",
            value=str(selected.get("name") or ""),
            key="patch_complication_name",
        )

        use_description = st.checkbox("Update description", key="patch_complication_use_description")
        patch_description = st.text_area(
            "Description",
            value=str(selected.get("description") or ""),
            key="patch_complication_description",
        )

        submitted = st.form_submit_button("Apply patch", width="stretch")

        if submitted:
            payload: dict[str, Any] = {}
            if use_snomed_code:
                payload["snomed_ct_code"] = patch_snomed_code.strip()
            if use_name:
                payload["name"] = patch_name.strip()
            if use_description:
                payload["description"] = optional_text(patch_description)

            status_code, data = request_json("PATCH", f"/complications/{selected['id']}", payload)
            show_api_result(status_code, data)
            if 200 <= status_code < 300:
                refresh_data()


def render_complication_delete_tab(complications: list[dict[str, Any]]) -> None:
    """Render delete complication operation."""
    if not complications:
        st.info("Create at least one complication to use this operation.")
        return

    selected = st.selectbox(
        "Complication to delete",
        options=complications,
        format_func=complication_label,
        key="delete_complication_select",
    )
    confirm_delete = st.checkbox(
        "I understand this action cannot be undone",
        key="delete_complication_confirm",
    )
    if st.button("Delete complication", type="primary", disabled=not confirm_delete, width="stretch"):
        status_code, data = request_json("DELETE", f"/complications/{selected['id']}")
        show_api_result(status_code, data)
        if 200 <= status_code < 300:
            refresh_data()


def render_complication_crud_workspace(complications: list[dict[str, Any]]) -> None:
    """Render complication CRUD operations in compact tabs."""
    card_open()
    section_title("Complications CRUD Workspace")
    op_tabs = st.tabs(["Create (POST)", "Read One (GET)", "Replace (PUT)", "Patch (PATCH)", "Delete (DELETE)"])

    with op_tabs[0]:
        render_complication_create_tab()
    with op_tabs[1]:
        render_complication_read_tab(complications)
    with op_tabs[2]:
        render_complication_put_tab(complications)
    with op_tabs[3]:
        render_complication_patch_tab(complications)
    with op_tabs[4]:
        render_complication_delete_tab(complications)

    card_close()


def complications_tab() -> None:
    """Render complications management UI."""
    st.subheader("Complications Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    try:
        complications = load_complications()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_complications_overview(complications)
    render_complication_crud_workspace(complications)


def case_export_tab() -> None:
    """Render case export UI that generates markdown and PDF downloads for a selected case."""
    st.caption(f"Backend API: {API_BASE_URL}")
    try:
        burn_unit_cases = load_burn_unit_cases()
        patients = load_patients()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    render_case_export_module(
        burn_unit_cases=burn_unit_cases,
        patients=patients,
        load_addresses=load_addresses,
        load_pathologies=load_pathologies,
        load_patient_pathologies=load_patient_pathologies,
        load_medications=load_medications,
        load_patient_medications=load_patient_medications,
        load_provenance_destinations=load_provenance_destinations,
        load_burn_etiologies=load_burn_etiologies,
        load_case_burns=load_case_burns,
        load_case_associated_injuries=load_case_associated_injuries,
        load_case_infections=load_case_infections,
        load_case_antibiotics=load_case_antibiotics,
        load_case_procedures=load_case_procedures,
        load_case_surgical_interventions=load_case_surgical_interventions,
        load_case_complications=load_case_complications,
        load_case_microbiology=load_case_microbiology,
        load_infections=load_infections,
        load_antibiotics=load_antibiotics,
        load_medical_procedures=load_medical_procedures,
        load_surgical_interventions=load_surgical_interventions,
        load_complications=load_complications,
        load_microbiology_specimens=load_microbiology_specimens,
        load_microbiology_agents=load_microbiology_agents,
        load_burn_depths=load_burn_depths,
        load_anatomic_locations=load_anatomic_locations,
    )


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Burn Unit UI", layout="wide")
    inject_style()

    st.title("Burn Unit Database")
    st.caption("Prioritized navigation: main overviews, core records, and grouped lookup tables")

    page = st.sidebar.radio(
        "Navigate",
        options=["Main", "Core Records", "Lookup Tables"],
        index=0,
    )

    if page == "Main":
        main_tabs = st.tabs(["Burn Unit Case Overview", "Patient Overview", "Case Export"])
        with main_tabs[0]:
            burn_unit_case_overview_tab()
        with main_tabs[1]:
            patient_overview_tab()
        with main_tabs[2]:
            case_export_tab()

    elif page == "Core Records":
        core_tabs = st.tabs(["Burn Unit Cases", "Patients"])
        with core_tabs[0]:
            burn_unit_cases_tab()
        with core_tabs[1]:
            patients_tab()

    else:
        st.subheader("Lookup Tables")
        st.caption("Grouped by workflow to keep CRUD operations easier to find.")

        lookup_groups = st.tabs(["Burn Clinical", "Patient and System"])

        with lookup_groups[0]:
            clinical_tabs = st.tabs(
                [
                    "Infections",
                    "Antibiotics",
                    "Medical Procedures",
                    "Surgical Interventions",
                    "Complications",
                    "Microbiology Specimens",
                    "Microbiology Agents",
                    "Burn Etiologies",
                ]
            )
            with clinical_tabs[0]:
                infections_tab()
            with clinical_tabs[1]:
                antibiotics_tab()
            with clinical_tabs[2]:
                medical_procedures_tab()
            with clinical_tabs[3]:
                surgical_interventions_tab()
            with clinical_tabs[4]:
                complications_tab()
            with clinical_tabs[5]:
                microbiology_specimens_tab()
            with clinical_tabs[6]:
                microbiology_agents_tab()
            with clinical_tabs[7]:
                burn_etiologies_tab()

        with lookup_groups[1]:
            support_tabs = st.tabs(["Pathologies", "Medications", "Provenance/Destination"])
            with support_tabs[0]:
                pathologies_tab()
            with support_tabs[1]:
                medications_tab()
            with support_tabs[2]:
                provenance_destinations_tab()


if __name__ == "__main__":
    main()


