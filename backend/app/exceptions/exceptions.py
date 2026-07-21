"""
Custom exceptions for IntelliICU.
"""


class IntelliICUException(Exception):
    """
    Base exception for IntelliICU.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundException(IntelliICUException):
    """
    Raised when a resource is not found.
    """

    pass


class DuplicateResourceException(IntelliICUException):
    """
    Raised when attempting to create a duplicate resource.
    """

    pass


class ValidationException(IntelliICUException):
    """
    Raised for business validation errors.
    """

    pass