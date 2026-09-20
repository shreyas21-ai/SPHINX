from typing import Dict, Any, List, Optional
from app.models.role import Role
from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.repositories.search_repository import SearchRepository
from app.crypto.aes_cipher import AESCipher
from app.crypto.hmac_indexer import HMACSearchIndexer
from app.utils.privacy_masking import PrivacyMasker
from app.utils.exceptions import NotFoundException, BadRequestException, ForbiddenException


class PatientService:
    @staticmethod
    def create_patient(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypts sensitive demographic fields and creates blind HMAC search indexes."""
        first_name = patient_data.get('first_name')
        last_name = patient_data.get('last_name')

        patient = Patient(
            first_name_enc=AESCipher.encrypt(first_name),
            last_name_enc=AESCipher.encrypt(last_name),
            dob_enc=AESCipher.encrypt(patient_data.get('dob')),
            gender_enc=AESCipher.encrypt(patient_data.get('gender')),
            phone_enc=AESCipher.encrypt(patient_data.get('phone')),
            email_enc=AESCipher.encrypt(patient_data.get('email')),
            address_enc=AESCipher.encrypt(patient_data.get('address')),
            insurance_provider_enc=AESCipher.encrypt(patient_data.get('insurance_provider')),
            policy_number_enc=AESCipher.encrypt(patient_data.get('policy_number')),
            blood_group_enc=AESCipher.encrypt(patient_data.get('blood_group'))
        )
        saved = PatientRepository.create(patient)

        # Generate HMAC searchable index entries
        index_entries = []
        if first_name:
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('first_name', first_name):
                index_entries.append(('first_name', token, t_type, saved.id, None))
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('name', f"{first_name} {last_name or ''}"):
                index_entries.append(('name', token, t_type, saved.id, None))

        if last_name:
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('last_name', last_name):
                index_entries.append(('last_name', token, t_type, saved.id, None))

        if patient_data.get('blood_group'):
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('blood_group', patient_data['blood_group']):
                index_entries.append(('blood_group', token, t_type, saved.id, None))

        if index_entries:
            SearchRepository.add_tokens(index_entries)

        # Return decrypted object representation
        return PatientService.decrypt_and_format_patient(saved, role_name='ADMIN')

    @staticmethod
    def decrypt_and_format_patient(patient: Patient, role_name: str) -> Dict[str, Any]:
        """Decrypts AES-256 field values and applies role-based privacy masking."""
        raw_dict = {
            'public_id': patient.public_id,
            'first_name': AESCipher.decrypt(patient.first_name_enc),
            'last_name': AESCipher.decrypt(patient.last_name_enc),
            'dob': AESCipher.decrypt(patient.dob_enc),
            'gender': AESCipher.decrypt(patient.gender_enc),
            'phone': AESCipher.decrypt(patient.phone_enc),
            'email': AESCipher.decrypt(patient.email_enc),
            'address': AESCipher.decrypt(patient.address_enc),
            'insurance_provider': AESCipher.decrypt(patient.insurance_provider_enc),
            'policy_number': AESCipher.decrypt(patient.policy_number_enc),
            'blood_group': AESCipher.decrypt(patient.blood_group_enc),
            'created_at': patient.created_at.isoformat(),
            'updated_at': patient.updated_at.isoformat()
        }
        return PrivacyMasker.mask_patient_data(raw_dict, role_name)

    @staticmethod
    def get_patient_by_public_id(public_id: str, role_name: str, user_id: Optional[int] = None, purpose: Optional[str] = None) -> Dict[str, Any]:
        patient = PatientRepository.get_by_public_id(public_id)
        if not patient:
            raise NotFoundException("Patient record not found.")

        # Enforce Doctor patient authorization scope
        if role_name == Role.DOCTOR and user_id and (purpose or '').upper() != 'EMERGENCY':
            authorized_patient_ids = PatientRepository.get_authorized_patient_ids_for_doctor(user_id)
            if patient.id not in authorized_patient_ids:
                raise ForbiddenException("Doctor is not authorized to access this patient record.")

        return PatientService.decrypt_and_format_patient(patient, role_name)

    @staticmethod
    def list_patients(role_name: str, page: int = 1, per_page: int = 50, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if role_name == Role.DOCTOR and user_id:
            patients = PatientRepository.get_patients_by_doctor(user_id)
        else:
            patients = PatientRepository.get_all(page=page, per_page=per_page)
        return [PatientService.decrypt_and_format_patient(p, role_name) for p in patients]

    @staticmethod
    def update_patient(public_id: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates patient demographics, maintaining AES encryption and blind HMAC search indexes."""
        patient = PatientRepository.get_by_public_id(public_id)
        if not patient:
            raise NotFoundException("Patient record not found.")

        if 'first_name' in patient_data:
            patient.first_name_enc = AESCipher.encrypt(patient_data['first_name'])
        if 'last_name' in patient_data:
            patient.last_name_enc = AESCipher.encrypt(patient_data['last_name'])
        if 'dob' in patient_data:
            patient.dob_enc = AESCipher.encrypt(patient_data['dob'])
        if 'gender' in patient_data:
            patient.gender_enc = AESCipher.encrypt(patient_data['gender'])
        if 'phone' in patient_data:
            patient.phone_enc = AESCipher.encrypt(patient_data['phone'])
        if 'email' in patient_data:
            patient.email_enc = AESCipher.encrypt(patient_data['email'])
        if 'address' in patient_data:
            patient.address_enc = AESCipher.encrypt(patient_data['address'])
        if 'insurance_provider' in patient_data:
            patient.insurance_provider_enc = AESCipher.encrypt(patient_data['insurance_provider'])
        if 'policy_number' in patient_data:
            patient.policy_number_enc = AESCipher.encrypt(patient_data['policy_number'])
        if 'blood_group' in patient_data:
            patient.blood_group_enc = AESCipher.encrypt(patient_data['blood_group'])

        saved = PatientRepository.update(patient)

        # Decrypt demographic values to rebuild blind HMAC search index
        decrypted_first = AESCipher.decrypt(saved.first_name_enc)
        decrypted_last = AESCipher.decrypt(saved.last_name_enc)
        decrypted_blood = AESCipher.decrypt(saved.blood_group_enc)

        SearchRepository.clear_index_for_patient(saved.id)

        index_entries = []
        if decrypted_first:
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('first_name', decrypted_first):
                index_entries.append(('first_name', token, t_type, saved.id, None))
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('name', f"{decrypted_first} {decrypted_last or ''}"):
                index_entries.append(('name', token, t_type, saved.id, None))

        if decrypted_last:
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('last_name', decrypted_last):
                index_entries.append(('last_name', token, t_type, saved.id, None))

        if decrypted_blood:
            for token, t_type in HMACSearchIndexer.generate_all_index_entries('blood_group', decrypted_blood):
                index_entries.append(('blood_group', token, t_type, saved.id, None))

        if index_entries:
            SearchRepository.add_tokens(index_entries)

        return PatientService.decrypt_and_format_patient(saved, role_name='ADMIN')

    @staticmethod
    def delete_patient(public_id: str) -> None:
        patient = PatientRepository.get_by_public_id(public_id)
        if not patient:
            raise NotFoundException("Patient record not found.")
        SearchRepository.clear_index_for_patient(patient.id)
        PatientRepository.delete(patient)
