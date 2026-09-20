from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.appointment_schema import AppointmentCreateSchema
from app.services.appointment_service import AppointmentService
from app.utils.rbac import roles_allowed
from app.utils.audit_decorator import audit_log
from app.models.role import Role

appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/v1/appointments')
appointment_create_schema = AppointmentCreateSchema()


@appointments_bp.route('', methods=['POST'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.RECEPTIONIST)
@audit_log(action='CREATE_APPOINTMENT', require_purpose=False)
def create_appointment():
    data = request.get_json() or {}
    errors = appointment_create_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    apt = AppointmentService.create_appointment(data)
    return jsonify({
        'status': 'success',
        'message': 'Appointment scheduled successfully.',
        'data': apt
    }), 201


@appointments_bp.route('', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST)
def list_appointments():
    user_id = int(get_jwt_identity())
    from app.repositories.user_repository import UserRepository
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'RECEPTIONIST'

    apts = AppointmentService.list_appointments(role_name=role_name, user_id=user_id)
    return jsonify({
        'status': 'success',
        'total': len(apts),
        'data': apts
    }), 200


@appointments_bp.route('/<public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST)
def get_appointment(public_id):
    apt = AppointmentService.get_appointment_by_public_id(public_id)
    return jsonify({
        'status': 'success',
        'data': apt
    }), 200


@appointments_bp.route('/<public_id>/status', methods=['PATCH'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.RECEPTIONIST)
@audit_log(action='UPDATE_APPOINTMENT_STATUS', require_purpose=False)
def update_appointment_status(public_id):
    user_id = int(get_jwt_identity())
    from app.repositories.user_repository import UserRepository
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else ''

    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'status': 'error', 'message': 'Status field is required.'}), 400

    if role_name == Role.RECEPTIONIST and status == 'COMPLETED':
        return jsonify({'status': 'error', 'message': 'Receptionists are not authorized to mark appointments as COMPLETED.'}), 403

    updated = AppointmentService.update_status(public_id, status)
    return jsonify({
        'status': 'success',
        'message': 'Appointment status updated.',
        'data': updated
    }), 200
