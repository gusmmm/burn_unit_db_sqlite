"""Streamlit frontend for managing patients via the FastAPI backend."""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any

import requests
import streamlit as st

ALLOWED_GENDERS = ["M", "F", "other"]
API_BASE_URL = os.getenv("BURN_API_URL", "http://127.0.0.1:8000").rstrip("/")


def inject_minimal_style() -> None:
    """Apply a sober and minimalist visual style with improved contrast."""
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #eff6ff 0%, #f8fafc 40%, #ffffff 100%);
            color: #0f172a;
        }
        .block-container {
            max-width: 1040px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #0b2a4a;
            letter-spacing: 0.01em;
        }

        .crud-card {
            border: 1px solid #cfe3ff;
            border-left: 6px solid #2563eb;
            border-radius: 12px;
            background: #ffffff;
            padding: 0.8rem 0.9rem 0.2rem 0.9rem;
            margin: 0.7rem 0 1.1rem 0;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08);
        }
        .crud-card.success {
            border-left-color: #16a34a;
            border-color: #cdeed8;
            box-shadow: 0 4px 14px rgba(22, 163, 74, 0.08);
        }
        .crud-card.warn {
            border-left-color: #0f766e;
            border-color: #bfe8e2;
        }

        div[data-testid="stForm"] {
            border: 1px solid #dbeafe;
            border-radius: 10px;
            background: #ffffff;
            padding: 0.9rem 0.9rem;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div,
        .stDateInput > div > div {
            background: #f8fbff !important;
            border: 1px solid #93c5fd !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="select"] input,
        div[data-baseweb="input"] * {
            color: #0f172a !important;
        }

        .stButton > button,
        .stForm button {
            background: linear-gradient(180deg, #1d4ed8 0%, #1e40af 100%);
            color: #ffffff;
            border: 0;
            border-radius: 9px;
            font-weight: 600;
        }
        .stButton > button:hover,
        .stForm button:hover {
            background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
        }

        .stAlert {
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_open(extra_class: str = "") -> None:
    """Open a styled section wrapper for clearer CRUD separation."""
    class_name = f"crud-card {extra_class}".strip()
    st.markdown(f"<div class=\"{class_name}\">", unsafe_allow_html=True)


def section_close() -> None:
    """Close a styled section wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    """Call backend API and return status code plus parsed JSON when available."""
    url = f"{API_BASE_URL}{path}"
    response = requests.request(method=method, url=url, json=payload, timeout=15)
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


def parse_birth_date(value: Any) -> date:
    """Convert backend date string into date widget value."""
    if not value:
        return date.today()
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return date.today()


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


def show_api_result(status: int, data: Any) -> None:
    """Display API request result in a concise way."""
    if 200 <= status < 300:
        st.success(f"Success ({status})")
        st.json(data)
    else:
        st.error(f"Request failed ({status})")
        st.json(data)


def patients_tab() -> None:
    """Render patients management UI."""
    st.subheader("Patients Management")
    st.caption(f"Backend API: {API_BASE_URL}")

    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("Refresh data"):
            load_patients.clear()
            load_addresses.clear()
            st.rerun()

    try:
        patients = load_patients()
        addresses = load_addresses()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    section_open("success")
    st.markdown("### Current Patients")
    st.dataframe(patients, width="stretch")
    section_close()

    addr_opts = address_options(addresses)

    section_open()
    st.markdown("### Read One Patient (GET)")
    if patients:
        selected_for_get = st.selectbox(
            "Select patient",
            options=patients,
            format_func=patient_label,
            key="get_patient_select",
        )
        if st.button("Fetch selected patient"):
            status, data = request_json("GET", f"/patients/{selected_for_get['id']}")
            show_api_result(status, data)
    else:
        st.info("No patients available yet.")
    section_close()

    section_open("success")
    st.markdown("### Create Patient (POST)")
    with st.form("create_patient_form"):
        create_name = st.text_input("Name", placeholder="Patient full name")
        create_birth_date = st.date_input("Birth date")
        create_gender = st.selectbox("Gender", options=ALLOWED_GENDERS)
        create_address = st.selectbox(
            "Address (municipio)",
            options=addr_opts,
            format_func=lambda x: x["label"],
            key="create_address_select",
        )
        create_submit = st.form_submit_button("Create patient")

        if create_submit:
            payload = {
                "name": create_name.strip(),
                "birth_date": create_birth_date.isoformat(),
                "gender": create_gender,
                "address": create_address["id"],
            }
            status, data = request_json("POST", "/patients", payload)
            show_api_result(status, data)
            if 200 <= status < 300:
                load_patients.clear()
    section_close()

    section_open("warn")
    st.markdown("### Replace Patient Data (PUT)")
    if patients:
        selected_for_put = st.selectbox(
            "Patient to replace",
            options=patients,
            format_func=patient_label,
            key="put_patient_select",
        )
        put_default_addr = next(
            (x for x in addr_opts if x["id"] == selected_for_put.get("address")),
            addr_opts[0],
        )

        with st.form("put_patient_form"):
            put_name = st.text_input("Name", value=str(selected_for_put.get("name", "")))
            put_birth = st.date_input("Birth date", value=parse_birth_date(selected_for_put.get("birth_date")))
            put_gender = st.selectbox(
                "Gender",
                options=ALLOWED_GENDERS,
                index=ALLOWED_GENDERS.index(selected_for_put.get("gender"))
                if selected_for_put.get("gender") in ALLOWED_GENDERS
                else 0,
            )
            put_address = st.selectbox(
                "Address (municipio)",
                options=addr_opts,
                format_func=lambda x: x["label"],
                index=addr_opts.index(put_default_addr),
                key="put_address_select",
            )
            put_submit = st.form_submit_button("Update patient")

            if put_submit:
                payload = {
                    "name": put_name.strip(),
                    "birth_date": put_birth.isoformat(),
                    "gender": put_gender,
                    "address": put_address["id"],
                }
                status, data = request_json("PUT", f"/patients/{selected_for_put['id']}", payload)
                show_api_result(status, data)
                if 200 <= status < 300:
                    load_patients.clear()
    section_close()

    section_open("warn")
    st.markdown("### Partial Update (PATCH)")
    if patients:
        selected_for_patch = st.selectbox(
            "Patient to patch",
            options=patients,
            format_func=patient_label,
            key="patch_patient_select",
        )
        patch_default_addr = next(
            (x for x in addr_opts if x["id"] == selected_for_patch.get("address")),
            addr_opts[0],
        )

        with st.form("patch_patient_form"):
            use_name = st.checkbox("Update name")
            patch_name = st.text_input("Name", value=str(selected_for_patch.get("name", "")))

            use_birth = st.checkbox("Update birth date")
            patch_birth = st.date_input(
                "Birth date",
                value=parse_birth_date(selected_for_patch.get("birth_date")),
                key="patch_birth_date",
            )

            use_gender = st.checkbox("Update gender")
            patch_gender = st.selectbox(
                "Gender",
                options=ALLOWED_GENDERS,
                index=ALLOWED_GENDERS.index(selected_for_patch.get("gender"))
                if selected_for_patch.get("gender") in ALLOWED_GENDERS
                else 0,
                key="patch_gender",
            )

            use_address = st.checkbox("Update address")
            patch_address = st.selectbox(
                "Address (municipio)",
                options=addr_opts,
                format_func=lambda x: x["label"],
                index=addr_opts.index(patch_default_addr),
                key="patch_address_select",
            )

            patch_submit = st.form_submit_button("Patch patient")

            if patch_submit:
                payload: dict[str, Any] = {}
                if use_name:
                    payload["name"] = patch_name.strip()
                if use_birth:
                    payload["birth_date"] = patch_birth.isoformat()
                if use_gender:
                    payload["gender"] = patch_gender
                if use_address:
                    payload["address"] = patch_address["id"]

                status, data = request_json("PATCH", f"/patients/{selected_for_patch['id']}", payload)
                show_api_result(status, data)
                if 200 <= status < 300:
                    load_patients.clear()
    section_close()

    section_open()
    st.markdown("### Delete Patient")
    if patients:
        selected_for_delete = st.selectbox(
            "Patient to delete",
            options=patients,
            format_func=patient_label,
            key="delete_patient_select",
        )
        confirm_delete = st.checkbox("I confirm this patient should be deleted")
        if st.button("Delete patient", disabled=not confirm_delete):
            status, data = request_json("DELETE", f"/patients/{selected_for_delete['id']}")
            show_api_result(status, data)
            if 200 <= status < 300:
                load_patients.clear()
    section_close()


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Burn Unit UI", layout="wide")
    inject_minimal_style()

    st.title("Burn Unit Database")
    st.caption("Minimal, high-contrast interface for patient management")

    tabs = st.tabs(["Patients"])
    with tabs[0]:
        patients_tab()


if __name__ == "__main__":
    main()
