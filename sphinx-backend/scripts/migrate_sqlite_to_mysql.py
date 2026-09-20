import os
import sys
import sqlite3
import pymysql
from datetime import datetime

# Ensure root workspace directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.search_index import SearchIndex


def parse_datetime(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val.replace('Z', ''))
    except Exception:
        try:
            return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
        except Exception:
            return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')


def migrate():
    print("====================================================")
    print("Project SPHINX — SQLite to MySQL Migration Tool")
    print("====================================================\n")

    # Step 1: Ensure MySQL database 'sphinx' exists
    db_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/sphinx')
    print(f"Target Database URL: {db_url}")

    # Extract host, user, password, port for raw database creation
    user = 'root'
    password = 'root'
    host = '127.0.0.1'
    port = 3306
    db_name = 'sphinx'

    try:
        conn_raw = pymysql.connect(host=host, port=port, user=user, password=password)
        with conn_raw.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"✓ MySQL Database `{db_name}` verified/created successfully.")
        conn_raw.close()
    except Exception as e:
        print(f"❌ Failed to connect or create MySQL database: {e}")
        sys.exit(1)

    # Step 2: Initialize Flask app context & MySQL table schemas
    app = create_app('development')
    with app.app_context():
        print("✓ Creating all SQLAlchemy tables in MySQL...")
        db.create_all()
        print("✓ MySQL schema ready.\n")

        # Step 3: Connect to source SQLite database
        sqlite_db_path = os.path.join(app.root_path, '..', 'instance', 'sphinx_dev.db')
        if not os.path.exists(sqlite_db_path):
            sqlite_db_path = os.path.join(app.root_path, '..', 'sphinx_dev.db')

        if not os.path.exists(sqlite_db_path):
            print(f"⚠️ Source SQLite DB file not found at {sqlite_db_path}. Running schema bootstrap on MySQL...")
            from scripts.bootstrap_admin import bootstrap
            bootstrap()
            print("✓ MySQL database bootstrapped successfully.")
            return

        print(f"Source SQLite DB: {sqlite_db_path}")
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        cur = sqlite_conn.cursor()

        # Step 4: Migrate data table by table
        # 1. Roles
        cur.execute("SELECT * FROM roles;")
        roles_rows = cur.fetchall()
        migrated_roles = 0
        for r in roles_rows:
            existing = Role.query.get(r['id'])
            if not existing:
                role = Role(
                    id=r['id'],
                    name=r['name'],
                    description=r['description'],
                    created_at=parse_datetime(r['created_at']) or datetime.utcnow()
                )
                db.session.add(role)
                migrated_roles += 1
        db.session.commit()
        print(f"✓ Roles: {migrated_roles} migrated / {Role.query.count()} total in MySQL")

        # 2. Users
        cur.execute("SELECT * FROM users;")
        users_rows = cur.fetchall()
        migrated_users = 0
        for u in users_rows:
            existing = User.query.get(u['id'])
            if not existing:
                user = User(
                    id=u['id'],
                    public_id=u['public_id'],
                    email=u['email'],
                    password_hash=u['password_hash'],
                    first_name=u['first_name'],
                    last_name=u['last_name'],
                    role_id=u['role_id'],
                    created_at=parse_datetime(u['created_at']) or datetime.utcnow(),
                    updated_at=parse_datetime(u['updated_at']) or datetime.utcnow()
                )
                db.session.add(user)
                migrated_users += 1
        db.session.commit()
        print(f"✓ Users: {migrated_users} migrated / {User.query.count()} total in MySQL")

        # 3. Patients
        cur.execute("SELECT * FROM patients;")
        patients_rows = cur.fetchall()
        migrated_patients = 0
        for p in patients_rows:
            existing = Patient.query.get(p['id'])
            if not existing:
                patient = Patient(
                    id=p['id'],
                    public_id=p['public_id'],
                    first_name_enc=p['first_name_enc'],
                    last_name_enc=p['last_name_enc'],
                    dob_enc=p['dob_enc'],
                    gender_enc=p['gender_enc'],
                    phone_enc=p['phone_enc'],
                    email_enc=p['email_enc'],
                    address_enc=p['address_enc'],
                    insurance_provider_enc=p['insurance_provider_enc'],
                    policy_number_enc=p['policy_number_enc'],
                    blood_group_enc=p['blood_group_enc'],
                    created_at=parse_datetime(p['created_at']) or datetime.utcnow(),
                    updated_at=parse_datetime(p['updated_at']) or datetime.utcnow()
                )
                db.session.add(patient)
                migrated_patients += 1
        db.session.commit()
        print(f"✓ Patients: {migrated_patients} migrated / {Patient.query.count()} total in MySQL")

        # 4. Medical Records
        cur.execute("SELECT * FROM medical_records;")
        mr_rows = cur.fetchall()
        migrated_mr = 0
        for mr in mr_rows:
            existing = MedicalRecord.query.get(mr['id'])
            if not existing:
                record = MedicalRecord(
                    id=mr['id'],
                    public_id=mr['public_id'],
                    patient_id=mr['patient_id'],
                    doctor_id=mr['doctor_id'],
                    disease_enc=mr['disease_enc'],
                    diagnosis_enc=mr['diagnosis_enc'],
                    medical_history_enc=mr['medical_history_enc'],
                    prescription_enc=mr['prescription_enc'],
                    lab_reports_enc=mr['lab_reports_enc'],
                    doctor_notes_enc=mr['doctor_notes_enc'],
                    insurance_details_enc=mr['insurance_details_enc'],
                    treatment_plan_enc=mr['treatment_plan_enc'],
                    allergies_enc=mr['allergies_enc'],
                    vitals_enc=mr['vitals_enc'],
                    created_at=parse_datetime(mr['created_at']) or datetime.utcnow(),
                    updated_at=parse_datetime(mr['updated_at']) or datetime.utcnow()
                )
                db.session.add(record)
                migrated_mr += 1
        db.session.commit()
        print(f"✓ Medical Records: {migrated_mr} migrated / {MedicalRecord.query.count()} total in MySQL")

        # 5. Appointments
        cur.execute("SELECT * FROM appointments;")
        apt_rows = cur.fetchall()
        migrated_apt = 0
        for a in apt_rows:
            existing = Appointment.query.get(a['id'])
            if not existing:
                apt = Appointment(
                    id=a['id'],
                    public_id=a['public_id'],
                    patient_id=a['patient_id'],
                    doctor_id=a['doctor_id'],
                    appointment_date=parse_datetime(a['appointment_date']) or datetime.utcnow(),
                    status=a['status'],
                    reason=a['reason'],
                    created_at=parse_datetime(a['created_at']) or datetime.utcnow(),
                    updated_at=parse_datetime(a['updated_at']) or datetime.utcnow()
                )
                db.session.add(apt)
                migrated_apt += 1
        db.session.commit()
        print(f"✓ Appointments: {migrated_apt} migrated / {Appointment.query.count()} total in MySQL")

        # 6. Audit Logs
        cur.execute("SELECT * FROM audit_logs;")
        audit_rows = cur.fetchall()
        migrated_audit = 0
        for al in audit_rows:
            existing = AuditLog.query.get(al['id'])
            if not existing:
                log = AuditLog(
                    id=al['id'],
                    user_id=al['user_id'],
                    user_role=al['user_role'],
                    action=al['action'],
                    patient_id=al['patient_id'],
                    purpose=al['purpose'],
                    ip_address=al['ip_address'],
                    user_agent=al['user_agent'],
                    timestamp=parse_datetime(al['timestamp']) or datetime.utcnow()
                )
                db.session.add(log)
                migrated_audit += 1
        db.session.commit()
        print(f"✓ Audit Logs: {migrated_audit} migrated / {AuditLog.query.count()} total in MySQL")

        # 7. Search Index
        cur.execute("SELECT * FROM search_index;")
        si_rows = cur.fetchall()
        migrated_si = 0
        for si in si_rows:
            existing = SearchIndex.query.get(si['id'])
            if not existing:
                idx = SearchIndex(
                    id=si['id'],
                    patient_id=si['patient_id'],
                    record_id=si['record_id'],
                    field_name=si['field_name'],
                    token_hash=si['token_hash'],
                    token_type=si['token_type'],
                    created_at=parse_datetime(si['created_at']) or datetime.utcnow()
                )
                db.session.add(idx)
                migrated_si += 1
        db.session.commit()
        print(f"✓ Search Index: {migrated_si} migrated / {SearchIndex.query.count()} total in MySQL")

        sqlite_conn.close()

    print("\n====================================================")
    print("MySQL Migration Completed Successfully!")
    print("====================================================\n")

if __name__ == '__main__':
    migrate()
