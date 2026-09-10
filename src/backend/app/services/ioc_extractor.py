"""
IOC (Indicator of Compromise) extractor.

Extracts common indicators from free-form text using regex:
- IPv4 addresses
- Domain names
- URLs
- MD5/SHA1/SHA256 hashes
- Email addresses
- CVE identifiers
- Windows file paths
- Registry keys
"""

import re
from typing import Dict, List


# ============ Regex patterns ============
_IPV4_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

_DOMAIN_PATTERN = re.compile(
    r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)"
    r"+(?:com|net|org|edu|gov|io|co|info|biz|me|dev|cloud|local|xyz|top|site|online|tech)\b",
    re.IGNORECASE,
)

_URL_PATTERN = re.compile(
    r"https?://[^\s<>\"'\)\]\}]+",
    re.IGNORECASE,
)

_MD5_PATTERN = re.compile(r"\b[a-fA-F0-9]{32}\b")
_SHA1_PATTERN = re.compile(r"\b[a-fA-F0-9]{40}\b")
_SHA256_PATTERN = re.compile(r"\b[a-fA-F0-9]{64}\b")

_EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")

_CVE_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)

_WINDOWS_PATH_PATTERN = re.compile(
    r"\b[A-Za-z]:\\(?:[^\\\/:*?\"<>|\r\n]+\\)*[^\\\/:*?\"<>|\r\n]*"
)

_REGISTRY_KEY_PATTERN = re.compile(
    r"\b(?:HKLM|HKCU|HKCR|HKU|HKCC)\\[^\s]+",
    re.IGNORECASE,
)


# ============ Private IP ranges (filter for meaningful IOCs) ============
_PRIVATE_IP_PREFIXES = ("10.", "192.168.", "127.", "169.254.")
_PRIVATE_IP_172 = re.compile(r"^172\.(1[6-9]|2\d|3[01])\.")


def _is_private_ip(ip: str) -> bool:
    """Check if an IPv4 is private/reserved."""
    if ip.startswith(_PRIVATE_IP_PREFIXES):
        return True
    if _PRIVATE_IP_172.match(ip):
        return True
    return False


def extract_iocs(text: str, include_private_ips: bool = True) -> Dict[str, List[str]]:
    """
    Extract all IOCs from a text.

    Args:
        text: Free-form text (alert description, raw_data serialized, etc.)
        include_private_ips: If False, filters out RFC1918/loopback addresses.

    Returns:
        Dict with keys: ips, domains, urls, md5, sha1, sha256, emails, cves,
                        windows_paths, registry_keys
    """
    if not text:
        return {
            "ips": [],
            "domains": [],
            "urls": [],
            "md5": [],
            "sha1": [],
            "sha256": [],
            "emails": [],
            "cves": [],
            "windows_paths": [],
            "registry_keys": [],
        }

    # IPs
    ips = list(set(_IPV4_PATTERN.findall(text)))
    if not include_private_ips:
        ips = [ip for ip in ips if not _is_private_ip(ip)]

    # URLs (must run before domains to avoid duplicates)
    urls = list(set(_URL_PATTERN.findall(text)))

    # Domains (exclude those inside URLs to reduce noise)
    domains = list(set(_DOMAIN_PATTERN.findall(text)))
    domains = [d for d in domains if not any(d in url for url in urls)]

    # Hashes — order matters (SHA256 before SHA1 before MD5)
    sha256 = list(set(_SHA256_PATTERN.findall(text)))
    sha1 = list(set(_SHA1_PATTERN.findall(text)))
    md5 = list(set(_MD5_PATTERN.findall(text)))

    # Remove overlap (a SHA256 contains no 40-char substring, but SHA1 might
    # accidentally match part of something — we deduplicate by exact length match)
    sha1 = [h for h in sha1 if len(h) == 40]
    md5 = [h for h in md5 if len(h) == 32]

    # Emails
    emails = list(set(_EMAIL_PATTERN.findall(text)))

    # CVEs
    cves = list(set(_CVE_PATTERN.findall(text)))

    # Windows paths
    windows_paths = list(set(_WINDOWS_PATH_PATTERN.findall(text)))

    # Registry keys
    registry_keys = list(set(_REGISTRY_KEY_PATTERN.findall(text)))

    return {
        "ips": sorted(ips),
        "domains": sorted(domains),
        "urls": sorted(urls),
        "md5": sorted(md5),
        "sha1": sorted(sha1),
        "sha256": sorted(sha256),
        "emails": sorted(emails),
        "cves": sorted(cves),
        "windows_paths": sorted(windows_paths),
        "registry_keys": sorted(registry_keys),
    }


def flatten_iocs(iocs: Dict[str, List[str]]) -> List[Dict[str, str]]:
    """
    Convert the IOC dict to a flat list of {type, value} objects.

    Used for storage in Alert.iocs (JSONB).
    """
    result: List[Dict[str, str]] = []
    for ioc_type, values in iocs.items():
        for value in values:
            result.append({"type": ioc_type.rstrip("s"), "value": value})
    return result


def extract_flat_iocs(
    text: str, include_private_ips: bool = True
) -> List[Dict[str, str]]:
    """Convenience: extract + flatten in one call."""
    return flatten_iocs(extract_iocs(text, include_private_ips))
