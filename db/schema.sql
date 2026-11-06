DROP TABLE IF EXISTS doctors, specialties, consultations, patients, prescriptions, medications, allergic_to;

CREATE TABLE specialties(
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_specialties PRIMARY KEY (id),
    CONSTRAINT uk_specialties_name UNIQUE (name),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at)
);

CREATE TABLE medications(
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_medications PRIMARY KEY (id),
    CONSTRAINT uk_medications_name_dosage UNIQUE (name, dosage),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at)
);

CREATE TABLE patients(
    id INT GENERATED ALWAYS AS IDENTITY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    sex CHAR(1) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(320) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_patients PRIMARY KEY (id),
    CONSTRAINT uk_patients_email UNIQUE (email),
    CONSTRAINT ck_sex CHECK (sex in ('M', 'F', 'X')),
    CONSTRAINT ck_birth_date_before_now CHECK (birth_date <= CURRENT_DATE),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at)
);

CREATE TABLE doctors(
    id INT GENERATED ALWAYS AS IDENTITY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty_id INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_doctors PRIMARY KEY (id),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at),
    CONSTRAINT fk_doctors_specialties FOREIGN KEY (specialty_id)
        REFERENCES specialties (id) ON DELETE RESTRICT
);

CREATE TABLE consultations(
    id INT GENERATED ALWAYS AS IDENTITY,
    consultation_date TIMESTAMPTZ NOT NULL,
    reason VARCHAR(200) NOT NULL,
    note TEXT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_consultations PRIMARY KEY (id),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at),
    CONSTRAINT fk_consultations_patients FOREIGN KEY (patient_id)
        REFERENCES patients (id) ON DELETE RESTRICT,
    CONSTRAINT fk_consultations_doctors FOREIGN KEY (doctor_id)
        REFERENCES doctors (id) ON DELETE RESTRICT
);

CREATE TABLE prescriptions(
    id INT GENERATED ALWAYS AS IDENTITY,
    instruction TEXT NOT NULL,
    duration_days SMALLINT NOT NULL,
    medication_id INT NOT NULL,
    consultation_id INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_prescriptions PRIMARY KEY (id),
    CONSTRAINT ck_duration_strict_positive CHECK (duration_days > 0),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at),
    CONSTRAINT fk_prescriptions_medications FOREIGN KEY (medication_id)
        REFERENCES medications (id) ON DELETE RESTRICT,
    CONSTRAINT fk_prescriptions_consultations FOREIGN KEY (consultation_id)
        REFERENCES consultations (id) ON DELETE CASCADE
);

CREATE TABLE allergic_to(
    medication_id INT NOT NULL,
    patient_id INT NOT NULL,
    severity VARCHAR(8) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_allergic_to PRIMARY KEY (patient_id, medication_id),
    CONSTRAINT ck_severity_case CHECK (severity in ('mild', 'moderate', 'severe')),
    CONSTRAINT ck_created_before_now CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_update_before_now CHECK (updated_at <= CURRENT_TIMESTAMP),
    CONSTRAINT ck_updated_after_created CHECK (created_at <= updated_at),
    CONSTRAINT fk_allergic_to_medication FOREIGN KEY (medication_id)
        REFERENCES medications (id) ON DELETE RESTRICT,
    CONSTRAINT fk_allergic_to_patient FOREIGN KEY (patient_id)
        REFERENCES patients (id) ON DELETE CASCADE
);

CREATE INDEX idx_doctors_specialty_id ON doctors (specialty_id);
CREATE INDEX idx_consultations_patient_id ON consultations (patient_id);
CREATE INDEX idx_consultations_doctor_id ON consultations (doctor_id);
CREATE INDEX idx_prescriptions_medication_id ON prescriptions (medication_id);
CREATE INDEX idx_prescriptions_consultation_id ON prescriptions (consultation_id);
CREATE INDEX idx_allergic_to_medication_id ON allergic_to (medication_id);
CREATE INDEX idx_patients_last_name ON patients (last_name);