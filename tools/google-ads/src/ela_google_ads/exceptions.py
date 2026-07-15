"""Typed exceptions for the ELA Google Ads toolkit."""

from __future__ import annotations


class ElaGoogleAdsError(Exception):
    """Base error for the toolkit."""


class ConfigurationError(ElaGoogleAdsError):
    """Missing or invalid local configuration."""


class ValidationError(ElaGoogleAdsError):
    """Campaign-spec or input validation failed."""

    def __init__(self, message: str, *, issues: list[str] | None = None) -> None:
        super().__init__(message)
        self.issues = issues or []


class MutationSafetyError(ElaGoogleAdsError):
    """A mutating operation was blocked by safety guards."""


class ApiAccessError(ElaGoogleAdsError):
    """Google Ads API access or authentication failure."""


class CredentialRequiredError(ConfigurationError):
    """Live credentials are required for this operation."""
