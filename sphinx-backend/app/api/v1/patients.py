from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.patient_schema import PatientCreateSchema, PatientUpdateSchema
from app.services.patient_service import PatientService
from app.repositories.user_repository import UserRepository
from app.utils.rbac import roles_allowed
from app.utils.audit_decorator import audit_log
from app.models.role import Role

patients_bp = Blueprint('patients', __name__, url_prefix='/api/v1/patients')
patient_create_schema = PatientCreateSchema()
patient_update_schema = PatientUpdateSchema()


@patients_bp.route('', methods=['POST'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.RECEPTIONIST)
@audit_log(action='CREATE_PATIENT', require_purpose=False)
def create_patient():
    data = request.get_json() or {}
    errors = patient_create_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    patient_dict = PatientService.create_patient(data)
    return jsonify({
        'status': 'success',
        'message': 'Patient record created and encrypted successfully.',
        'data': patient_dict
    }), 201


@patients_bp.route('', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST, Role.INSURANCE_OFFICER)
@audit_log(action='LIST_PATIENTS', require_purpose=True)
def list_patients():
    user_id = int(get_jwt_identity())
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'RECEPTIONIST'

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    patients = PatientService.list_patients(role_name=role_name, page=page, per_page=per_page, user_id=user_id)
    return jsonify({
        'status': 'success',
        'total': len(patients),
        'data': patients
    }), 200


@patients_bp.route('/<public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST, Role.INSURANCE_OFFICER)
@audit_log(action='VIEW_PATIENT_DEMOGRAPHICS', require_purpose=True)
def get_patient(public_id):
    user_id = int(get_jwt_identity())
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'RECEPTIONIST'
    purpose = request.headers.get('X-Access-Purpose') or request.args.get('purpose')

    patient = PatientService.get_patient_by_public_id(public_id, role_name=role_name, user_id=user_id, purpose=purpose)
    return jsonify({
        'status': 'success',
        'data': patient
    }), 200


@patients_bp.route('/<public_id>', methods=['PUT'])
@jwt_required()
@roles_allowed(Role.ADMIN)
@audit_log(action='UPDATE_PATIENT', require_purpose=False)
def update_patient(public_id):
    data = request.get_json() or {}
    errors = patient_update_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    patient_dict = PatientService.update_patient(public_id, data)
    return jsonify({
        'status': 'success',
        'message': 'Patient record updated, encrypted, and search indices refreshed.',
        'data': patient_dict
    }), 200


@patients_bp.route('/<public_id>', methods=['DELETE'])
@jwt_required()
@roles_allowed(Role.ADMIN)
@audit_log(action='DELETE_PATIENT', require_purpose=False)
def delete_patient(public_id):
    PatientService.delete_patient(public_id)
    return jsonify({
        'status': 'success',
        'message': 'Patient record and cryptographic indices deleted.'
    }), 200
