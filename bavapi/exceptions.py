"""Exceptions for handling errors with the Fount API."""


class APIError(Exception):
    """Exception for errors interacting with APIs."""


class DataNotFoundError(Exception):
    """Exception for when the request returns no data."""


class RateLimitExceededError(Exception):
    """Exception for when the request exceeds the rate limit."""
