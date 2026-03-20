"""Streamlit frontend for managing patients via the FastAPI backend."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st

ALLOWED_GENDERS = ["M", "F", "other"]
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
    st.rerun()


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


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Burn Unit UI", layout="wide")
    inject_style()

    st.title("Burn Unit Database")
    st.caption("Unified light theme with compact CRUD workflow")

    tabs = st.tabs(["Patients"])
    with tabs[0]:
        patients_tab()


if __name__ == "__main__":
    main()
