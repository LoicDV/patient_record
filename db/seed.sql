-- =============================================================================
-- seed.sql : fictitious test data for the patient_record database
-- All people, emails and phone numbers are invented (example.com is a
-- domain reserved for documentation).
--
--
-- IDs are generated automatically and start at 1 after schema.sql, so they
-- follow the insertion order below. Foreign keys rely on that order.
--
-- Scenarios deliberately included for the JOIN queries:
--   * specialty 4 (Dermatology) has no doctor
--   * doctor 4 (Lucas Peeters) has no consultation
--   * patients 7 and 8 have no consultation
--   * medication 6 (Omeprazole) has never been prescribed
--   * consultations 2, 14 and 15 have no prescription
--   * allergy alerts: patient 5 received Amoxicillin (consultation 13)
--     and patient 3 received Ibuprofen (consultation 8) despite an allergy
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Specialties (ids 1 to 4)
-- -----------------------------------------------------------------------------
INSERT INTO specialties (name) VALUES
    ('General practice'),   -- 1
    ('Cardiology'),         -- 2
    ('Pediatrics'),         -- 3
    ('Dermatology');        -- 4 : no doctor

-- -----------------------------------------------------------------------------
-- Medications (ids 1 to 7)
-- -----------------------------------------------------------------------------
INSERT INTO medications (name, dosage) VALUES
    ('Amoxicillin', '500 mg'),          -- 1
    ('Paracetamol', '1 g'),             -- 2
    ('Ibuprofen',   '400 mg'),          -- 3
    ('Bisoprolol',  '5 mg'),            -- 4
    ('Salbutamol',  '100 mcg/dose'),    -- 5
    ('Omeprazole',  '20 mg'),           -- 6 : never prescribed
    ('Paracetamol', '500 mg');          -- 7 : same name, other dosage

-- -----------------------------------------------------------------------------
-- Patients (ids 1 to 8)
-- -----------------------------------------------------------------------------
INSERT INTO patients (first_name, last_name, birth_date, sex, phone, email) VALUES
    ('Thomas',  'Dubois',    '1985-03-14', 'M', '+32 470 00 00 01', 'thomas.dubois@example.com'),        -- 1
    ('Julie',   'Leroy',     '1992-07-02', 'F', '+32 470 00 00 02', 'julie.leroy@example.com'),          -- 2
    ('Marc',    'Willems',   '1958-11-23', 'M', '+32 470 00 00 03', 'marc.willems@example.com'),         -- 3
    ('Sarah',   'Claes',     '2017-05-09', 'F', '+32 470 00 00 04', 'claes.family@example.com'),         -- 4 : child
    ('Nicolas', 'Maes',      '1974-01-30', 'M', NULL,               'nicolas.maes@example.com'),         -- 5
    ('Camille', 'Wouters',   '1999-09-18', 'X', '+32 470 00 00 06', 'camille.wouters@example.com'),      -- 6
    ('Laura',   'Mertens',   '2001-12-05', 'F', '+32 470 00 00 07', 'laura.mertens@example.com'),        -- 7 : no consultation
    ('Antoine', 'Goossens',  '1966-04-27', 'M', NULL,               'antoine.goossens@example.com');     -- 8 : no consultation

-- -----------------------------------------------------------------------------
-- Doctors (ids 1 to 5)
-- -----------------------------------------------------------------------------
INSERT INTO doctors (first_name, last_name, specialty_id) VALUES
    ('Claire', 'Dupont',   1),  -- 1 : General practice
    ('Hugo',   'Martin',   1),  -- 2 : General practice
    ('Sofia',  'Lambert',  2),  -- 3 : Cardiology
    ('Lucas',  'Peeters',  2),  -- 4 : Cardiology, no consultation
    ('Emma',   'Janssens', 3);  -- 5 : Pediatrics

