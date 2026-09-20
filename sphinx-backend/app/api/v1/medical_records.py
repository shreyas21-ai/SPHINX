from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.medical_record_schema import MedicalRecordCreateSchema
from app.services.medical_record_service import MedicalRecordService
from app.repositories.user_repository import UserRepository
from app.utils.rbac import roles_allowed
from app.utils.audit_decorator import audit_log
from app.models.role import Role

medical_records_bp = Blueprint('medical_records', __name__, url_prefix='/api/v1/medical-records')
record_create_schema = MedicalRecordCreateSchema()


@medical_records_bp.route('', methods=['POST'])
@jwt_required()
@roles_allowed(Role.DOCTOR)
@audit_log(action='CREATE_MEDICAL_RECORD', require_purpose=False)
def create_medical_record():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    errors = record_create_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    rec = MedicalRecordService.create_record(data, doctor_id=user_id)
    return jsonify({
        'status': 'success',
        'message': 'Medical record created, encrypted with AES-256, and indexed.',
        'data': rec
    }), 201


@medical_records_bp.route('/<public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.DOCTOR, Role.NURSE, Role.INSURANCE_OFFICER)
@audit_log(action='VIEW_MEDICAL_RECORD', require_purpose=True)
def get_medical_record(public_id):
    user_id = int(get_jwt_identity())
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'NURSE'
    purpose = request.headers.get('X-Access-Purpose') or request.args.get('purpose')

    rec = MedicalRecordService.get_record_by_public_id(public_id, role_name=role_name, user_id=user_id, purpose=purpose)
    return jsonify({
        'status': 'success',
        'data': rec
    }), 200


@medical_records_bp.route('/patient/<patient_public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.DOCTOR, Role.NURSE, Role.INSURANCE_OFFICER)
@audit_log(action='VIEW_PATIENT_MEDICAL_HISTORY', require_purpose=True)
def get_patient_medical_records(patient_public_id):
    user_id = int(get_jwt_identity())
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'NURSE'
    purpose = request.headers.get('X-Access-Purpose') or request.args.get('purpose')

    records = MedicalRecordService.get_patient_records(patient_public_id, role_name=role_name, user_id=user_id, purpose=purpose)
    return jsonify({
        'status': 'success',
        'total': len(records),
        'data': records
    }), 200


@medical_records_bp.route('/<public_id>', methods=['DELETE'])
@jwt_required()
@roles_allowed(Role.ADMIN)
@audit_log(action='DELETE_MEDICAL_RECORD', require_purpose=False)
def delete_medical_record(public_id):
    MedicalRecordService.delete_record(public_id)
    return jsonify({
        'status': 'success',
        'message': 'Medical record and associated search indices deleted.'
    }), 200
