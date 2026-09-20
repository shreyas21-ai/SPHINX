import pytest
from flask_jwt_extended import create_access_token
from app.models.role import Role
from app.models.user import User
from app.models.billing import BillingRecord
from app.models.audit_log import AuditLog
from app.extensions import db


@pytest.fixture(scope='module')
def test_users(app):
    with app.app_context():
        users = {}
        roles = Role.query.all()
        role_map = {r.name: r.id for r in roles}

        for r_name in [Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST, Role.INSURANCE_OFFICER]:
            email = f'{r_name.lower()}_workflow@test.com'
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(email=email, first_name=r_name, last_name='Workflow', role_id=role_map[r_name])
                u.set_password('Pass123!')
                db.session.add(u)
        db.session.commit()

        for r_name in [Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST, Role.INSURANCE_OFFICER]:
            email = f'{r_name.lower()}_workflow@test.com'
            u_obj = User.query.filter_by(email=email).first()
            users[r_name] = u_obj.id
        return users


def test_purpose_restrictions(client, app, test_users):
    with app.app_context():
        doc_token = create_access_token(identity=str(test_users[Role.DOCTOR]))
        nurse_token = create_access_token(identity=str(test_users[Role.NURSE]))
        rec_token = create_access_token(identity=str(test_users[Role.RECEPTIONIST]))
        ins_token = create_access_token(identity=str(test_users[Role.INSURANCE_OFFICER]))

    # Doctor allowed: TREATMENT, EMERGENCY, RESEARCH
    res_doc_valid = client.get('/api/v1/patients', headers={'Authorization': f'Bearer {doc_token}', 'X-Access-Purpose': 'TREATMENT'})
    assert res_doc_valid.status_code == 200

    # Nurse blocked for BILLING purpose
    res_nurse_invalid = client.get('/api/v1/patients', headers={'Authorization': f'Bearer {nurse_token}', 'X-Access-Purpose': 'BILLING'})
    assert res_nurse_invalid.status_code == 400

    # Receptionist blocked for TREATMENT purpose
    res_rec_invalid = client.get('/api/v1/patients', headers={'Authorization': f'Bearer {rec_token}', 'X-Access-Purpose': 'TREATMENT'})
    assert res_rec_invalid.status_code == 400

    # Receptionist allowed for ADMINISTRATIVE purpose
    res_rec_valid = client.get('/api/v1/patients', headers={'Authorization': f'Bearer {rec_token}', 'X-Access-Purpose': 'ADMINISTRATIVE'})
    assert res_rec_valid.status_code == 200

    # Insurance Officer allowed for BILLING purpose
    res_ins_valid = client.get('/api/v1/patients', headers={'Authorization': f'Bearer {ins_token}', 'X-Access-Purpose': 'BILLING'})
    assert res_ins_valid.status_code == 200


def test_receptionist_search_blocked(client, app, test_users):
    with app.app_context():
        rec_token = create_access_token(identity=str(test_users[Role.RECEPTIONIST]))

    # Receptionist must NOT access Cryptographic Search
    res_search = client.post('/api/v1/search', json={'query': 'John'}, headers={'Authorization': f'Bearer {rec_token}', 'X-Access-Purpose': 'ADMINISTRATIVE'})
    assert res_search.status_code == 403


def test_admin_billing_creation_blocked(client, app, test_users):
    with app.app_context():
        admin_token = create_access_token(identity=str(test_users[Role.ADMIN]))

    payload = {
        'patient_public_id': 'dummy-id',
        'items': [{'item_name': 'Consultation', 'quantity': 1, 'unit_price': 500.0}],
        'approved_amount': 0.0
    }
    # Admin must NOT be allowed to create billing claims
    res = client.post('/api/v1/billing', json=payload, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 403


def test_insurance_officer_billing_workflow(client, app, test_users):
    # First create a patient record
    with app.app_context():
        admin_token = create_access_token(identity=str(test_users[Role.ADMIN]))
        ins_token = create_access_token(identity=str(test_users[Role.INSURANCE_OFFICER]))

    create_patient_res = client.post('/api/v1/patients', json={'first_name': 'BillTest', 'last_name': 'Patient'}, headers={'Authorization': f'Bearer {admin_token}'})
    assert create_patient_res.status_code == 201
    patient_public_id = create_patient_res.get_json()['data']['public_id']

    # Insurance Officer creates billing claim statement
    billing_payload = {
        'patient_public_id': patient_public_id,
        'items': [
            {'item_name': 'Consultation', 'quantity': 1, 'unit_price': 500.0},
            {'item_name': 'Lab tests', 'quantity': 1, 'unit_price': 800.0},
            {'item_name': 'Room', 'quantity': 1, 'unit_price': 2000.0},
            {'item_name': 'Medicines', 'quantity': 1, 'unit_price': 700.0},
            {'item_name': 'Treatment', 'quantity': 1, 'unit_price': 6000.0}
        ],
        'approved_amount': 8000.0,
        'insurance_provider': 'BlueShield Care',
        'policy_number': 'POL-123456'
    }

    res_billing = client.post('/api/v1/billing', json=billing_payload, headers={'Authorization': f'Bearer {ins_token}', 'X-Access-Purpose': 'BILLING'})
    assert res_billing.status_code == 201
    data = res_billing.get_json()['data']

    # Verify math calculations: Total = 500+800+2000+700+6000 = 10000. Approved = 8000. Payable = 2000.
    assert data['total_bill'] == 10000.0
    assert data['approved_amount'] == 8000.0
    assert data['patient_payable'] == 2000.0

    # Verify audit log entry was created for CREATE_BILLING_CLAIM
    with app.app_context():
        audit = AuditLog.query.filter_by(action='CREATE_BILLING_CLAIM', user_id=test_users[Role.INSURANCE_OFFICER]).first()
        assert audit is not None
        assert audit.purpose == 'BILLING'
