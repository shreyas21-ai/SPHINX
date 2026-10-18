from app.services.patient_service import PatientService
from app.services.medical_record_service import MedicalRecordService
from app.services.search_service import SearchService


def test_searchable_encryption_flow(app, doctor_user, doctor_token, nurse_token, client):
    with app.app_context():
        # Create Patient
        pat = PatientService.create_patient({
            'first_name': 'Ravi',
            'last_name': 'Kumar',
            'blood_group': 'O+'
        })

        # Create Medical Record with Disease = Diabetes
        rec = MedicalRecordService.create_record({
            'patient_public_id': pat['public_id'],
            'disease': 'Diabetes Mellitus Type 2',
            'diagnosis': 'High Fasting Sugar',
            'doctor_notes': 'Strict diet recommended'
        }, doctor_id=doctor_user.id)

        # Doctor executes Substring Search for Disease = "Diab" with Purpose = TREATMENT
        headers = {
            'Authorization': f'Bearer {doctor_token}',
            'X-Access-Purpose': 'TREATMENT'
        }
        res = client.post('/api/v1/search', headers=headers, json={
            'query': 'Diab',
            'field_name': 'disease',
            'search_type': 'SUBSTRING',
            'purpose': 'TREATMENT'
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        assert data['total_matching_medical_records'] >= 1
        record_res = data['medical_records'][0]
        assert 'Diabetes' in record_res['disease']
        assert record_res['doctor_notes'] == 'Strict diet recommended'

        # Nurse executes the same search; verify Privacy Masking redacts Doctor Notes & Disease
        nurse_headers = {
            'Authorization': f'Bearer {nurse_token}',
            'X-Access-Purpose': 'TREATMENT'
        }
        res_nurse = client.post('/api/v1/search', headers=nurse_headers, json={
            'query': 'Diab',
            'field_name': 'disease',
            'search_type': 'SUBSTRING',
            'purpose': 'TREATMENT'
        })
        assert res_nurse.status_code == 200
        data_nurse = res_nurse.get_json()['data']
        assert data_nurse['medical_records'][0]['disease'] == '[REDACTED_PRIVACY_POLICY]'


def test_exact_patient_name_search(app, doctor_user, doctor_token, client):
    with app.app_context():
        pat = PatientService.create_patient({
            'first_name': 'Anand',
            'last_name': 'Patel',
            'blood_group': 'A+'
        })
        MedicalRecordService.create_record({
            'patient_public_id': pat['public_id'],
            'disease': 'Hypertension',
            'diagnosis': 'High BP'
        }, doctor_id=doctor_user.id)

        headers = {'Authorization': f'Bearer {doctor_token}', 'X-Access-Purpose': 'TREATMENT'}
        res = client.post('/api/v1/search', headers=headers, json={
            'query': 'Anand Patel',
            'field_name': 'name',
            'search_type': 'EXACT',
            'purpose': 'TREATMENT'
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        assert data['total_matching_patients'] >= 1
        assert data['total_matching_medical_records'] >= 1
        matched_pat = next(p for p in data['patients'] if p['public_id'] == pat['public_id'])
        assert matched_pat['first_name'] == 'Anand'
        assert matched_pat['last_name'] == 'Patel'


def test_substring_patient_name_search(app, doctor_user, doctor_token, client):
    with app.app_context():
        pat = PatientService.create_patient({
            'first_name': 'Kavita',
            'last_name': 'Sharma',
            'blood_group': 'B+'
        })
        MedicalRecordService.create_record({
            'patient_public_id': pat['public_id'],
            'disease': 'Asthma',
            'diagnosis': 'Bronchial Asthma'
        }, doctor_id=doctor_user.id)

        headers = {'Authorization': f'Bearer {doctor_token}', 'X-Access-Purpose': 'TREATMENT'}
        res = client.post('/api/v1/search', headers=headers, json={
            'query': 'Kav',
            'field_name': 'name',
            'search_type': 'SUBSTRING',
            'purpose': 'TREATMENT'
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        assert data['total_matching_patients'] >= 1
        matched_pat = next(p for p in data['patients'] if p['public_id'] == pat['public_id'])
        assert matched_pat['first_name'] == 'Kavita'


def test_no_match_patient_name_search(app, doctor_token, client):
    headers = {'Authorization': f'Bearer {doctor_token}', 'X-Access-Purpose': 'TREATMENT'}
    res = client.post('/api/v1/search', headers=headers, json={
        'query': 'NonExistentZzz999',
        'field_name': 'name',
        'search_type': 'SUBSTRING',
        'purpose': 'TREATMENT'
    })
    assert res.status_code == 200
    data = res.get_json()['data']
    assert data['total_matching_patients'] == 0
    assert data['total_matching_medical_records'] == 0
    assert data['patients'] == []
    assert data['medical_records'] == []


def test_patient_with_no_medical_records_search(app, doctor_user, doctor_token, client):
    with app.app_context():
        pat = PatientService.create_patient({
            'first_name': 'Suresh',
            'last_name': 'Verma',
            'blood_group': 'AB+'
        })

        # Assign patient to doctor_user via medical record creation or emergency purpose
        headers = {'Authorization': f'Bearer {doctor_token}', 'X-Access-Purpose': 'EMERGENCY'}
        res = client.post('/api/v1/search', headers=headers, json={
            'query': 'Suresh',
            'field_name': 'name',
            'search_type': 'SUBSTRING',
            'purpose': 'EMERGENCY'
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        assert data['total_matching_patients'] >= 1
        assert data['total_matching_medical_records'] == 0
        matched_pat = next(p for p in data['patients'] if p['public_id'] == pat['public_id'])
        assert matched_pat['first_name'] == 'Suresh'
        assert data['medical_records'] == []


def test_doctor_patient_name_search_authorization(app, doctor_user, doctor_token, client):
    from flask_jwt_extended import create_access_token
    from app.models.user import User
    from app.models.role import Role
    from app.extensions import db

    with app.app_context():
        # Create Patient Unassigned to doctor_user
        unassigned_pat = PatientService.create_patient({
            'first_name': 'UnassignedName',
            'last_name': 'PatientObj',
            'blood_group': 'O-'
        })

        # Doctor 1 searches for unassigned patient with TREATMENT purpose -> filtered out (0 results)
        headers = {'Authorization': f'Bearer {doctor_token}', 'X-Access-Purpose': 'TREATMENT'}
        res = client.post('/api/v1/search', headers=headers, json={
            'query': 'UnassignedName',
            'field_name': 'name',
            'search_type': 'SUBSTRING',
            'purpose': 'TREATMENT'
        })
        assert res.status_code == 200
        data = res.get_json()['data']
        matching_pub_ids = [p['public_id'] for p in data['patients']]
        assert unassigned_pat['public_id'] not in matching_pub_ids

        # Doctor 1 searches for unassigned patient with EMERGENCY purpose -> allowed
        headers_emerg = {'Authorization': f'Bearer {doctor_token}', 'X-Access-Purpose': 'EMERGENCY'}
        res_emerg = client.post('/api/v1/search', headers=headers_emerg, json={
            'query': 'UnassignedName',
            'field_name': 'name',
            'search_type': 'SUBSTRING',
            'purpose': 'EMERGENCY'
        })
        assert res_emerg.status_code == 200
        data_emerg = res_emerg.get_json()['data']
        matching_pub_ids_emerg = [p['public_id'] for p in data_emerg['patients']]
        assert unassigned_pat['public_id'] in matching_pub_ids_emerg

