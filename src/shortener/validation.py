"""Destination URL validation and normalization.

Satisfies: FR-SHR-002, FR-SHR-003, FR-SHR-004, NFR-SEC-001, PD-001, PVT-010.
"""
from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit, urlunsplit

ALLOWED_SCHEMES = frozenset({"http", "https"})
DEFAULT_PORTS = {"http": 80, "https": 443}


class InvalidURL(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _blocked_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
            or ip.is_unspecified or ip.is_reserved)


def validate_url(raw: str, *, self_hosts: frozenset[str], max_length: int = 2048) -> str:
    """Return the normalized URL or raise InvalidURL with a machine-readable code."""
    if not raw or not raw.strip():
        raise InvalidURL("malformed_url", "URL is empty")
    if len(raw) > max_length:
        raise InvalidURL("url_too_long", f"URL exceeds {max_length} characters")
    if any(ord(ch) <= 32 or ord(ch) == 127 for ch in raw):
        raise InvalidURL("invalid_characters", "URL contains whitespace or control characters")
    try:
        parts = urlsplit(raw)
        port = parts.port
    except ValueError:
        raise InvalidURL("malformed_url", "URL cannot be parsed") from None
    scheme = parts.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise InvalidURL("scheme_not_allowed", "only http and https URLs are accepted")
    if "@" in parts.netloc:
        raise InvalidURL("credentials_in_url", "URLs with embedded credentials are not accepted")
    host = (parts.hostname or "").rstrip(".").lower()
    if not host:
        raise InvalidURL("malformed_url", "URL has no host")
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        raise InvalidURL("malformed_url", "host name is not valid") from None
    if host == "localhost" or host.endswith(".localhost") or _blocked_ip(host):
        raise InvalidURL("private_address_not_allowed", "private, loopback and link-local hosts are not accepted")
    if any(host == h or host.endswith("." + h) for h in self_hosts if h):
        raise InvalidURL("self_referential_url", "URLs pointing to this shortener are not accepted")
    netloc = f"[{host}]" if ":" in host else host
    if port is not None and port != DEFAULT_PORTS[scheme]:
        netloc += f":{port}"
    return urlunsplit((scheme, netloc, parts.path or "/", parts.query, parts.fragment))
