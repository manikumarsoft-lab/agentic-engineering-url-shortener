import pytest

from shortener.codes import ALPHABET, CODE_PATTERN, generate
from shortener.validation import InvalidURL, validate_url

SELF = frozenset({"sho.rt"})


@pytest.mark.parametrize("raw, expected", [
    ("https://example.com/a?b=1#c", "https://example.com/a?b=1#c"),
    ("HTTP://Example.COM", "http://example.com/"),
    ("https://example.com:443/x", "https://example.com/x"),
    ("https://example.com:8443/x", "https://example.com:8443/x"),
    ("https://8.8.8.8/dns", "https://8.8.8.8/dns"),
    ("https://bücher.example/", "https://xn--bcher-kva.example/"),
])
def test_valid_urls_are_normalized(raw, expected):
    assert validate_url(raw, self_hosts=SELF) == expected


@pytest.mark.parametrize("raw, code", [
    ("", "malformed_url"),
    ("javascript:alert(1)", "scheme_not_allowed"),
    ("data:text/html,hi", "scheme_not_allowed"),
    ("file:///etc/passwd", "scheme_not_allowed"),
    ("ftp://example.com/f", "scheme_not_allowed"),
    ("https://user:pw@example.com/", "credentials_in_url"),
    ("https://user@example.com/", "credentials_in_url"),
    ("http://127.0.0.1/", "private_address_not_allowed"),
    ("http://10.1.2.3/", "private_address_not_allowed"),
    ("http://192.168.0.1/", "private_address_not_allowed"),
    ("http://169.254.169.254/latest/meta-data", "private_address_not_allowed"),
    ("http://[::1]/", "private_address_not_allowed"),
    ("http://[fe80::1]/", "private_address_not_allowed"),
    ("http://0.0.0.0/", "private_address_not_allowed"),
    ("http://localhost:8000/", "private_address_not_allowed"),
    ("http://api.localhost/", "private_address_not_allowed"),
    ("https://sho.rt/abc1234", "self_referential_url"),
    ("https://www.sho.rt/abc1234", "self_referential_url"),
    ("https://example.com/" + "a" * 2049, "url_too_long"),
    ("https://example.com/a b", "invalid_characters"),
    ("https://example.com/\x00", "invalid_characters"),
    ("https:///nohost", "malformed_url"),
    ("https://example.com:99999/", "malformed_url"),
])
def test_invalid_urls_are_rejected_with_a_reason(raw, code):
    with pytest.raises(InvalidURL) as err:
        validate_url(raw, self_hosts=SELF)
    assert err.value.code == code


def test_length_limit_is_inclusive():
    url = "https://example.com/" + "a" * (2048 - len("https://example.com/"))
    assert len(url) == 2048
    assert validate_url(url, self_hosts=SELF) == url


def test_codes_are_random_base62_of_length_7():
    sample = [generate() for _ in range(2000)]
    assert all(len(c) == 7 and CODE_PATTERN.match(c) and set(c) <= set(ALPHABET) for c in sample)
    assert len(set(sample)) == len(sample)
