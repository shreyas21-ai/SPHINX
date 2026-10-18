import pytest
from flask_jwt_extended import create_access_token
from app.models.role import Role
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.extensions import db


@pytest.fixture(scope='module')
def doctor_setup(app):
    with app.app_context():
        roles = {r.name: r.id for r in Role.query.all()}

        # Create Doctor 1 and Doctor 2
        doc1 = User.query.filter_by(email='doc1@test.com').first()
        if not doc1:
            doc1 = User(email='doc1@test.com', first_name='John', last_name='Doctor', role_id=roles[Role.DOCTOR])
            doc1.set_password('Pass123!')
            db.session.add(doc1)

        doc2 = User.query.filter_by(email='doc2@test.com').first()
        if not doc2:
            doc2 = User(email='doc2@test.com', first_name='Sarah', last_name='Doctor', role_id=roles[Role.DOCTOR])
            doc2.set_password('Pass123!')
            db.session.add(doc2)

        # Create Admin
        admin = User.query.filter_by(email='admin_doc_test@test.com').first()
        if not admin:
            admin = User(email='admin_doc_test@test.com', first_name='Admin', last_name='User', role_id=roles[Role.ADMIN])
            admin.set_password('Pass123!')
            db.session.add(admin)

        db.session.commit()

        doc1_obj = User.query.filter_by(email='doc1@test.com').first()
        doc2_obj = User.query.filter_by(email='doc2@test.com').first()
        admin_obj = User.query.filter_by(email='admin_doc_test@test.com').first()

        # Create Assigned Patient for Doc 1
        pat_assigned = PatientRepository_create_helper("AssignedDoc1", "Patient")
        # Create Unassigned Patient (no relation to Doc 1)
        pat_unassigned = PatientRepository_create_helper("UnassignedDoc1", "Patient")

        from app.crypto.aes_cipher import AESCipher
        # Assign pat_assigned to Doc 1 via MedicalRecord
        mr = MedicalRecord(
            patient_id=pat_assigned.id,
            doctor_id=doc1_obj.id,
            disease_enc=AESCipher.encrypt("Initial Consultation"),
            diagnosis_enc=AESCipher.encrypt("Routine Checkup")
        )
        db.session.add(mr)
        db.session.commit()

        return {
            'doc1_id': doc1_obj.id,
            'doc2_id': doc2_obj.id,
            'admin_id': admin_obj.id,
            'assigned_pat_public_id': pat_assigned.public_id,
            'unassigned_pat_public_id': pat_unassigned.public_id
        }


def PatientRepository_create_helper(first_name, last_name):
    from app.services.patient_service import PatientService
    res = PatientService.create_patient({
        'first_name': first_name,
        'last_name': last_name,
        'blood_group': 'O+'
    })
    return Patient.query.filter_by(public_id=res['public_id']).first()


def test_doctor_assigned_patient_access(client, app, doctor_setup):
    with app.app_context():
        doc1_token = create_access_token(identity=str(doctor_setup['doc1_id']))

    # Access assigned patient with TREATMENT purpose -> allowed (200 OK)
    res = client.get(
        f"/api/v1/patients/{doctor_setup['assigned_pat_public_id']}",
        headers={'Authorization': f'Bearer {doc1_token}', 'X-Access-Purpose': 'TREATMENT'}
    )
    assert res.status_code == 200
    assert res.get_json()['data']['first_name'] == 'AssignedDoc1'


def test_doctor_unassigned_patient_blocked_without_emergency(client, app, doctor_setup):
    with app.app_context():
        doc1_token = create_access_token(identity=str(doctor_setup['doc1_id']))

    # Access unassigned patient with TREATMENT purpose -> 403 Forbidden
    res = client.get(
        f"/api/v1/patients/{doctor_setup['unassigned_pat_public_id']}",
        headers={'Authorization': f'Bearer {doc1_token}', 'X-Access-Purpose': 'TREATMENT'}
    )
    assert res.status_code == 403


