"""Exceptions for handling errors with the WPPBAV Fount API."""


class APIError(Exception):
    """Exception for errors interacting with APIs."""


class DataNotFoundError(APIError):
    """Exception for when the request returns no data."""


class RateLimitExceededError(APIError):
    """Exception for when the request exceeds the rate limit."""
