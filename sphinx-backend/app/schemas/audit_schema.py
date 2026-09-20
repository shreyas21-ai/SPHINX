from marshmallow import Schema, fields


class AuditLogSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    user_role = fields.Str(dump_only=True)
    action = fields.Str(dump_only=True)
    patient_id = fields.Int(dump_only=True)
    purpose = fields.Str(dump_only=True)
    ip_address = fields.Str(dump_only=True)
    user_agent = fields.Str(dump_only=True)
    timestamp = fields.DateTime(dump_only=True)