def test_doctor_unassigned_patient_accessible_with_emergency_purpose(client, app, doctor_setup):
    with app.app_context():
        doc1_token = create_access_token(identity=str(doctor_setup['doc1_id']))

    # Access unassigned patient with EMERGENCY purpose -> allowed (200 OK) + Audited
    res = client.get(
        f"/api/v1/patients/{doctor_setup['unassigned_pat_public_id']}",
        headers={'Authorization': f'Bearer {doc1_token}', 'X-Access-Purpose': 'EMERGENCY'}
    )
    assert res.status_code == 200

    # Verify audit log entry captured EMERGENCY purpose
    with app.app_context():
        log = AuditLog.query.filter_by(user_id=doctor_setup['doc1_id'], purpose='EMERGENCY').first()
        assert log is not None


def test_doctor_cannot_create_update_delete_patient(client, app, doctor_setup):
    with app.app_context():
        doc1_token = create_access_token(identity=str(doctor_setup['doc1_id']))

    # Doctor create patient -> 403
    res_create = client.post('/api/v1/patients', json={'first_name': 'NoDocCreate'}, headers={'Authorization': f'Bearer {doc1_token}'})
    assert res_create.status_code == 403

    # Doctor update patient -> 403
    res_update = client.put(f"/api/v1/patients/{doctor_setup['assigned_pat_public_id']}", json={'first_name': 'NewName'}, headers={'Authorization': f'Bearer {doc1_token}'})
    assert res_update.status_code == 403

    # Doctor delete patient -> 403
    res_delete = client.delete(f"/api/v1/patients/{doctor_setup['assigned_pat_public_id']}", headers={'Authorization': f'Bearer {doc1_token}'})
    assert res_delete.status_code == 403


def test_doctor_cannot_create_billing_claims(client, app, doctor_setup):
    with app.app_context():
        doc1_token = create_access_token(identity=str(doctor_setup['doc1_id']))

    payload = {
        'patient_public_id': doctor_setup['assigned_pat_public_id'],
        'items': [{'item_name': 'Care', 'quantity': 1, 'unit_price': 100}],
        'approved_amount': 0
    }
    # Doctor create billing claim -> 403 Forbidden
    res = client.post('/api/v1/billing', json=payload, headers={'Authorization': f'Bearer {doc1_token}', 'X-Access-Purpose': 'BILLING'})
    assert res.status_code == 403


def test_doctor_hmac_exact_and_substring_search(client, app, doctor_setup):
    with app.app_context():
        doc1_token = create_access_token(identity=str(doctor_setup['doc1_id']))

    # Create medical record with disease = "Diabetes Mellitus" for assigned patient
    create_rec_res = client.post(
        '/api/v1/medical-records',
        json={
            'patient_public_id': doctor_setup['assigned_pat_public_id'],
            'disease': 'Diabetes Mellitus',
            'diagnosis': 'Type 2 Diabetes',
            'treatment_plan': 'Insulin therapy'
        },
        headers={'Authorization': f'Bearer {doc1_token}'}
    )
    assert create_rec_res.status_code == 201

    # Execute exact search for Diabetes
    res_exact = client.post(
        '/api/v1/search',
        json={
            'query': 'Diabetes Mellitus',
            'field_name': 'disease',
            'search_type': 'EXACT'
        },
        headers={'Authorization': f'Bearer {doc1_token}', 'X-Access-Purpose': 'TREATMENT'}
    )
    assert res_exact.status_code == 200
    exact_data = res_exact.get_json()['data']
    assert exact_data['total_matching_medical_records'] >= 1
    assert exact_data['search_telemetry']['full_db_scanned'] is False

    # Execute substring search for "Diab"
    res_sub = client.post(
        '/api/v1/search',
        json={
            'query': 'Diab',
            'field_name': 'disease',
            'search_type': 'SUBSTRING'
        },
        headers={'Authorization': f'Bearer {doc1_token}', 'X-Access-Purpose': 'TREATMENT'}
    )
    assert res_sub.status_code == 200
    sub_data = res_sub.get_json()['data']
    assert sub_data['total_matching_medical_records'] >= 1
    assert sub_data['search_telemetry']['full_db_scanned'] is False
