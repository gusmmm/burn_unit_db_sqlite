"""Independent Streamlit module for exporting one burn-unit case to Markdown and PDF."""

from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Any, Callable

import streamlit as st
from fpdf import FPDF  # type: ignore[import-not-found]


def _safe_filename(value: str, fallback: str) -> str:
    """Return a filesystem-safe filename stem."""
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("._")
    return stem or fallback


def _fmt(value: Any) -> str:
    """Format values for display/export."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def _escape_md(value: Any) -> str:
    """Escape markdown table-special characters."""
    return _fmt(value).replace("|", "\\|").replace("\n", " ").strip()


def _build_md_table(columns: list[str], rows: list[dict[str, Any]]) -> str:
    """Build a markdown table from columns and row dictionaries."""
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    if not rows:
        return header + "\n" + divider + "\n| " + " | ".join(["-"] * len(columns)) + " |"

    body_lines = []
    for row in rows:
        body_lines.append("| " + " | ".join(_escape_md(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, divider, *body_lines])


def _build_pdf_table(pdf: FPDF, title: str, columns: list[str], rows: list[dict[str, Any]]) -> None:
    """Write a readable table into a PDF document with adaptive widths and wrapping."""

    def wrap_cell_text(text: Any, max_width: float) -> list[str]:
        """Wrap text to fit inside a PDF table cell width."""
        raw_text = _fmt(text)
        if not raw_text:
            return [""]

        usable_width = max(max_width, 2.0)
        normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = normalized.split("\n")
        wrapped_lines: list[str] = []

        for paragraph in paragraphs:
            words = paragraph.split()
            if not words:
                wrapped_lines.append("")
                continue

            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if pdf.get_string_width(candidate) <= usable_width:
                    current = candidate
                    continue

                if current:
                    wrapped_lines.append(current)
                    current = ""

                # Split very long tokens (no spaces) by character width.
                chunk = ""
                for char in word:
                    next_chunk = f"{chunk}{char}"
                    if pdf.get_string_width(next_chunk) <= usable_width:
                        chunk = next_chunk
                    else:
                        if chunk:
                            wrapped_lines.append(chunk)
                        chunk = char
                current = chunk

            if current:
                wrapped_lines.append(current)

        return wrapped_lines or [""]

    def column_weights(table_rows: list[dict[str, Any]], pad_x: float) -> list[float]:
        """Estimate preferred column widths based on headers and sampled rows."""
        sample_rows = table_rows[:40]
        weights: list[float] = []
        for col in columns:
            header_w = pdf.get_string_width(_fmt(col))
            body_w = 0.0
            for row in sample_rows:
                cell_lines = _fmt(row.get(col, "")).replace("\r\n", "\n").replace("\r", "\n").split("\n")
                longest = max((pdf.get_string_width(line.strip()) for line in cell_lines), default=0.0)
                if longest > body_w:
                    body_w = longest
            weights.append(max(header_w * 1.15, body_w * 0.70) + (2 * pad_x))
        return weights

    def normalize_widths(weights: list[float], page_width: float, min_width: float) -> list[float]:
        """Fit preferred widths to available space while preserving readability."""
        if not weights:
            return []

        widths = [max(min_width, weight) for weight in weights]
        total = sum(widths)

        if total < page_width:
            slack = page_width - total
            weight_total = sum(weights) or float(len(widths))
            for idx, weight in enumerate(weights):
                widths[idx] += slack * (weight / weight_total)
            return widths

        if total > page_width:
            deficit = total - page_width
            shrinkable = [max(0.0, width - min_width) for width in widths]
            shrink_total = sum(shrinkable)
            if shrink_total > 0:
                ratio = min(1.0, deficit / shrink_total)
                for idx, amount in enumerate(shrinkable):
                    widths[idx] -= amount * ratio

        final_total = sum(widths)
        if final_total > page_width:
            # Last-resort fallback for many columns on narrow pages.
            uniform = page_width / len(widths)
            widths = [uniform for _ in widths]
        return widths

    def draw_header(col_widths: list[float], line_height: float, pad_x: float, pad_y: float) -> None:
        """Draw wrapped and filled table header row."""
        pdf.set_font("Helvetica", "B", header_font_size)
        header_lines = [
            wrap_cell_text(col, width - (2 * pad_x))
            for col, width in zip(columns, col_widths)
        ]
        header_height = (max(len(lines) for lines in header_lines) * line_height) + (2 * pad_y)

        if pdf.get_y() + header_height > pdf.page_break_trigger:
            pdf.add_page()

        start_x = pdf.l_margin
        row_top_y = pdf.get_y()
        pdf.set_x(start_x)

        pdf.set_fill_color(232, 236, 240)
        for header_col_lines, width in zip(header_lines, col_widths):
            cell_x = pdf.get_x()
            pdf.rect(cell_x, row_top_y, width, header_height, style="DF")
            pdf.set_xy(cell_x + pad_x, row_top_y + pad_y)
            pdf.multi_cell(width - (2 * pad_x), line_height, "\n".join(header_col_lines), border=0)
            pdf.set_xy(cell_x + width, row_top_y)

        pdf.set_xy(start_x, row_top_y + header_height)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")

    table_rows = rows if rows else [{col: "-" for col in columns}]
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    wide_table = len(columns) >= 6
    header_font_size = 8 if wide_table else 9
    body_font_size = 8 if wide_table else 9
    line_height = 4.2 if wide_table else 4.6
    pad_x = 1.4
    pad_y = 1.2

    pdf.set_font("Helvetica", "", body_font_size)
    min_width = 18.0 if wide_table else 22.0
    weights = column_weights(table_rows, pad_x)

    if len(columns) == 2 and {c.lower() for c in columns} == {"field", "value"}:
        col_widths = [max(36.0, page_width * 0.33), min(page_width * 0.67, page_width - 36.0)]
    else:
        col_widths = normalize_widths(weights, page_width, min_width)

    draw_header(col_widths, line_height, pad_x, pad_y)

    pdf.set_font("Helvetica", "", body_font_size)
    for row_index, row in enumerate(table_rows):
        row_lines = [
            wrap_cell_text(row.get(col, ""), width - (2 * pad_x))
            for col, width in zip(columns, col_widths)
        ]
        row_height = (max(len(lines) for lines in row_lines) * line_height) + (2 * pad_y)

        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            draw_header(col_widths, line_height, pad_x, pad_y)
            pdf.set_font("Helvetica", "", body_font_size)

        start_x = pdf.l_margin
        row_top_y = pdf.get_y()
        pdf.set_x(start_x)

        if row_index % 2 == 0:
            pdf.set_fill_color(248, 249, 250)
        else:
            pdf.set_fill_color(255, 255, 255)

        for cell_lines, width in zip(row_lines, col_widths):
            cell_x = pdf.get_x()
            pdf.rect(cell_x, row_top_y, width, row_height, style="DF")
            pdf.set_xy(cell_x + pad_x, row_top_y + pad_y)
            pdf.multi_cell(width - (2 * pad_x), line_height, "\n".join(cell_lines), border=0)
            pdf.set_xy(cell_x + width, row_top_y)

        pdf.set_xy(start_x, row_top_y + row_height)

    pdf.ln(3)


def _case_label(case_row: dict[str, Any], patients_by_id: dict[int, dict[str, Any]]) -> str:
    """Build a readable label for burn unit case selection."""
    patient_id = int(case_row.get("patient_id") or -1)
    patient_name = patients_by_id.get(patient_id, {}).get("name", "Unknown patient")
    admission_date = case_row.get("admission_date") or "no-admission-date"
    return f"Case {case_row.get('id')} | Patient {patient_id} ({patient_name}) | Admission {admission_date}"


def _collect_export_bundle(
    selected_case: dict[str, Any],
    patients: list[dict[str, Any]],
    load_addresses: Callable[[], list[dict[str, Any]]],
    load_pathologies: Callable[[], list[dict[str, Any]]],
    load_patient_pathologies: Callable[[], list[dict[str, Any]]],
    load_medications: Callable[[], list[dict[str, Any]]],
    load_patient_medications: Callable[[], list[dict[str, Any]]],
    load_provenance_destinations: Callable[[], list[dict[str, Any]]],
    load_burn_etiologies: Callable[[], list[dict[str, Any]]],
    load_case_burns: Callable[[int | None], list[dict[str, Any]]],
    load_case_associated_injuries: Callable[[int], list[dict[str, Any]]],
    load_case_infections: Callable[[int | None], list[dict[str, Any]]],
    load_case_antibiotics: Callable[[int | None], list[dict[str, Any]]],
    load_case_procedures: Callable[[int | None], list[dict[str, Any]]],
    load_case_surgical_interventions: Callable[[int | None], list[dict[str, Any]]],
    load_case_complications: Callable[[int | None], list[dict[str, Any]]],
    load_case_microbiology: Callable[[int | None], list[dict[str, Any]]],
    load_infections: Callable[[], list[dict[str, Any]]],
    load_antibiotics: Callable[[], list[dict[str, Any]]],
    load_medical_procedures: Callable[[], list[dict[str, Any]]],
    load_surgical_interventions: Callable[[], list[dict[str, Any]]],
    load_complications: Callable[[], list[dict[str, Any]]],
    load_microbiology_specimens: Callable[[], list[dict[str, Any]]],
    load_microbiology_agents: Callable[[], list[dict[str, Any]]],
    load_burn_depths: Callable[[], list[dict[str, Any]]],
    load_anatomic_locations: Callable[[], list[dict[str, Any]]],
) -> dict[str, Any]:
    """Collect all patient and case linked data required for an export."""
    case_id = int(selected_case["id"])
    patient_id = int(selected_case["patient_id"])

    patient = next((row for row in patients if row.get("id") == patient_id), {"id": patient_id})

    pathologies = load_pathologies()
    pathologies_by_id = {row["id"]: row for row in pathologies if row.get("id") is not None}

    medications = load_medications()
    medications_by_id = {row["id"]: row for row in medications if row.get("id") is not None}

    addresses = load_addresses()
    addresses_by_id = {row["id"]: row for row in addresses if row.get("id") is not None}

    provenance = load_provenance_destinations()
    provenance_by_id = {row["id"]: row for row in provenance if row.get("id") is not None}

    etiologies = load_burn_etiologies()
    etiology_by_id = {row["id"]: row for row in etiologies if row.get("id") is not None}

    infections = load_infections()
    infections_by_id = {row["id"]: row for row in infections if row.get("id") is not None}

    antibiotics = load_antibiotics()
    antibiotics_by_id = {row["id"]: row for row in antibiotics if row.get("id") is not None}

    med_procedures = load_medical_procedures()
    procedures_by_id = {row["id"]: row for row in med_procedures if row.get("id") is not None}

    interventions = load_surgical_interventions()
    interventions_by_id = {row["id"]: row for row in interventions if row.get("id") is not None}

    complications = load_complications()
    complications_by_id = {row["id"]: row for row in complications if row.get("id") is not None}

    specimens = load_microbiology_specimens()
    specimens_by_id = {row["id"]: row for row in specimens if row.get("id") is not None}

    agents = load_microbiology_agents()
    agents_by_id = {row["id"]: row for row in agents if row.get("id") is not None}

    burn_depths = load_burn_depths()
    burn_depths_by_id = {row["id"]: row for row in burn_depths if row.get("id") is not None}

    anatomic_locations = load_anatomic_locations()
    anatomic_locations_by_id = {row["id"]: row for row in anatomic_locations if row.get("id") is not None}

    patient_pathologies = [
        row for row in load_patient_pathologies() if row.get("patient_id") == patient_id
    ]
    patient_medications = [
        row for row in load_patient_medications() if row.get("patient_id") == patient_id
    ]

    case_burns = load_case_burns(case_id)
    case_associated_injuries = load_case_associated_injuries(case_id)
    case_infections = load_case_infections(case_id)
    case_antibiotics = load_case_antibiotics(case_id)
    case_procedures = load_case_procedures(case_id)
    case_surgical_interventions = load_case_surgical_interventions(case_id)
    case_complications = load_case_complications(case_id)
    case_microbiology = load_case_microbiology(case_id)

    return {
        "patient": patient,
        "case": selected_case,
        "resolved": {
            "admission_provenance": provenance_by_id.get(selected_case.get("admission_provenance"), {}),
            "release_destination": provenance_by_id.get(selected_case.get("release_destination"), {}),
            "burn_etiology": etiology_by_id.get(selected_case.get("burn_etiology"), {}),
            "patient_address": addresses_by_id.get(patient.get("address"), {}),
        },
        "patient_pathologies": [
            {
                "Pathology ID": row.get("pathology_id"),
                "Pathology": pathologies_by_id.get(row.get("pathology_id"), {}).get("name", "Unknown"),
                "Diagnosed date": row.get("diagnosed_date"),
                "Severity": row.get("severity"),
            }
            for row in patient_pathologies
        ],
        "patient_medications": [
            {
                "Medication ID": row.get("medication_id"),
                "Medication": medications_by_id.get(row.get("medication_id"), {}).get("name", "Unknown"),
                "ATC": medications_by_id.get(row.get("medication_id"), {}).get("ATC_code", ""),
                "Prescribed date": row.get("prescribed_date"),
                "Dosage": row.get("dosage"),
            }
            for row in patient_medications
        ],
        "case_burns": [
            {
                "Depth": (
                    f"{row.get('burn_depth_id')} - "
                    f"{burn_depths_by_id.get(row.get('burn_depth_id'), {}).get('depth_new', 'Unknown')}"
                ),
                "Location": (
                    f"{row.get('anatomic_location_id')} - "
                    f"{anatomic_locations_by_id.get(row.get('anatomic_location_id'), {}).get('name', 'Unknown')}"
                ),
                "Note": row.get("note"),
            }
            for row in case_burns
        ],
        "case_associated_injuries": [
            {
                "Injury ID": row.get("injury_id"),
                "Injury": pathologies_by_id.get(row.get("injury_id"), {}).get("name", "Unknown"),
                "Date": row.get("date_of_injury"),
                "Note": row.get("note"),
            }
            for row in case_associated_injuries
        ],
        "case_infections": [
            {
                "Infection ID": row.get("infection_id"),
                "Infection": infections_by_id.get(row.get("infection_id"), {}).get("name", "Unknown"),
                "Date": row.get("date_of_infection"),
                "Note": row.get("note"),
            }
            for row in case_infections
        ],
        "case_antibiotics": [
            {
                "Antibiotic ID": row.get("antibiotic_id"),
                "Antibiotic": antibiotics_by_id.get(row.get("antibiotic_id"), {}).get("name", "Unknown"),
                "Indication": (
                    ""
                    if row.get("indication") is None
                    else (
                        f"{row.get('indication')} - "
                        f"{infections_by_id.get(row.get('indication'), {}).get('name', 'Unknown')}"
                    )
                ),
                "Date started": row.get("date_started"),
                "Date stopped": row.get("date_stopped"),
                "Note": row.get("note"),
            }
            for row in case_antibiotics
        ],
        "case_procedures": [
            {
                "Procedure row ID": row.get("id"),
                "Procedure ID": row.get("procedure_id"),
                "Procedure": procedures_by_id.get(row.get("procedure_id"), {}).get("name", "Unknown"),
                "Date started": row.get("date_started"),
                "Date stopped": row.get("date_stopped"),
                "Before admission": _fmt(bool(row.get("before_admission"))),
                "Note": row.get("note"),
            }
            for row in case_procedures
        ],
        "case_surgical_interventions": [
            {
                "Intervention row ID": row.get("id"),
                "Intervention ID": row.get("intervention_id"),
                "Intervention": interventions_by_id.get(row.get("intervention_id"), {}).get("name", "Unknown"),
                "Location": (
                    ""
                    if row.get("location") is None
                    else (
                        f"{row.get('location')} - "
                        f"{anatomic_locations_by_id.get(row.get('location'), {}).get('name', 'Unknown')}"
                    )
                ),
                "Date started": row.get("date_started"),
                "Date stopped": row.get("date_stopped"),
                "Note": row.get("note"),
            }
            for row in case_surgical_interventions
        ],
        "case_complications": [
            {
                "Complication ID": row.get("complication_id"),
                "Complication": complications_by_id.get(row.get("complication_id"), {}).get("name", "Unknown"),
                "Date started": row.get("date_started"),
                "Note": row.get("note"),
            }
            for row in case_complications
        ],
        "case_microbiology": [
            {
                "Row ID": row.get("id"),
                "Specimen": (
                    f"{row.get('specimen_id')} - "
                    f"{specimens_by_id.get(row.get('specimen_id'), {}).get('specimen_type', 'Unknown')}"
                ),
                "Microorganism": (
                    f"{row.get('microorganism_id')} - "
                    f"{agents_by_id.get(row.get('microorganism_id'), {}).get('name', 'Unknown')}"
                ),
                "Hospital test": row.get("hospital_test_id"),
                "Collection date": row.get("date_of_collection"),
                "Report date": row.get("date_of_reporting"),
                "Note": row.get("note"),
            }
            for row in case_microbiology
        ],
    }


def _build_markdown(bundle: dict[str, Any]) -> str:
    """Build a machine-readable markdown report for one case."""
    patient = bundle["patient"]
    case_row = bundle["case"]
    resolved = bundle["resolved"]
    address_text = ""
    if patient.get("address") is not None:
        address_text = (
            f"{patient.get('address')} - "
            f"{resolved.get('patient_address', {}).get('municipio', 'Unknown address')}"
        )

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    sections: list[str] = []
    sections.append(f"# Burn Unit Case Export\n\nGenerated: {generated_at}")

    sections.append("## Patient")
    sections.append(
        _build_md_table(
            ["Field", "Value"],
            [
                {"Field": "Patient ID", "Value": patient.get("id")},
                {"Field": "Name", "Value": patient.get("name")},
                {"Field": "Birth date", "Value": patient.get("birth_date")},
                {"Field": "Gender", "Value": patient.get("gender")},
                {"Field": "Address", "Value": address_text},
            ],
        )
    )

    sections.append("## Burn Unit Case")
    sections.append(
        _build_md_table(
            ["Field", "Value"],
            [
                {"Field": "Case ID", "Value": case_row.get("id")},
                {"Field": "Patient ID", "Value": case_row.get("patient_id")},
                {"Field": "TBSA burned", "Value": case_row.get("TBSA_burned")},
                {"Field": "Admission date", "Value": case_row.get("admission_date")},
                {"Field": "Burn date", "Value": case_row.get("burn_date")},
                {"Field": "Release date", "Value": case_row.get("release_date")},
                {
                    "Field": "Admission provenance",
                    "Value": (
                        ""
                        if case_row.get("admission_provenance") is None
                        else (
                            f"{case_row.get('admission_provenance')} - "
                            f"{resolved.get('admission_provenance', {}).get('name', '')}"
                        )
                    ),
                },
                {
                    "Field": "Release destination",
                    "Value": (
                        ""
                        if case_row.get("release_destination") is None
                        else (
                            f"{case_row.get('release_destination')} - "
                            f"{resolved.get('release_destination', {}).get('name', '')}"
                        )
                    ),
                },
                {
                    "Field": "Burn etiology",
                    "Value": (
                        ""
                        if case_row.get("burn_etiology") is None
                        else (
                            f"{case_row.get('burn_etiology')} - "
                            f"{resolved.get('burn_etiology', {}).get('name', '')}"
                        )
                    ),
                },
                {"Field": "Burn mechanism", "Value": case_row.get("burn_mecanism")},
                {"Field": "Violence related", "Value": case_row.get("violence_related")},
                {"Field": "Suicide attempt", "Value": case_row.get("suicide_attempt")},
                {"Field": "Accident type", "Value": case_row.get("accident_type")},
                {"Field": "Wildfire", "Value": case_row.get("wildfire")},
                {"Field": "Bonfire", "Value": case_row.get("bonfire_fogueira")},
                {"Field": "Fireplace", "Value": case_row.get("fireplace_lareira")},
                {"Field": "Special forces", "Value": case_row.get("special_forces")},
                {"Field": "Note", "Value": case_row.get("note")},
            ],
        )
    )

    mapping = [
        ("Patient Pathologies", bundle["patient_pathologies"]),
        ("Patient Medications", bundle["patient_medications"]),
        ("Case Burns", bundle["case_burns"]),
        ("Case Associated Injuries", bundle["case_associated_injuries"]),
        ("Case Infections", bundle["case_infections"]),
        ("Case Antibiotics", bundle["case_antibiotics"]),
        ("Case Procedures", bundle["case_procedures"]),
        ("Case Surgical Interventions", bundle["case_surgical_interventions"]),
        ("Case Complications", bundle["case_complications"]),
        ("Case Microbiology", bundle["case_microbiology"]),
    ]

    for title, rows in mapping:
        sections.append(f"## {title}")
        if rows:
            cols = list(rows[0].keys())
            sections.append(_build_md_table(cols, rows))
        else:
            sections.append("No records.")

    return "\n\n".join(sections) + "\n"


def _build_pdf(bundle: dict[str, Any]) -> bytes:
    """Build a human-readable PDF report for one case."""
    patient = bundle["patient"]
    case_row = bundle["case"]
    resolved = bundle["resolved"]
    address_text = ""
    if patient.get("address") is not None:
        address_text = (
            f"{patient.get('address')} - "
            f"{resolved.get('patient_address', {}).get('municipio', 'Unknown address')}"
        )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, "Burn Unit Case Export", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    pdf.cell(0, 7, f"Generated: {generated_at}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    patient_rows = [
        {"Field": "Patient ID", "Value": patient.get("id")},
        {"Field": "Name", "Value": patient.get("name")},
        {"Field": "Birth date", "Value": patient.get("birth_date")},
        {"Field": "Gender", "Value": patient.get("gender")},
        {"Field": "Address", "Value": address_text},
    ]
    _build_pdf_table(pdf, "Patient", ["Field", "Value"], patient_rows)

    case_rows = [
        {"Field": "Case ID", "Value": case_row.get("id")},
        {"Field": "Patient ID", "Value": case_row.get("patient_id")},
        {"Field": "TBSA burned", "Value": case_row.get("TBSA_burned")},
        {"Field": "Admission date", "Value": case_row.get("admission_date")},
        {"Field": "Burn date", "Value": case_row.get("burn_date")},
        {"Field": "Release date", "Value": case_row.get("release_date")},
        {
            "Field": "Admission provenance",
            "Value": (
                ""
                if case_row.get("admission_provenance") is None
                else (
                    f"{case_row.get('admission_provenance')} - "
                    f"{resolved.get('admission_provenance', {}).get('name', '')}"
                )
            ),
        },
        {
            "Field": "Release destination",
            "Value": (
                ""
                if case_row.get("release_destination") is None
                else (
                    f"{case_row.get('release_destination')} - "
                    f"{resolved.get('release_destination', {}).get('name', '')}"
                )
            ),
        },
        {
            "Field": "Burn etiology",
            "Value": (
                ""
                if case_row.get("burn_etiology") is None
                else (
                    f"{case_row.get('burn_etiology')} - "
                    f"{resolved.get('burn_etiology', {}).get('name', '')}"
                )
            ),
        },
        {"Field": "Burn mechanism", "Value": case_row.get("burn_mecanism")},
    ]
    _build_pdf_table(pdf, "Burn Unit Case", ["Field", "Value"], case_rows)

    mapping = [
        ("Patient Pathologies", bundle["patient_pathologies"]),
        ("Patient Medications", bundle["patient_medications"]),
        ("Case Burns", bundle["case_burns"]),
        ("Case Associated Injuries", bundle["case_associated_injuries"]),
        ("Case Infections", bundle["case_infections"]),
        ("Case Antibiotics", bundle["case_antibiotics"]),
        ("Case Procedures", bundle["case_procedures"]),
        ("Case Surgical Interventions", bundle["case_surgical_interventions"]),
        ("Case Complications", bundle["case_complications"]),
        ("Case Microbiology", bundle["case_microbiology"]),
    ]

    for title, rows in mapping:
        cols = list(rows[0].keys()) if rows else ["Info"]
        normalized_rows = rows if rows else [{"Info": "No records"}]
        _build_pdf_table(pdf, title, cols, normalized_rows)

    raw_output = pdf.output()
    if isinstance(raw_output, str):
        return raw_output.encode("latin-1")
    return bytes(raw_output)


def render_case_export_module(
    burn_unit_cases: list[dict[str, Any]],
    patients: list[dict[str, Any]],
    load_addresses: Callable[[], list[dict[str, Any]]],
    load_pathologies: Callable[[], list[dict[str, Any]]],
    load_patient_pathologies: Callable[[], list[dict[str, Any]]],
    load_medications: Callable[[], list[dict[str, Any]]],
    load_patient_medications: Callable[[], list[dict[str, Any]]],
    load_provenance_destinations: Callable[[], list[dict[str, Any]]],
    load_burn_etiologies: Callable[[], list[dict[str, Any]]],
    load_case_burns: Callable[[int | None], list[dict[str, Any]]],
    load_case_associated_injuries: Callable[[int], list[dict[str, Any]]],
    load_case_infections: Callable[[int | None], list[dict[str, Any]]],
    load_case_antibiotics: Callable[[int | None], list[dict[str, Any]]],
    load_case_procedures: Callable[[int | None], list[dict[str, Any]]],
    load_case_surgical_interventions: Callable[[int | None], list[dict[str, Any]]],
    load_case_complications: Callable[[int | None], list[dict[str, Any]]],
    load_case_microbiology: Callable[[int | None], list[dict[str, Any]]],
    load_infections: Callable[[], list[dict[str, Any]]],
    load_antibiotics: Callable[[], list[dict[str, Any]]],
    load_medical_procedures: Callable[[], list[dict[str, Any]]],
    load_surgical_interventions: Callable[[], list[dict[str, Any]]],
    load_complications: Callable[[], list[dict[str, Any]]],
    load_microbiology_specimens: Callable[[], list[dict[str, Any]]],
    load_microbiology_agents: Callable[[], list[dict[str, Any]]],
    load_burn_depths: Callable[[], list[dict[str, Any]]],
    load_anatomic_locations: Callable[[], list[dict[str, Any]]],
) -> None:
    """Render independent export controls and download actions for one selected case."""
    st.subheader("Case Export")
    st.caption("Export one burn unit case and linked patient/case data to Markdown and/or PDF.")

    if not burn_unit_cases:
        st.info("No burn unit cases available to export.")
        return

    patients_by_id = {int(row["id"]): row for row in patients if row.get("id") is not None}

    selected_case = st.selectbox(
        "Select burn unit case to export",
        options=burn_unit_cases,
        format_func=lambda row: _case_label(row, patients_by_id),
        key="case_export_select_case",
    )
    selected_formats = st.multiselect(
        "Select format(s)",
        options=["Markdown (.md)", "PDF (.pdf)"],
        default=["Markdown (.md)", "PDF (.pdf)"],
        key="case_export_format_select",
    )

    selected_case_id = int(selected_case.get("id") or -1)
    default_stem = f"case_{selected_case.get('id')}_patient_{selected_case.get('patient_id')}_export"
    last_case_key = "case_export_last_case_id"
    filename_key = "case_export_filename_stem"

    if st.session_state.get(last_case_key) != selected_case_id:
        st.session_state[filename_key] = default_stem
        st.session_state[last_case_key] = selected_case_id

    filename_stem = st.text_input(
        "Base filename (without extension)",
        key=filename_key,
    )
    submitted = st.button("Prepare export files", width="stretch", key="case_export_prepare_button")

    if not submitted:
        return

    if not selected_formats:
        st.warning("Select at least one format.")
        return

    safe_stem = _safe_filename(filename_stem, default_stem)

    try:
        bundle = _collect_export_bundle(
            selected_case=selected_case,
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
    except Exception as exc:
        st.error(f"Could not collect export data: {exc}")
        return

    markdown_content = _build_markdown(bundle)

    st.success("Export files are ready. Download below.")

    if "Markdown (.md)" in selected_formats:
        st.download_button(
            label="Download Markdown",
            data=markdown_content.encode("utf-8"),
            file_name=f"{safe_stem}.md",
            mime="text/markdown",
            key="case_export_download_markdown",
            width="stretch",
        )

    if "PDF (.pdf)" in selected_formats:
        try:
            pdf_bytes = _build_pdf(bundle)
        except Exception as exc:
            st.error(f"Could not generate PDF: {exc}")
        else:
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{safe_stem}.pdf",
                mime="application/pdf",
                key="case_export_download_pdf",
                width="stretch",
            )

    with st.expander("Preview markdown export"):
        st.code(markdown_content, language="markdown")
