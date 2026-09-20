from marshmallow import Schema, fields, validate


class MedicalRecordCreateSchema(Schema):
    patient_public_id = fields.Str(required=True)
    disease = fields.Str(required=False)
    diagnosis = fields.Str(required=False)
    medical_history = fields.Str(required=False)
    prescription = fields.Str(required=False)
    lab_reports = fields.Str(required=False)
    doctor_notes = fields.Str(required=False)
    insurance_details = fields.Str(required=False)
    treatment_plan = fields.Str(required=False)
    allergies = fields.Str(required=False)
    vitals = fields.Str(required=False)


class MedicalRecordResponseSchema(Schema):
    public_id = fields.Str(dump_only=True)
    patient_public_id = fields.Str(dump_only=True)
    doctor_email = fields.Str(dump_only=True)
    disease = fields.Str()
    diagnosis = fields.Str()
    medical_history = fields.Str()
    prescription = fields.Str()
    lab_reports = fields.Str()
    doctor_notes = fields.Str()
    insurance_details = fields.Str()
    treatment_plan = fields.Str()
    allergies = fields.Str()
    vitals = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
