from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.billing_schema import BillingCreateSchema
from app.services.billing_service import BillingService
from app.utils.rbac import roles_allowed
from app.utils.audit_decorator import audit_log
from app.models.role import Role

billing_bp = Blueprint('billing', __name__, url_prefix='/api/v1/billing')
billing_create_schema = BillingCreateSchema()


@billing_bp.route('', methods=['POST'])
@jwt_required()
@roles_allowed(Role.INSURANCE_OFFICER)
@audit_log(action='CREATE_BILLING_CLAIM', require_purpose=True)
def create_billing_claim():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    errors = billing_create_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    result = BillingService.create_billing_claim(data, officer_id=user_id)
    return jsonify({
        'status': 'success',
        'message': 'Billing statement and insurance claim processed successfully.',
        'data': result
    }), 201


@billing_bp.route('/patient/<patient_public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.INSURANCE_OFFICER, Role.DOCTOR)
@audit_log(action='VIEW_PATIENT_BILLING_CLAIMS', require_purpose=True)
def get_patient_billing_records(patient_public_id):
    records = BillingService.get_patient_billing_records(patient_public_id)
    return jsonify({
        'status': 'success',
        'total': len(records),
        'data': records
    }), 200


@billing_bp.route('/<public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.INSURANCE_OFFICER, Role.DOCTOR)
@audit_log(action='VIEW_BILLING_CLAIM_DETAIL', require_purpose=True)
def get_billing_record(public_id):
    record = BillingService.get_billing_record_by_public_id(public_id)
    return jsonify({
        'status': 'success',
        'data': record
    }), 200
