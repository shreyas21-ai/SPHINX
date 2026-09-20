from marshmallow import Schema, fields, validate


class AppointmentCreateSchema(Schema):
    patient_public_id = fields.Str(required=True)
    doctor_public_id = fields.Str(required=True)
    nurse_public_id = fields.Str(required=False)
    appointment_date = fields.DateTime(required=True)
    reason = fields.Str(required=False, validate=validate.Length(max=255))


class AppointmentResponseSchema(Schema):
    public_id = fields.Str(dump_only=True)
    patient_public_id = fields.Str(dump_only=True)
    doctor_public_id = fields.Str(dump_only=True)
    appointment_date = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    reason = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
