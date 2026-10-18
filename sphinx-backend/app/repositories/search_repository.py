from typing import List, Set, Tuple, Optional
import math
from sqlalchemy import func
from app.extensions import db
from app.models.search_index import SearchIndex


class SearchRepository:
    @staticmethod
    def add_tokens(entries: List[Tuple[str, str, str, Optional[int], Optional[int]]]) -> None:
        """
        Batch adds index tokens.
        entries list format: [(field_name, token_hash, token_type, patient_id, record_id)]
        """
        objects = []
        for field_name, token_hash, token_type, patient_id, record_id in entries:
            idx = SearchIndex(
                field_name=field_name,
                token_hash=token_hash,
                token_type=token_type,
                patient_id=patient_id,
                record_id=record_id
            )
            objects.append(idx)
        db.session.bulk_save_objects(objects)
        db.session.commit()

    @staticmethod
    def clear_index_for_record(record_id: int) -> None:
        SearchIndex.query.filter_by(record_id=record_id).delete()
        db.session.commit()

    @staticmethod
    def clear_index_for_patient(patient_id: int) -> None:
        SearchIndex.query.filter_by(patient_id=patient_id).delete()
        db.session.commit()

    @staticmethod
    def find_matching_record_ids_by_exact_tokens(token_field_pairs: List[Tuple[str, str]]) -> Set[int]:
        """
        Finds MedicalRecord IDs that match exact token_field_pairs across candidate fields.
        """
        if not token_field_pairs:
            return set()

        matching_sets = []
        for token_hash, field_name in token_field_pairs:
            query = db.session.query(SearchIndex.record_id).filter(
                SearchIndex.token_hash == token_hash,
                SearchIndex.field_name == field_name,
                SearchIndex.record_id.isnot(None)
            )
            rec_ids = {row.record_id for row in query.all()}
            if rec_ids:
                matching_sets.append(rec_ids)

        if not matching_sets:
            return set()

        # Combine matching record ID sets across candidate fields (OR condition)
        return set.union(*matching_sets)

    @staticmethod
    def find_matching_record_ids_by_ngram_tokens(token_field_pairs: List[Tuple[str, str]], min_match_ratio: float = 0.6) -> Set[int]:
        """
        Finds MedicalRecord IDs matching n-gram substring tokens for each field.
        Calculates threshold matching per record ID using ceil(token_count * min_match_ratio).
        """
        if not token_field_pairs:
            return set()

        # Group tokens by field_name
        field_tokens = {}
        for token_hash, field_name in token_field_pairs:
            field_tokens.setdefault(field_name, []).append(token_hash)

        all_matching_record_ids = set()

        for field_name, tokens in field_tokens.items():
            token_count = len(tokens)
            required_count = max(1, math.ceil(token_count * min_match_ratio))

            # Query records having at least required_count matching n-gram tokens
            results = db.session.query(
                SearchIndex.record_id,
                func.count(SearchIndex.id).label('match_cnt')
            ).filter(
                SearchIndex.field_name == field_name,
                SearchIndex.token_hash.in_(tokens),
                SearchIndex.record_id.isnot(None)
            ).group_by(SearchIndex.record_id).having(func.count(SearchIndex.id) >= required_count).all()

            rec_ids = {row.record_id for row in results}
            all_matching_record_ids.update(rec_ids)

        return all_matching_record_ids

    @staticmethod
    def find_matching_patient_ids_by_ngram_tokens(token_field_pairs: List[Tuple[str, str]], min_match_ratio: float = 0.6) -> Set[int]:
        """
        Finds Patient IDs matching n-gram substring tokens for each field.
        Calculates threshold matching per patient ID to prevent false-positive leakage.
        """
        if not token_field_pairs:
            return set()

        field_tokens = {}
        for token_hash, field_name in token_field_pairs:
            field_tokens.setdefault(field_name, []).append(token_hash)

        all_matching_patient_ids = set()

        for field_name, tokens in field_tokens.items():
            token_count = len(tokens)
            required_count = max(1, math.ceil(token_count * min_match_ratio))

            results = db.session.query(
                SearchIndex.patient_id,
                func.count(SearchIndex.id).label('match_cnt')
            ).filter(
                SearchIndex.field_name == field_name,
                SearchIndex.token_hash.in_(tokens),
                SearchIndex.patient_id.isnot(None)
            ).group_by(SearchIndex.patient_id).having(func.count(SearchIndex.id) >= required_count).all()

            patient_ids = {row.patient_id for row in results}
            all_matching_patient_ids.update(patient_ids)

        return all_matching_patient_ids

    @staticmethod
    def find_matching_patient_ids_by_tokens(token_field_pairs: List[Tuple[str, str]]) -> Set[int]:
        """Finds Patient IDs matching search tokens across fields."""
        if not token_field_pairs:
            return set()

        matching_sets = []
        for token_hash, field_name in token_field_pairs:
            query = db.session.query(SearchIndex.patient_id).filter(
                SearchIndex.token_hash == token_hash,
                SearchIndex.field_name == field_name,
                SearchIndex.patient_id.isnot(None)
            )
            patient_ids = {row.patient_id for row in query.all()}
            if patient_ids:
                matching_sets.append(patient_ids)

        if not matching_sets:
            return set()
        return set.union(*matching_sets)
