# Project SPHINX — Secure Patient Healthcare Information Network eXchange

A full-stack healthcare information system featuring **role-based access control (RBAC)**, **AES-256-GCM field-level encryption**, and **cryptographic HMAC blind-index search** that lets authorised staff search encrypted patient records without ever decrypting the full database.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Implemented Features](#3-implemented-features)
4. [User Roles and Permissions](#4-user-roles-and-permissions)
5. [Security Design](#5-security-design)
6. [Prerequisites](#6-prerequisites)
7. [Environment Variables](#7-environment-variables)
8. [Database Setup](#8-database-setup)
9. [Running the Application](#9-running-the-application)
10. [Running Tests](#10-running-tests)
11. [Demo Walkthrough](#11-demo-walkthrough)
12. [API Reference Summary](#12-api-reference-summary)
13. [Known Limitations](#13-known-limitations)

---

## 1. System Overview

SPHINX is a **local-development** healthcare platform built for a university submission.
It is **not configured for production deployment** — no TLS termination, email delivery, or production secrets management is wired up.

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite 5 + MUI 5 |
| Backend | Python 3.11 + Flask 3.0 |
| Database | MySQL 8 (dev) / SQLite (tests) |
| Auth | JWT (access 2 h, refresh 30 days) |
| Encryption | AES-256-GCM per field (cryptography lib) |
| Search | HMAC-SHA256 blind indexing (n-gram + exact) |

---

## 2. Architecture

```
sphinx-frontend/          React/Vite SPA (port 3000)
  src/pages/              One page per feature area
  src/components/         Shared MUI components

sphinx-backend/
  app/
    api/v1/               Flask blueprints (auth, patients, records,
                          appointments, billing, search, audit, users, dashboard)
    crypto/               AESCipher · HMACSearchIndexer · KeyManager
    models/               SQLAlchemy ORM models
    repositories/         Data-access layer (no raw SQL in services)
    services/             Business logic + decrypt-on-read
    schemas/              Marshmallow request/response schemas
    utils/                RBAC decorator · audit decorator · exceptions
  config.py               DevelopmentConfig / TestingConfig / ProductionConfig
  wsgi.py                 Entry point (flask run / python wsgi.py)
  scripts/
    init_db.py            Create all tables (idempotent)
    bootstrap_admin.py    Seed roles, admin account, and demo data (idempotent)
```

Vite dev-server proxies all `/api/*` requests to `http://localhost:5000`, so the frontend never needs a hard-coded backend URL.

---

## 3. Implemented Features

| Feature | Status |
|---|---|
| JWT authentication (login / refresh / me) | ? |
| Role-based access control (5 roles) | ? |
| Patient registration and management | ? |
| AES-256-GCM field-level encryption of PII | ? |
| HMAC blind-index search (exact + n-gram substring) | ? |
| Encrypted medical records (CRUD) | ? |
| Appointment scheduling (doctor + nurse assignment) | ? |
| Billing claims and insurance management | ? |
| Audit log — every data access recorded | ? |
| Admin user management (create / deactivate accounts) | ? |
| Dashboard summaries per role | ? |
| Password reset flow (token-based, local only) | ? |
| Demo data seeding (patients, records, appointments, billing) |
| Suspicious activity monitoring & anomaly detection (Isolation Forest + threshold rules) | Yes | ? |

---

## 4. User Roles and Permissions

| Role | Patients | Medical Records | Appointments | Billing | Audit Log | Users |
|---|---|---|---|---|---|---|
| **ADMIN** | Read | Read | Read | Read | Full | Full CRUD |
| **DOCTOR** | Own patients (read/write) | Own patients (CRUD) | Own schedule (read) | — | — | — |
| **NURSE** | Read | Read | Read | — | — | — |
| **RECEPTIONIST** | Create / Read | — | Create / Read | — | — | — |
| **INSURANCE_OFFICER** | Read (limited) | Read (limited) | — | Full CRUD | — | — |

> Doctors performing an **EMERGENCY** search bypass the own-patient scope restriction (recorded in the audit log).

---

## 5. Security Design

### 5.1 Field-Level Encryption

Sensitive patient and medical-record fields are encrypted individually using **AES-256-GCM** before being written to the database.

- A **unique 96-bit nonce** is generated for every encryption call — the same plaintext stored twice produces two different ciphertexts.
- The GCM authentication tag detects any in-database tampering.
- Stored format: `base64(nonce[12] || ciphertext || tag[16])`.
- Decryption happens in the service layer immediately before the API response is serialised; the database never holds readable PII.

### 5.2 Searchable Encryption (HMAC Blind Index)

SPHINX allows searching encrypted records without decrypting any row that does not match.

1. **At write time** — for each searchable field (disease, diagnosis, allergies, name, blood_group, etc.) the system computes:
   - One **HMAC-SHA256 exact token** over the normalised full value.
   - Multiple **HMAC-SHA256 n-gram tokens** (character sliding windows of length 3–4) for substring search.
   All tokens are stored in a separate `search_index` table alongside the record ID; no plaintext is stored there.

2. **At search time** — the query string is tokenised identically, the tokens are looked up in `search_index`, and only the matching record IDs are fetched and decrypted. **The full database is never scanned.**

3. The HMAC key (`SPHINX_HMAC_SECRET_KEY`) is separate from the AES encryption key (`SPHINX_AES_SECRET_KEY`). Compromising one does not compromise the other.

### 5.3 Passwords

All passwords are hashed with **bcrypt** (default work factor 12). Plaintext passwords are never logged or stored.

### 5.4 Audit Logging

Every authenticated data-access call is recorded in the `audit_logs` table: user ID, role, action, target resource, IP address, and timestamp. The ADMIN role can read audit logs through the UI.

---

## 6. Prerequisites

| Requirement | Version tested | Notes |
|---|---|---|
| Python | 3.11 | Any 3.10+ should work |
| Node.js | 18 LTS | For Vite dev server |
| npm | 9+ | Bundled with Node 18 |
| MySQL | 8.0 | Running locally on port 3306 |
| Git | any | |

> **SQLite** is used automatically during automated tests — MySQL is not needed to run `pytest`.

---

## 7. Environment Variables

Copy the example file and fill in your own values. **Never commit `.env` to version control.**

```powershell
# From the project root
Copy-Item sphinx-backend\.env.example sphinx-backend\.env
```

Then edit `sphinx-backend/.env`:

```dotenv
FLASK_APP=wsgi.py
FLASK_ENV=development

SECRET_KEY=replace-with-a-random-secret
JWT_SECRET_KEY=replace-with-a-different-random-secret

# Generate separate secure keys for your local environment
SPHINX_AES_SECRET_KEY=replace-with-base64-encoded-32-byte-key
SPHINX_HMAC_SECRET_KEY=replace-with-a-separate-base64-encoded-32-byte-key

# Database — SQLite for quick start, MySQL for full demo
DATABASE_URL=sqlite:///sphinx_dev.db
# DATABASE_URL=mysql+pymysql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:3306/sphinx

# Admin bootstrap credentials
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=replace-with-a-strong-password
```

### Generating cryptographic keys

Run once in any Python interpreter:

```python
import os, base64
print("AES key: ", base64.b64encode(os.urandom(32)).decode())
print("HMAC key:", base64.b64encode(os.urandom(32)).decode())
```

Paste each output into the corresponding `.env` variable.

### MySQL database creation (if not using SQLite)

```sql
CREATE DATABASE sphinx CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 8. Database Setup

> These commands are **idempotent**. Running them against an existing database is safe — no tables are dropped or truncated, and records are only inserted if they do not already exist.

### Step 1 — Activate the virtual environment

```powershell
cd sphinx-backend
.\venv\Scripts\Activate.ps1
```

*(Use `.\.venv\Scripts\Activate.ps1` if the venv is in the project root.)*

### Step 2 — Install Python dependencies

```powershell
pip install -r requirements.txt
```

### Step 3 — Create tables

```powershell
python scripts/init_db.py
```

Expected output: `Database schema successfully created!`

### Step 4 — Seed roles, admin, and demo data

```powershell
python scripts/bootstrap_admin.py
```

This creates (skipping any that already exist):

- All five system roles
- The admin account (credentials from `.env`)
- Four sample staff accounts
- Two sample patients with encrypted records, one appointment, and one billing claim

**Demo accounts created by bootstrap:**

| Role | Email | Password |
|---|---|---|
| ADMIN | *(BOOTSTRAP_ADMIN_EMAIL from .env)* | *(BOOTSTRAP_ADMIN_PASSWORD from .env)* |
| DOCTOR | dr.smith@sphinxhealth.com | DoctorPass123! |
| NURSE | nurse.john@sphinxhealth.com | NursePass123! |
| RECEPTIONIST | rec.sarah@sphinxhealth.com | RecPass123! |
| INSURANCE_OFFICER | ins.mark@sphinxhealth.com | InsPass123! |

> These passwords are for local demo/grading only. They are printed at the end of bootstrap output.

---

## 9. Running the Application

Open **two separate terminals**.

### Terminal 1 — Backend (Flask)

```powershell
cd sphinx-backend
.\venv\Scripts\Activate.ps1
$env:FLASK_ENV = "development"
flask run
```

The backend listens on **http://localhost:5000**.

Health check:

```powershell
Invoke-RestMethod http://localhost:5000/health
```

Expected:
```json
{"status": "healthy", "system": "SPHINX Secure Patient Healthcare Information Platform", "version": "1.0.0"}
```

Alternative (without flask CLI):

```powershell
python wsgi.py
```

### Terminal 2 — Frontend (Vite)

```powershell
cd sphinx-frontend
npm install        # first run only
npm run dev
```

Open **http://localhost:3000** in a browser.  
All `/api/*` calls are proxied to `http://localhost:5000` by `vite.config.js`.

---

## 10. Running Tests

Tests use SQLite in-memory — no MySQL or running server required.

```powershell
cd sphinx-backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

Run a single test file:

```powershell
pytest tests/test_search.py -v
```

Run a single test case:

```powershell
pytest tests/test_search.py::test_hmac_exact_search -v
```

### Test suite at a glance

| File | What it covers |
|---|---|
| `test_auth.py` | Login, JWT issuance and validation |
| `test_crypto.py` | AES-GCM round-trip, nonce uniqueness, tamper detection |
| `test_patients.py` | Patient CRUD, field encryption round-trip |
| `test_role_workflows.py` | RBAC enforcement across all five roles |
| `test_doctor_workflow.py` | Doctor patient scope, emergency bypass |
| `test_search.py` | Exact match, substring n-gram, multi-field, role filtering |

| 	est_activity_monitor.py | Repeated failed logins, excessive searches, off-hours logins, genuine Isolation Forest ML detection, duplicate prevention |

**Verified baseline: 22 backend tests + 6 search tests + 10 activity monitoring tests = 38 passing.**

---

## 11. Demo Walkthrough

Ensure both servers are running before starting (see §9).

### Step 1 — Admin: system overview and user management

1. Open **http://localhost:3000** and log in with the admin credentials.
2. Explore the **Dashboard** — shows system-wide patient, record, and appointment counts.
3. Navigate to **Users** ? create a new DOCTOR account to demonstrate admin-provisioned access.

### Step 2 — Receptionist: patient registration

1. Log in as `rec.sarah@sphinxhealth.com` / `RecPass123!`.
2. Navigate to **Patients** ? **New Patient**.
3. Fill in patient details and save — all PII is encrypted at rest on submission.
4. Confirm the patient appears in the list.

### Step 3 — Doctor: medical records and appointments

1. Log in as `dr.smith@sphinxhealth.com` / `DoctorPass123!`.
2. Navigate to **Patients** ? open *Rav Kumar*.
3. Navigate to **Medical Records** ? view the pre-seeded encrypted record (Diabetes Mellitus Type 2).
4. Click **+ Add Record** to create a new encrypted medical record.
5. Navigate to **Appointments** ? view the scheduled appointment.

### Step 4 — Secure Search (key demo point)

1. Staying logged in as Doctor, open **Secure Search**.
2. Search `diabetes` with type **Substring** — results appear; the response includes `"full_db_scanned": false`.
3. Switch to **Exact** and search `Diabetes Mellitus Type 2` — same patient returned via HMAC exact token.
4. Search `penicillin` in field **Allergies** — returns Rav Kumar (allergy field HMAC match).
5. Switch to **Multi-Field**, enter `O+` as blood group — demonstrates cross-field HMAC search.

### Step 5 — Nurse: read-only view

1. Log in as `nurse.john@sphinxhealth.com` / `NursePass123!`.
2. Verify read-only access to Patients and Medical Records.
3. Confirm that create/edit controls are absent or blocked.

### Step 6 — Insurance Officer: billing

1. Log in as `ins.mark@sphinxhealth.com` / `InsPass123!`.
2. Navigate to **Billing** ? open the seeded claim for Rav Kumar.
3. Update claim status from **Pending** to **Approved** to demonstrate the billing workflow.

### Step 7 — Admin: audit log review

1. Log back in as Admin.
2. Navigate to **Audit Logs** — every access from Steps 1–6 is listed with role, action, resource, and timestamp.

---

## 12. API Reference Summary

Base URL: `http://localhost:5000/api/v1`

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| POST | `/auth/login` | None | Obtain JWT access + refresh tokens |
| POST | `/auth/refresh` | Refresh JWT | Issue new access token |
| GET | `/auth/me` | JWT | Current user profile |
| POST | `/auth/register` | ADMIN | Create staff account |
| GET | `/patients/` | JWT | List patients (role-filtered) |
| POST | `/patients/` | RECEPTIONIST, ADMIN | Register new patient |
| GET | `/patients/:id` | JWT | Fetch and decrypt single patient |
| GET | `/medical-records/` | JWT | List records (role-filtered) |
| POST | `/medical-records/` | DOCTOR | Create encrypted record |
| PATCH | `/medical-records/:id` | DOCTOR | Update record |
| GET | `/appointments/` | JWT | List appointments |
| POST | `/appointments/` | RECEPTIONIST, ADMIN | Schedule appointment |
| GET | `/billing/` | INSURANCE_OFFICER, ADMIN | List billing claims |
| POST | `/billing/` | INSURANCE_OFFICER | Create billing claim |
| PATCH | `/billing/:id` | INSURANCE_OFFICER | Update claim status |
| POST | `/search/` | DOCTOR, ADMIN, NURSE | HMAC blind-index search |
| GET | `/audit/` | ADMIN | Paginated audit log |
| GET | `/dashboard/` | JWT | Role-specific summary stats |
| GET | `/users/` | ADMIN | List staff accounts |

---

## 13. Known Limitations

| Area | Limitation |
|---|---|
| **Deployment** | Local development only. No TLS, no production WSGI configuration included. |
| **Email** | Forgot-password flow returns the reset token directly in the API response — no SMTP integration. |
| **Password reset tokens** | Stored in-memory (Python dict). Tokens are lost on server restart. |
| **Search substring length** | N-gram indexing requires a minimum query of 3 characters. Shorter queries fall back to exact match only. |
| **Key rotation** | No key-rotation workflow is implemented. Re-encrypting existing records after changing `SPHINX_AES_SECRET_KEY` requires a custom migration. |
| **Concurrency** | `flask run` is single-threaded. `gunicorn` (included in `requirements.txt`) can be used for multi-worker local testing. |
| **Large downloads** | SPHINX does not implement bulk file download endpoints; individual record lookups are audited individually. |
| **Doctor scope** | Doctors see only patients explicitly assigned to them. Cross-department referrals require Admin re-assignment. |
| **Test database** | Tests use SQLite; production uses MySQL. Schema compatibility is maintained but not CI-validated against MySQL in this submission. |

---

*Project SPHINX — Academic Submission Build · October 2026*
