"""
Unit tests for IOC extractor.
"""
from app.services.ioc_extractor import (
    extract_iocs,
    extract_flat_iocs,
    flatten_iocs,
    _is_private_ip,
)


class TestIPv4Extraction:
    def test_simple_ip(self):
        result = extract_iocs("Connection from 8.8.8.8 detected")
        assert "8.8.8.8" in result["ips"]

    def test_multiple_ips(self):
        result = extract_iocs("IPs: 1.1.1.1, 2.2.2.2, 3.3.3.3")
        assert len(result["ips"]) == 3

    def test_invalid_ip_rejected(self):
        result = extract_iocs("Not an IP: 999.999.999.999")
        assert result["ips"] == []

    def test_private_ip_detected(self):
        assert _is_private_ip("192.168.1.1") is True
        assert _is_private_ip("10.0.0.1") is True
        assert _is_private_ip("172.16.5.5") is True
        assert _is_private_ip("8.8.8.8") is False

    def test_filter_private_ips(self):
        text = "Public: 8.8.8.8, Private: 192.168.1.1"
        result = extract_iocs(text, include_private_ips=False)
        assert "8.8.8.8" in result["ips"]
        assert "192.168.1.1" not in result["ips"]


class TestDomainExtraction:
    def test_simple_domain(self):
        result = extract_iocs("Visit evil.com for more info")
        assert "evil.com" in result["domains"]

    def test_multiple_tlds(self):
        result = extract_iocs("Domains: bad.net, worse.org, evil.io")
        assert "bad.net" in result["domains"]
        assert "worse.org" in result["domains"]
        assert "evil.io" in result["domains"]


class TestURLExtraction:
    def test_https_url(self):
        result = extract_iocs("Payload at https://evil.com/malware.exe")
        assert any("evil.com" in u for u in result["urls"])

    def test_http_url(self):
        result = extract_iocs("Visit http://bad.site/path?x=1")
        assert any("bad.site" in u for u in result["urls"])

    def test_urls_and_domains_not_duplicated(self):
        text = "URL: https://evil.com/path"
        result = extract_iocs(text)
        # The domain is inside a URL, should not appear in domains list
        assert "evil.com" not in result["domains"]


class TestHashExtraction:
    def test_md5(self):
        md5 = "5d41402abc4b2a76b9719d911017c592"
        result = extract_iocs(f"Hash: {md5}")
        assert md5 in result["md5"]

    def test_sha1(self):
        sha1 = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
        result = extract_iocs(f"SHA1: {sha1}")
        assert sha1 in result["sha1"]

    def test_sha256(self):
        sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        result = extract_iocs(f"SHA256: {sha256}")
        assert sha256 in result["sha256"]

    def test_no_hash_overlap(self):
        """Ensure 32-char MD5 not matched as SHA1 part etc."""
        md5 = "5d41402abc4b2a76b9719d911017c592"
        result = extract_iocs(md5)
        assert md5 in result["md5"]
        assert result["sha1"] == []
        assert result["sha256"] == []


class TestEmailExtraction:
    def test_email(self):
        result = extract_iocs("Contact attacker@evil.com immediately")
        assert "attacker@evil.com" in result["emails"]


class TestCVEExtraction:
    def test_cve(self):
        result = extract_iocs("Exploited CVE-2024-12345")
        assert "CVE-2024-12345" in result["cves"]

    def test_cve_case_insensitive(self):
        result = extract_iocs("cve-2024-12345")
        assert "CVE-2024-12345" in result["cves"] or "cve-2024-12345" in result["cves"]


class TestWindowsPathExtraction:
    def test_windows_path(self):
        result = extract_iocs(r"Suspicious file: C:\Windows\System32\evil.dll")
        assert any("Windows" in p for p in result["windows_paths"])


class TestRegistryKeyExtraction:
    def test_hklm(self):
        result = extract_iocs(r"Persistence: HKLM\Software\Microsoft\Windows\Run")
        assert any("HKLM" in k for k in result["registry_keys"])


class TestFlattenIOCs:
    def test_flatten(self):
        iocs = {
            "ips": ["1.1.1.1"],
            "domains": ["evil.com"],
            "md5": [],
            "sha1": [],
            "sha256": [],
            "urls": [],
            "emails": [],
            "cves": [],
            "windows_paths": [],
            "registry_keys": [],
        }
        flat = flatten_iocs(iocs)
        assert len(flat) == 2
        assert {"type": "ip", "value": "1.1.1.1"} in flat
        assert {"type": "domain", "value": "evil.com"} in flat

    def test_extract_flat(self):
        flat = extract_flat_iocs("IP 8.8.8.8 and domain evil.com")
        types = {item["type"] for item in flat}
        assert "ip" in types
        assert "domain" in types


class TestEmptyInput:
    def test_empty_string(self):
        result = extract_iocs("")
        assert all(len(v) == 0 for v in result.values())

    def test_none_input(self):
        result = extract_iocs(None)
        assert all(len(v) == 0 for v in result.values())

    def test_clean_text(self):
        result = extract_iocs("This is a normal sentence with no IOCs.")
        assert result["ips"] == []
        assert result["domains"] == []
