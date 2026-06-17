class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str, fields=None):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.fields = fields
        super().__init__(message)
