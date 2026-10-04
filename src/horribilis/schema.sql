CREATE TABLE IF NOT EXISTS specimens (
    guid TEXT PRIMARY KEY CHECK (guid GLOB '[A-Za-z]*:[A-Za-z]*:[^:]*'),
    scientific_name TEXT KEY,
    collectors TEXT,
    collected_date DATE,

    country TEXT,
    state_prov TEXT,
    county TEXT,
    spec_locality TEXT,
    dec_lat REAL,
    dec_long REAL,
    coordinate_uncertainty REAL,

    sex TEXT,
    total_length REAL,
    tail_length REAL,
    hind_foot_with_claw REAL,
    ear_from_notch REAL,
    ear_from_crown REAL,
    tragus_length REAL,
    forearm_length REAL,
    weight REAL,

    life_stage TEXT,
    testes_length REAL,
    testes_width REAL,
    embryo_count INTEGER,
    embryo_count_left INTEGER,
    embryo_count_right INTEGER,
    crown_rump_length REAL,
    scars TEXT,

    unformatted_measurements TEXT,
    reproductive_data TEXT,

    source TEXT NOT NULL,
    ranges_date DATE,
    initials TEXT
);

CREATE INDEX IF NOT EXISTS idx_specimens_scientific_name ON specimens(scientific_name);