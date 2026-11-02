"""Official Python client for the Plagiarism Checker Plus API."""

from .client import (
    DEFAULT_BASE_URL,
    ErrorCodes,
    PlagiarismCheckerPlus,
    PlagiarismCheckerPlusError,
    ScanTimeoutError,
    parse_retry_after,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "ErrorCodes",
    "PlagiarismCheckerPlus",
    "PlagiarismCheckerPlusError",
    "ScanTimeoutError",
    "parse_retry_after",
]
__version__ = "1.0.0"
