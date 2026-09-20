from flask import jsonify


class APIException(Exception):
    """Base Custom Exception for API Errors."""
    def __init__(self, message: str, status_code: int = 400, payload: dict = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        rv = dict(self.payload)
        rv['status'] = 'error'
        rv['message'] = self.message
        return rv


class BadRequestException(APIException):
    def __init__(self, message: str = "Bad Request", payload: dict = None):
        super().__init__(message, status_code=400, payload=payload)


class UnauthorizedException(APIException):
    def __init__(self, message: str = "Authentication credentials required", payload: dict = None):
        super().__init__(message, status_code=401, payload=payload)


class ForbiddenException(APIException):
    def __init__(self, message: str = "Access forbidden: Insufficient permissions", payload: dict = None):
        super().__init__(message, status_code=403, payload=payload)


class NotFoundException(APIException):
    def __init__(self, message: str = "Requested resource not found", payload: dict = None):
        super().__init__(message, status_code=404, payload=payload)


class PurposeRequiredException(APIException):
    def __init__(self, message: str = "Access Purpose (TREATMENT, BILLING, RESEARCH, EMERGENCY) is required in X-Access-Purpose header or request body."):
        super().__init__(message, status_code=400)


def register_error_handlers(app):
    """Registers global error handlers with Flask application factory."""

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal Server Error'
        }), 500
