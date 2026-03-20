"""Streamlit frontend for managing patients via the FastAPI backend."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st

ALLOWED_GENDERS = ["M", "F", "other"]
ALLOWED_PATHOLOGY_STATUSES = ["Active", "Inactive"]
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
def load_medications() -> list[dict[str, Any]]:
    """Load all medications from API."""
    status, data = request_json("GET", "/medications")
    if status != 200:
        raise RuntimeError(f"Could not load medications: {data}")
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
    load_medications.clear()
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

    with st.form("patch_patient_form"):
        use_name = st.checkbox("Update name")
        patch_name = st.text_input("Name", value=str(selected.get("name", "")))

        use_birth = st.checkbox("Update birth date")
        patch_birth = st.text_input(
            "Birth date (YYYY-MM-DD)",
            value=birth_date_text(selected.get("birth_date")),
            key="patch_birth_date",
        )

        use_gender = st.checkbox("Update gender")
        patch_gender = st.selectbox(
            "Gender",
            options=ALLOWED_GENDERS,
            index=ALLOWED_GENDERS.index(selected.get("gender")) if selected.get("gender") in ALLOWED_GENDERS else 0,
            key="patch_gender",
        )

        use_address = st.checkbox("Update address")
        patch_address = st.selectbox(
            "Address (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            index=address_option_index(addr_opts, selected.get("address")),
            key="patch_address_select",
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


def patient_pathology_row_label(row: dict[str, Any], pathologies_by_id: dict[int, dict[str, Any]]) -> str:
    """Build readable association label for patient overview selectors."""
    pathology_id = row.get("pathology_id")
    pathology_name = pathologies_by_id.get(pathology_id, {}).get("name", "Unknown pathology")
    severity = row.get("severity") or "-"
    diagnosed_date = row.get("diagnosed_date") or "-"
    return f"pathology {pathology_id} ({pathology_name}) | severity={severity} | diagnosed={diagnosed_date}"


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
        associations = load_patient_pathologies()
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

    render_patient_pathologies_section(selected_patient, pathologies, associations)
    render_future_associations_placeholder()


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Burn Unit UI", layout="wide")
    inject_style()

    st.title("Burn Unit Database")
    st.caption("Unified light theme with compact CRUD workflow")

    tabs = st.tabs(["Patient Overview", "Patients", "Pathologies", "Medications"])
    with tabs[0]:
        patient_overview_tab()
    with tabs[1]:
        patients_tab()
    with tabs[2]:
        pathologies_tab()
    with tabs[3]:
        medications_tab()


if __name__ == "__main__":
    main()
