class Keysight33600AError(Exception):
    """Base class for all 33600A library errors."""


class ConnectionError33600A(Keysight33600AError):
    """Raised for connection/open/close related failures."""


class SCPICommandError(Keysight33600AError):
    """Raised when instrument reports SCPI errors."""


class ValidationError33600A(Keysight33600AError):
    """Raised when caller input is outside accepted range/format."""
