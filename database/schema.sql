-- burn unit database schema for sqlite

-- Table: patients
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    birth_date DATE,
    gender TEXT CHECK (gender IN ('M', 'F', 'other')),
    address INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (address) REFERENCES addresses(id)
);
-- Table: addresses
-- by municipio 
-- check here https://anmp.pt/municipios/municipios/municipios-de-a-a-v/
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    municipio TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: pathologies
-- SNOMED-CT reference for burn unit diagnoses
CREATE TABLE IF NOT EXISTS pathologies (
    id INTEGER PRIMARY KEY, --SNOMED-CT Concept ID 
    name TEXT NOT NULL,  -- SNOMED-CT Preferred Term (PT)
    fsn TEXT,  -- Fully Specified Name with semantic tag (e.g., "burn wound (disorder)")
    semantic_tag TEXT,  -- Category type: disorder, finding, procedure, substance, etc.
    definition TEXT,  -- Clinical/technical description from SNOMED-CT
    icd11_code TEXT,  -- ICD-11 equivalent for interoperability
    mesh_id TEXT,  -- MeSH ID for research linkage
    status TEXT CHECK (status IN ('Active', 'Inactive')) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: patient_pathologies
CREATE TABLE IF NOT EXISTS patient_pathologies (
    patient_id INTEGER NOT NULL,
    pathology_id INTEGER NOT NULL,
    diagnosed_date DATE,
    severity TEXT,  -- e.g., mild, moderate, severe (burn-unit-specific)
    PRIMARY KEY (patient_id, pathology_id),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (pathology_id) REFERENCES pathologies(id)
);

CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ATC_code TEXT UNIQUE, -- Unique ATC code for medication classification
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patient_medications (
    patient_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    prescribed_date DATE,
    dosage TEXT,  -- e.g., "500 mg twice daily"
    PRIMARY KEY (patient_id, medication_id),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);