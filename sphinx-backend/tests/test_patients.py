import pytest
from app.models.patient import Patient
from app.models.audit_log import AuditLog
from app.models.search_index import SearchIndex
from app.crypto.aes_cipher import AESCipher
from flask_jwt_extended import create_access_token


def test_patient_crud_flow(client, app, admin_user, doctor_user):
    with app.app_context():
        admin_token = create_access_token(identity=str(admin_user.id))
        doctor_token = create_access_token(identity=str(doctor_user.id))

    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    headers_doctor = {'Authorization': f'Bearer {doctor_token}'}

    # 1. Create Patient (Admin)
    new_patient_payload = {
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '1985-06-15',
        'gender': 'Male',
        'phone': '555-0199',
        'email': 'john.doe@example.com',
        'address': '123 Health Way',
        'insurance_provider': 'BlueShield',
        'policy_number': 'BS-998877',
        'blood_group': 'O+'
    }
    res_create = client.post('/api/v1/patients', json=new_patient_payload, headers=headers_admin)
    assert res_create.status_code == 201
    patient_data = res_create.get_json()['data']
    public_id = patient_data['public_id']
    assert patient_data['first_name'] == 'John'
    assert patient_data['last_name'] == 'Doe'

    # Verify AES encryption in DB
    with app.app_context():
        p = Patient.query.filter_by(public_id=public_id).first()
        assert p is not None
        assert p.first_name_enc != 'John'
        assert AESCipher.decrypt(p.first_name_enc) == 'John'

        # Verify HMAC search tokens exist
        tokens = SearchIndex.query.filter_by(patient_id=p.id).all()
        assert len(tokens) > 0

    # 2. Update Patient - Forbidden for Doctor
    update_payload = {
        'first_name': 'Johnny',
        'blood_group': 'A+'
    }
    res_update_doc = client.put(f'/api/v1/patients/{public_id}', json=update_payload, headers=headers_doctor)
    assert res_update_doc.status_code == 403

    # 3. Update Patient - Success for Admin
    res_update_admin = client.put(f'/api/v1/patients/{public_id}', json=update_payload, headers=headers_admin)
    assert res_update_admin.status_code == 200
    updated_data = res_update_admin.get_json()['data']
    assert updated_data['first_name'] == 'Johnny'
    assert updated_data['blood_group'] == 'A+'

    # Verify DB state after update (AES encryption maintained & HMAC index updated)
    with app.app_context():
        p_updated = Patient.query.filter_by(public_id=public_id).first()
        assert AESCipher.decrypt(p_updated.first_name_enc) == 'Johnny'
        assert AESCipher.decrypt(p_updated.blood_group_enc) == 'A+'

        # Audit log entry created for UPDATE_PATIENT
        audit = AuditLog.query.filter_by(action='UPDATE_PATIENT', user_id=admin_user.id).first()
        assert audit is not None

    # 4. Delete Patient - Success for Admin
    res_delete = client.delete(f'/api/v1/patients/{public_id}', headers=headers_admin)
    assert res_delete.status_code == 200

    with app.app_context():
        assert Patient.query.filter_by(public_id=public_id).first() is None
        assert SearchIndex.query.filter_by(patient_id=p.id).count() == 0
