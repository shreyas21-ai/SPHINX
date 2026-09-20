from typing import Dict, Any, List, Set, Optional
from app.repositories.search_repository import SearchRepository
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.repositories.patient_repository import PatientRepository
from app.services.medical_record_service import MedicalRecordService
from app.services.patient_service import PatientService
from app.crypto.hmac_indexer import HMACSearchIndexer
from app.models.role import Role


class SearchService:
    """
    Searchable Encryption Service.
    Executes Exact, Substring, and Multi-field cryptographic searches on HMAC indexes.
    Fetches and decrypts ONLY records matching HMAC tokens. Never performs database scans.
    """

    @staticmethod
    def search_records(criteria: Dict[str, Any], role_name: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes cryptographic HMAC search over encrypted indexes.
        Supports:
        - `query` / `field_name` ('disease', 'diagnosis', 'allergies', 'name', 'blood_group', 'all')
        - `search_type`: 'EXACT', 'SUBSTRING', 'MULTI_FIELD'
        """
        search_type = (criteria.get('search_type') or 'SUBSTRING').upper()
        target_field = criteria.get('field_name')
        query_val = criteria.get('query') or criteria.get('disease') or criteria.get('name') or ''
        purpose = (criteria.get('purpose') or '').upper()

        exact_token_pairs = []
        ngram_token_pairs = []

        # Determine target fields to search
        searchable_fields = ['disease', 'diagnosis', 'allergies', 'treatment_plan', 'prescription', 'name', 'blood_group']
        if target_field and target_field in searchable_fields:
            fields_to_search = [target_field]
        else:
            fields_to_search = ['disease', 'diagnosis', 'allergies', 'name', 'blood_group']

        # Include additional blood group filter if multi-field
        blood_group_val = criteria.get('blood_group')

        for field_name in fields_to_search:
            val_to_use = query_val
            if field_name == 'blood_group' and blood_group_val:
                val_to_use = blood_group_val

            if not val_to_use:
                continue

            if search_type == 'EXACT':
                token = HMACSearchIndexer.generate_exact_token(field_name, val_to_use)
                if token:
                    exact_token_pairs.append((token, field_name))
            else:  # SUBSTRING or MULTI_FIELD
                exact_tok = HMACSearchIndexer.generate_exact_token(field_name, val_to_use)
                if exact_tok:
                    exact_token_pairs.append((exact_tok, field_name))

                ngrams = HMACSearchIndexer.generate_ngram_tokens(field_name, val_to_use)
                for ng in ngrams:
                    ngram_token_pairs.append((ng, field_name))

        matching_record_ids: Set[int] = set()

        if search_type == 'EXACT':
            matching_record_ids = SearchRepository.find_matching_record_ids_by_exact_tokens(exact_token_pairs)
        else:
            matching_record_ids = SearchRepository.find_matching_record_ids_by_exact_tokens(exact_token_pairs)
            if not matching_record_ids and ngram_token_pairs:
                matching_record_ids = SearchRepository.find_matching_record_ids_by_ngram_tokens(ngram_token_pairs)

        matching_patient_ids = SearchRepository.find_matching_patient_ids_by_tokens(exact_token_pairs + ngram_token_pairs)

        # Enforce Doctor patient authorization scope
        if role_name == Role.DOCTOR and user_id and purpose != 'EMERGENCY':
            authorized_patient_ids = PatientRepository.get_authorized_patient_ids_for_doctor(user_id)
            matching_patient_ids = matching_patient_ids.intersection(authorized_patient_ids)

            # Filter medical records to authorized patients
            matching_records_list = MedicalRecordRepository.get_by_ids(list(matching_record_ids))
            matching_record_ids = {r.id for r in matching_records_list if r.patient_id in authorized_patient_ids}

        # Retrieve and decrypt ONLY matching authorized records
        matching_records = MedicalRecordRepository.get_by_ids(list(matching_record_ids))
        decrypted_results = [
            MedicalRecordService.decrypt_and_format_record(rec, role_name)
            for rec in matching_records
        ]

        matching_patients = PatientRepository.get_by_ids(list(matching_patient_ids))
        decrypted_patients = [
            PatientService.decrypt_and_format_patient(pat, role_name)
            for pat in matching_patients
        ]

        return {
            'total_matching_medical_records': len(decrypted_results),
            'total_matching_patients': len(decrypted_patients),
            'medical_records': decrypted_results,
            'patients': decrypted_patients,
            'search_telemetry': {
                'search_type': search_type,
                'decrypted_records_count': len(decrypted_results),
                'full_db_scanned': False  # Always False in SPHINX architecture
            }
        }
