# SPHINX

**Secure Searchable Medical Data Management System**

SPHINX is a healthcare information platform prototype designed to manage patient information while demonstrating encrypted storage and searchable-encryption techniques.

> **Status:** Academic/development project. This repository is not a certified or production-ready healthcare system. Do not use real patient data or deploy it with default/development credentials.

## Key features

- Role-based access for healthcare staff (including Admin, Doctor, Nurse, Receptionist, and Insurance Officer roles).
- JWT-based authentication and token refresh.
- Patient and medical-record management APIs.
- AES-256-GCM authenticated encryption helper for sensitive values.
- HMAC-based searchable-index functionality for searching encrypted records.
- Audit logging for selected access and search operations, including purpose-of-access requirements on protected routes.
- React frontend with Material UI components and a Flask REST API backend.

## Technology stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, React Router, Material UI, Axios, Recharts |
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Marshmallow |
| Cryptography | Python `cryptography` (AES-GCM), HMAC-based indexing |
| Database | SQLAlchemy; configuration supports MySQL via PyMySQL |

## Repository structure

```text
.
├── sphinx-backend/       # Flask API, models, services, crypto, tests
│   ├── app/
│   ├── tests/
│   ├── scripts/
│   ├── config.py
│   ├── requirements.txt
│   └── wsgi.py
└── sphinx-frontend/      # React + Vite application
    └── package.json
```

## Getting started

### 1. Backend

From the repository root, create and activate a Python virtual environment, then install the backend dependencies:

```powershell
cd sphinx-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Edit `sphinx-backend/.env` and set **unique, securely generated values** for `SECRET_KEY`, `JWT_SECRET_KEY`, `SPHINX_AES_SECRET_KEY`, and `SPHINX_HMAC_SECRET_KEY`. Configure `DATABASE_URL` for your local database. Keep `.env` private and never commit it. The sample file is a template, not a production configuration.

Start the Flask development server using the app factory:

```powershell
$env:FLASK_APP = "wsgi.py"
flask run
```

The backend defines a health endpoint at `/health`. API routes are registered under `/api/v1`.

### 2. Frontend

Open a second terminal at the repository root:

```powershell
cd sphinx-frontend
npm install
npm run dev
```

Vite prints the local development URL in the terminal. Ensure the frontend API base URL is configured to point to your running backend.

## Configuration and security notes

- Use separate, randomly generated secrets for Flask sessions, JWT signing, AES encryption, and HMAC indexing.
- Never commit `.env`, production credentials, real patient records, database dumps, or access tokens.
- Use synthetic data only for development and demonstrations.
- AES-GCM provides authenticated encryption; protecting and rotating keys is still an operational responsibility.
- Searchable indexes can reveal information through search/access patterns. Searchable encryption does not eliminate all leakage.
- Review authorization rules, audit coverage, CORS configuration, password-reset behavior, and deployment settings before any real-world use.
- The development configuration enables debug mode and permissive API CORS; do not use it as-is in production.

## Testing

Backend dependencies include `pytest`. From `sphinx-backend`, run:

```powershell
python -m pytest
```

Run the frontend scripts from `sphinx-frontend`:

```powershell
npm run lint
npm run build
```

These commands are provided for local verification; results depend on your environment and current code.

## Contributing

1. Create a feature branch.
2. Make a focused change and add/update tests where appropriate.
3. Run relevant backend and frontend checks.
4. Open a pull request describing the change and its verification.

## License

No license file is currently specified. All rights are reserved unless the repository owner adds a license.