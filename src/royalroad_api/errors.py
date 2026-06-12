"""Errors mirroring the TS lib's RoyalError."""

from __future__ import annotations


class RoyalError(Exception):
    """Raised when a request fails or RoyalRoad returns an error page.

    RR always responds with HTTP 200, embedding errors (404/403, validation
    failures) in the page body, so most errors surface here from the body
    parser rather than from an HTTP status code.
    """

    def __init__(self, message: str, data: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.data = data or {}
