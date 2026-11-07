# Patient Record

Console application to manage patient records (patients, doctors, consultations,
prescriptions and allergies), written in Python with a PostgreSQL database.

The project deliberately uses **raw SQL** through `psycopg` (no ORM) to show the
database design and the queries: joins, aggregates, anti-joins, `DISTINCT ON`,
transactions and constraints.

All the data in `db/seed.sql` is fictitious.

## Features

| Menu | What it does |
|---|---|
| List / search patients | Search is case-insensitive on first or last name |
| Patient record | Identity, allergies, consultations and prescriptions, with allergy warnings |
| Add / update / delete a patient | Input validation; a patient with consultations cannot be deleted |
| Add a consultation | Consultation and its prescriptions saved in a single transaction |
| Add a prescription | Warns and asks confirmation if the patient is allergic to the medication |
| Add an allergy | Patient <-> medication, with a severity |
| Statistics | 7 reporting queries (see below) |
| Reset database | Rebuilds the schema and reloads the test data, after confirmation |

## Installation

Requirements: Python 3.10+ and PostgreSQL 13+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

createdb patient_record
cp .env.example .env             # then fill in your PostgreSQL credentials
```

## Usage

```bash
python main.py
```

On the first launch, the tables are created and filled with test data
automatically. Choose an option by typing its number; `0` exits or goes back.

Run the unit tests (models and console helpers, no database needed):

```bash
python -m unittest -v
```

## Project structure

```
main.py              Entry point: connection, first-launch setup, error handling
menu.py              Menus: choice -> (label, action) dictionaries, generic menu loop
console.py           Validated input (text, int, date...) and table display
db/
  db.py              Connection, SQL file execution, database check
  schema.sql         Tables, constraints and indexes
  seed.sql           Fictitious test data
models/              Dataclasses: Patient, Doctor, Medication, Allergy, Consultation...
repositories/        Data access layer: every SQL query lives here, returns models
actions/             Menu actions: ask the user, call the repositories, display
tests/               Unit tests (unittest + unittest.mock)
```

Layers never skip each other: the menu calls actions, actions call repositories,
and only repositories contain SQL. Repositories never print anything.

### Models

The business objects are **dataclasses** in `models/`. Repositories build them
directly from the query rows with psycopg's `class_row(Patient)`: each selected
column is passed as a keyword argument, so the `SELECT` lists exactly the fields
of the class (joined columns included, e.g. `s.name AS specialty` for `Doctor`).

- `__post_init__` validates the same rules as the database (sex, birth date not in
  the future, duration > 0): errors are caught before reaching PostgreSQL.
- Read-only records are `frozen=True` (immutable); `Patient` is not, since its
  `id` is set once saved.
- Computed values are properties: `Patient.age`, `Patient.full_name`,
  `Medication.label`.
- `Severity` is an `Enum` whose values are the ones stored in the database.
- `PrescriptionDraft` is a prescription typed by the user and not saved yet: the
  consultation and its drafts are then saved together in one transaction.
- Statistics stay plain dictionaries: they are ad hoc reports, not business objects.

## Data model

- a **specialty** is practiced by 0..n doctors; a **doctor** has exactly one specialty
- a **doctor** performs 0..n consultations; a **patient** attends 0..n consultations
- a **consultation** includes 0..n prescriptions; a **prescription** refers to one medication
- a **patient** is allergic to 0..n medications (`allergic_to`, with a severity)

`allergic_to` is an association carrying data (the severity); its primary key is
`(patient_id, medication_id)`, so a patient cannot have the same allergy twice.

### Design choices

- **Deleting**: consultations use `ON DELETE RESTRICT` towards patients and doctors,
  because a medical history must be kept. Prescriptions are deleted with their
  consultation (`CASCADE`), and allergies with their patient.
- **Constraints** are named (`pk_`, `fk_`, `uk_`, `ck_`) so that errors are readable.
- **Indexes** on every foreign key (PostgreSQL does not create them automatically),
  plus `patients.last_name`. `allergic_to.patient_id` needs none: it is the first
  column of the primary key.
- **`TIMESTAMPTZ`** for every timestamp, to avoid ambiguities around daylight saving time.
- **Parameterised queries only** (`%s`): user input is never concatenated into SQL,
  which prevents SQL injection. LIKE wildcards in searches are escaped too.
- **Transactions**: the connection is in autocommit mode, and `conn.transaction()`
  groups the writes that must succeed or fail together (a consultation and its
  prescriptions). All input is collected before the transaction starts, so no
  transaction stays open while waiting for the user.

## Statistics queries

| Query | SQL technique |
|---|---|
| Consultations per doctor | `LEFT JOIN` + `GROUP BY`, doctors without consultation included |
| Consultations per specialty | Three tables, `COUNT(DISTINCT ...)` |
| Consultations per month | `date_trunc`, `to_char` |
| Most prescribed medications | `GROUP BY`, `ORDER BY`, `LIMIT` |
| Patients without consultation | Anti-join `LEFT JOIN ... WHERE ... IS NULL` |
| Allergy alerts | Join on two columns reached through different paths |
| Last consultation per patient | PostgreSQL `DISTINCT ON` in a subquery |

## Known limits

- An allergy is recorded per medication **and dosage**. In reality a patient is
  allergic to an active substance; a `substances` table would model that better.
- `updated_at` is set by the application on update; a trigger would guarantee it
  for every client.
