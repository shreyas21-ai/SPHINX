from typing import Dict, Any, List, Optional
from app.models.role import Role
from app.models.medical_record import MedicalRecord
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.repositories.search_repository import SearchRepository
from app.crypto.aes_cipher import AESCipher
from app.crypto.hmac_indexer import HMACSearchIndexer
from app.utils.privacy_masking import PrivacyMasker
from app.utils.exceptions import NotFoundException, BadRequestException, ForbiddenException


class MedicalRecordService:
    @staticmethod
    def create_record(record_data: Dict[str, Any], doctor_id: int) -> Dict[str, Any]:
        """Encrypts sensitive clinical fields with AES-256 and populates HMAC search index."""
        patient_public_id = record_data.get('patient_public_id')
        patient = PatientRepository.get_by_public_id(patient_public_id)
        if not patient:
            raise NotFoundException("Patient not found.")

        doctor = UserRepository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor user not found.")

        record = MedicalRecord(
            patient_id=patient.id,
            doctor_id=doctor.id,
            disease_enc=AESCipher.encrypt(record_data.get('disease')),
            diagnosis_enc=AESCipher.encrypt(record_data.get('diagnosis')),
            medical_history_enc=AESCipher.encrypt(record_data.get('medical_history')),
            prescription_enc=AESCipher.encrypt(record_data.get('prescription')),
            lab_reports_enc=AESCipher.encrypt(record_data.get('lab_reports')),
            doctor_notes_enc=AESCipher.encrypt(record_data.get('doctor_notes')),
            insurance_details_enc=AESCipher.encrypt(record_data.get('insurance_details')),
            treatment_plan_enc=AESCipher.encrypt(record_data.get('treatment_plan')),
            allergies_enc=AESCipher.encrypt(record_data.get('allergies')),
            vitals_enc=AESCipher.encrypt(record_data.get('vitals'))
        )
        saved = MedicalRecordRepository.create(record)

        # Build HMAC searchable index entries for clinical search fields
        index_entries = []
        searchable_fields = ['disease', 'diagnosis', 'allergies', 'treatment_plan', 'prescription']

        for field in searchable_fields:
            val = record_data.get(field)
            if val:
                for token, t_type in HMACSearchIndexer.generate_all_index_entries(field, val):
                    index_entries.append((field, token, t_type, patient.id, saved.id))

        if index_entries:
            SearchRepository.add_tokens(index_entries)

        return MedicalRecordService.decrypt_and_format_record(saved, role_name='DOCTOR')

    @staticmethod
    def decrypt_and_format_record(record: MedicalRecord, role_name: str) -> Dict[str, Any]:
        """Decrypts AES-256 fields and applies role-based privacy exposure rules."""
        patient = PatientRepository.get_by_id(record.patient_id)
        doctor = UserRepository.get_by_id(record.doctor_id)

        raw_dict = {
            'public_id': record.public_id,
            'patient_public_id': patient.public_id if patient else None,
            'doctor_email': doctor.email if doctor else None,
            'disease': AESCipher.decrypt(record.disease_enc),
            'diagnosis': AESCipher.decrypt(record.diagnosis_enc),
            'medical_history': AESCipher.decrypt(record.medical_history_enc),
            'prescription': AESCipher.decrypt(record.prescription_enc),
            'lab_reports': AESCipher.decrypt(record.lab_reports_enc),
            'doctor_notes': AESCipher.decrypt(record.doctor_notes_enc),
            'insurance_details': AESCipher.decrypt(record.insurance_details_enc),
            'treatment_plan': AESCipher.decrypt(record.treatment_plan_enc),
            'allergies': AESCipher.decrypt(record.allergies_enc),
            'vitals': AESCipher.decrypt(record.vitals_enc),
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat()
        }
        return PrivacyMasker.mask_medical_record(raw_dict, role_name)

    @staticmethod
    def get_record_by_public_id(public_id: str, role_name: str, user_id: Optional[int] = None, purpose: Optional[str] = None) -> Dict[str, Any]:
        record = MedicalRecordRepository.get_by_public_id(public_id)
        if not record:
            raise NotFoundException("Medical record not found.")

        # Enforce Doctor patient authorization scope
        if role_name == Role.DOCTOR and user_id and (purpose or '').upper() != 'EMERGENCY':
            authorized_patient_ids = PatientRepository.get_authorized_patient_ids_for_doctor(user_id)
            if record.patient_id not in authorized_patient_ids:
                raise ForbiddenException("Doctor is not authorized to access this medical record.")

        return MedicalRecordService.decrypt_and_format_record(record, role_name)

    @staticmethod
    def get_patient_records(patient_public_id: str, role_name: str, user_id: Optional[int] = None, purpose: Optional[str] = None) -> List[Dict[str, Any]]:
        patient = PatientRepository.get_by_public_id(patient_public_id)
        if not patient:
            raise NotFoundException("Patient not found.")

        # Enforce Doctor patient authorization scope
        if role_name == Role.DOCTOR and user_id and (purpose or '').upper() != 'EMERGENCY':
            authorized_patient_ids = PatientRepository.get_authorized_patient_ids_for_doctor(user_id)
            if patient.id not in authorized_patient_ids:
                raise ForbiddenException("Doctor is not authorized to access this patient's medical history.")

        records = MedicalRecordRepository.get_by_patient_id(patient.id)
        return [MedicalRecordService.decrypt_and_format_record(r, role_name) for r in records]

    @staticmethod
    def delete_record(public_id: str) -> None:
        record = MedicalRecordRepository.get_by_public_id(public_id)
        if not record:
            raise NotFoundException("Medical record not found.")
        SearchRepository.clear_index_for_record(record.id)
        MedicalRecordRepository.delete(record)
