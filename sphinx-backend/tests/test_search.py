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
