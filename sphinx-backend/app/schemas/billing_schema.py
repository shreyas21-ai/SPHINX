from marshmallow import Schema, fields, validate


class BillingItemSchema(Schema):
    item_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Float(required=True, validate=validate.Range(min=0.0))
    amount = fields.Float(dump_only=True)


class BillingCreateSchema(Schema):
    patient_public_id = fields.Str(required=True)
    items = fields.List(fields.Nested(BillingItemSchema), required=True, validate=validate.Length(min=1))
    approved_amount = fields.Float(required=False, load_default=0.0)
    insurance_provider = fields.Str(required=False)
    policy_number = fields.Str(required=False)
    claim_notes = fields.Str(required=False)


class BillingResponseSchema(Schema):
    public_id = fields.Str(dump_only=True)
    patient_public_id = fields.Str(dump_only=True)
    items = fields.List(fields.Nested(BillingItemSchema))
    total_bill = fields.Float()
    approved_amount = fields.Float()
    patient_payable = fields.Float()
    insurance_provider = fields.Str()
    policy_number = fields.Str()
    claim_status = fields.Str()
    claim_notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)
