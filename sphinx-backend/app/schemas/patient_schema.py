from marshmallow import Schema, fields, validate


class PatientCreateSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    dob = fields.Str(required=False)
    gender = fields.Str(required=False)
    phone = fields.Str(required=False)
    email = fields.Email(required=False)
    address = fields.Str(required=False)
    insurance_provider = fields.Str(required=False)
    policy_number = fields.Str(required=False)
    blood_group = fields.Str(required=False)

class PatientUpdateSchema(Schema):
    first_name = fields.Str(required=False, validate=validate.Length(min=1, max=80))
    last_name = fields.Str(required=False, validate=validate.Length(min=1, max=80))
    dob = fields.Str(required=False)
    gender = fields.Str(required=False)
    phone = fields.Str(required=False)
    email = fields.Email(required=False)
    address = fields.Str(required=False)
    insurance_provider = fields.Str(required=False)
    policy_number = fields.Str(required=False)
    blood_group = fields.Str(required=False)


class PatientResponseSchema(Schema):
    public_id = fields.Str(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    dob = fields.Str()
    gender = fields.Str()
    phone = fields.Str()
    email = fields.Str()
    address = fields.Str()
    insurance_provider = fields.Str()
    policy_number = fields.Str()
    blood_group = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
