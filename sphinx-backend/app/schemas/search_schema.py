from marshmallow import Schema, fields, validate


class SearchQuerySchema(Schema):
    # Flexible multi-field query parameters
    query = fields.Str(required=False)  # General free text search term
    field_name = fields.Str(required=False)  # Specific field search target e.g. 'disease', 'name', 'blood_group'
    disease = fields.Str(required=False)
    name = fields.Str(required=False)
    blood_group = fields.Str(required=False)
    search_type = fields.Str(required=False, validate=validate.OneOf(['EXACT', 'SUBSTRING', 'MULTI_FIELD']))
    purpose = fields.Str(required=False, validate=validate.OneOf(['TREATMENT', 'BILLING', 'RESEARCH', 'EMERGENCY', 'ADMINISTRATIVE']))