-- -----------------------------------------------------------------------------
-- Consultations (ids 1 to 15), from May to October 2026
-- -----------------------------------------------------------------------------
INSERT INTO consultations (consultation_date, reason, note, patient_id, doctor_id) VALUES
    ('2026-05-12 09:00+02', 'Persistent cough',      'Productive cough for 10 days, no fever.',            1, 1),  -- 1
    ('2026-06-02 10:30+02', 'Cough follow-up',       'Clear improvement, no further treatment needed.',    1, 1),  -- 2 : no prescription
    ('2026-09-15 14:00+02', 'Chest pain',            'ECG normal, mild tachycardia.',                      1, 3),  -- 3
    ('2026-05-20 11:00+02', 'Migraine',              'Recurring migraines, about twice a month.',          2, 2),  -- 4
    ('2026-08-04 16:30+02', 'Lower back pain',       'Pain after moving furniture.',                       2, 2),  -- 5
    ('2026-06-10 08:45+02', 'Hypertension check-up', 'Blood pressure 152/95.',                             3, 3),  -- 6
    ('2026-09-09 09:15+02', 'Hypertension follow-up','Blood pressure 138/86, treatment continued.',        3, 3),  -- 7
    ('2026-10-01 10:00+02', 'Flu symptoms',          'Fever 38.9, body aches.',                            3, 1),  -- 8 : allergy alert
    ('2026-05-28 15:00+02', 'Ear infection',         'Acute otitis, left ear.',                            4, 5),  -- 9
    ('2026-07-14 15:30+02', 'Asthma attack',         'Exercise-induced asthma.',                           4, 5),  -- 10
    ('2026-10-06 14:45+02', 'Asthma follow-up',      'Well controlled, inhaler renewed.',                  4, 5),  -- 11
    ('2026-06-25 17:00+02', 'Sprained ankle',        'Right ankle, no fracture suspected.',                5, 2),  -- 12
    ('2026-08-19 09:30+02', 'Sore throat',           'Suspected bacterial angina.',                        5, 1),  -- 13 : allergy alert
    ('2026-07-07 13:00+02', 'Annual check-up',       NULL,                                                 6, 2),  -- 14 : no prescription
    ('2026-10-20 11:15+02', 'Skin rash',             'Referred to a dermatologist.',                       6, 1);  -- 15 : no prescription

-- -----------------------------------------------------------------------------
-- Prescriptions (20 lines)
-- -----------------------------------------------------------------------------
INSERT INTO prescriptions (instruction, duration_days, medication_id, consultation_id) VALUES
    ('1 tablet 3 times a day',                        7,  1, 1),
    ('1 tablet up to 3 times a day if fever',         5,  2, 1),
    ('1 tablet every morning',                        30, 4, 3),
    ('1 tablet at migraine onset, max 3 per day',     5,  3, 4),
    ('1 tablet if pain, max 3 per day',               5,  2, 4),
    ('1 tablet 3 times a day with food',              7,  3, 5),
    ('1 tablet up to 3 times a day if pain',          5,  2, 5),
    ('1 tablet every morning',                        90, 4, 6),
    ('1 tablet every morning',                        90, 4, 7),
    ('1 tablet up to 3 times a day if fever',         5,  2, 8),
    ('1 tablet 3 times a day with food',              3,  3, 8),   -- patient 3 is allergic
    ('Dose adapted to weight, 3 times a day',         7,  1, 9),
    ('1 tablet up to 4 times a day if fever',         3,  7, 9),
    ('2 puffs when short of breath',                  30, 5, 10),
    ('1 tablet up to 4 times a day if fever',         3,  7, 10),
    ('2 puffs when short of breath',                  90, 5, 11),
    ('1 tablet 3 times a day with food',              7,  3, 12),
    ('1 tablet up to 3 times a day if pain',          5,  2, 12),
    ('1 tablet 3 times a day',                        7,  1, 13),  -- patient 5 is allergic
    ('1 tablet up to 3 times a day if pain',          4,  2, 13);

-- -----------------------------------------------------------------------------
-- Allergies
-- -----------------------------------------------------------------------------
INSERT INTO allergic_to (patient_id, medication_id, severity) VALUES
    (5, 1, 'severe'),    -- Nicolas Maes / Amoxicillin : prescribed in consultation 13
    (3, 3, 'moderate'),  -- Marc Willems / Ibuprofen : prescribed in consultation 8
    (2, 1, 'mild'),      -- Julie Leroy / Amoxicillin : never prescribed to her
    (4, 3, 'mild'),      -- Sarah Claes / Ibuprofen : never prescribed to her
    (7, 2, 'mild');      -- Laura Mertens / Paracetamol 1 g : patient without consultation

COMMIT;