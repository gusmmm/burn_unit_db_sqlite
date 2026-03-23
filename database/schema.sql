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

-- Table: medications
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ATC_code TEXT UNIQUE, -- Unique ATC code for medication classification
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: patient_medications
CREATE TABLE IF NOT EXISTS patient_medications (
    patient_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    prescribed_date DATE,
    dosage TEXT,  -- e.g., "500 mg twice daily"
    PRIMARY KEY (patient_id, medication_id),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

------- NEW SECTION: Burn-specific clinical data -------

-- Table: burn_unit_clinical_data
CREATE TABLE IF NOT EXISTS burn_unit_cases (
    id INTEGER PRIMARY KEY, -- Unique identifier for each clinical data entry
    patient_id INTEGER NOT NULL, -- Reference to the patient
    TBSA_burned REAL,  -- Percentage of body surface area burned
    admission_date DATE,  -- Date of admission to the burn unit
    burn_date DATE,  -- Date of burn injury
    release_date DATE,  -- Date of discharge from the burn unit
    admission_provenance INTEGER,  -- foreign key to table provenance_destination (e.g., emergency room, transfer from another hospital)
    release_destination INTEGER,  --  foreign key to table provenance_destination (e.g., home, rehabilitation)
    burn_mecanism TEXT CHECK (burn_mecanism IN ('heat', 'electrical_discharge', 'friction','chemical','radiaton','other')),  -- Me chanism of burn injury 
    burn_etiology INTEGER,  --foreign key to table burn etiology
    violence_related BOOLEAN,  -- Whether the burn injury is related to violence
    suicide_attempt BOOLEAN,  -- Whether the burn injury is related
    accident_type TEXT CHECK (accident_type IN ('workplace', 'domestic', 'traffic', 'war', 'terrorism', 'other')),  -- Type of accident (e.g., workplace, domestic, etc.)
    wildfire BOOLEAN, 
    bonfire_fogueira BOOLEAN,
    fireplace_lareira BOOLEAN,
    note TEXT,
    special_forces TEXT CHECK (special_forces IN ('army', 'navy', 'air_force', 'firefighters', 'police', 'other')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_provenance) REFERENCES provenance_destination(id),
    FOREIGN KEY (release_destination) REFERENCES provenance_destination(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (burn_etiology) REFERENCES burn_etiology(id)
);

-- Table: provenance_destination
CREATE TABLE IF NOT EXISTS provenance_destination (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('hospital', 'department','emergency','other')),
    location INTEGER, --foreign key to addresses
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location) REFERENCES addresses(id)
);

-- Table: burn_etiology
CREATE TABLE IF NOT EXISTS burn_etiology (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- a implementar
-- Table: burn_depth
CREATE TABLE IF NOT EXISTS burn_depth (
    id INTEGER PRIMARY KEY,
    depth_new TEXT NOT NULL,
    depth_old TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: anatomic_locations
CREATE TABLE IF NOT EXISTS anatomic_locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: case_burns
-- association table between burn cases and burn characteristics (depth, location, etc.)
CREATE TABLE IF NOT EXISTS case_burns (
    case_id INTEGER NOT NULL,
    burn_depth_id INTEGER NOT NULL,
    anatomic_location_id INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (case_id, burn_depth_id, anatomic_location_id),
    FOREIGN KEY (case_id) REFERENCES burn_unit_cases(id),
    FOREIGN KEY (burn_depth_id) REFERENCES burn_depth(id),
    FOREIGN KEY (anatomic_location_id) REFERENCES anatomic_locations(id)
);


-- Table: case_associated_injuries
-- Table: interventions
-- Table: case_interventions
-- Table: infections
-- Table: case_infections
-- Table: antibiotics
-- Table: case_antibiotics
-- Table: microbiology
-- Table: case_microbiology
-- Table: procedures
-- Table: case_procedures
-- Table: complications
-- Table: case_complications