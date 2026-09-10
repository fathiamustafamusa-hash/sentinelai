"""
Unit tests for MITRE ATT&CK mapper.
"""
from app.services.mitre_mapper import (
    map_to_mitre,
    get_technique_info,
    TECHNIQUE_CATALOG,
    SOURCE_HINTS,
)


class TestMapToMitre:
    def test_brute_force_keyword(self):
        result = map_to_mitre(title="SSH Brute Force Attack")
        assert "T1110" in result

    def test_failed_login_keyword(self):
        result = map_to_mitre(description="Multiple failed login attempts")
        assert "T1110" in result

    def test_ransomware_keyword(self):
        result = map_to_mitre(title="Ransomware Detected")
        assert "T1486" in result

    def test_phishing_keyword(self):
        result = map_to_mitre(description="Suspicious phishing email detected")
        assert "T1566" in result

    def test_powershell_keyword(self):
        result = map_to_mitre(description="Suspicious powershell command")
        assert "T1059" in result

    def test_exploit_keyword(self):
        result = map_to_mitre(description="CVE-2024-1234 exploit attempt")
        assert "T1190" in result

    def test_ddos_keyword(self):
        result = map_to_mitre(title="DDoS attack on web server")
        assert "T1498" in result

    def test_mimikatz_keyword(self):
        result = map_to_mitre(description="Mimikatz execution detected")
        assert "T1003" in result

    def test_no_match_returns_empty(self):
        result = map_to_mitre(title="Normal business activity")
        assert result == []

    def test_case_insensitive(self):
        result = map_to_mitre(title="BRUTE FORCE")
        assert "T1110" in result


class TestSourceHints:
    def test_wazuh_source(self):
        result = map_to_mitre(source="Wazuh")
        assert "T1078" in result
        assert "T1059" in result

    def test_suricata_source(self):
        result = map_to_mitre(source="Suricata")
        assert "T1071" in result

    def test_source_case_insensitive(self):
        result = map_to_mitre(source="WAZUH")
        assert "T1078" in result


class TestCombined:
    def test_multiple_techniques(self):
        result = map_to_mitre(
            title="SSH Brute Force",
            description="Followed by powershell execution and CVE-2024-1234",
            source="Wazuh",
        )
        assert "T1110" in result  # brute force
        assert "T1059" in result  # powershell
        assert "T1190" in result  # CVE
        assert "T1078" in result  # wazuh source hint

    def test_deduplicated_and_sorted(self):
        result = map_to_mitre(
            title="Brute force brute force brute force",
        )
        # Should appear only once
        assert result.count("T1110") == 1
        # Should be sorted
        assert result == sorted(result)

    def test_empty_inputs(self):
        result = map_to_mitre()
        assert result == []

    def test_raw_data_searched(self):
        result = map_to_mitre(raw_data='{"command": "mimikatz sekurlsa::logonpasswords"}')
        assert "T1003" in result


class TestGetTechniqueInfo:
    def test_known_technique(self):
        info = get_technique_info("T1110")
        assert info["id"] == "T1110"
        assert info["name"] == "Brute Force"
        assert len(info["keywords"]) > 0

    def test_unknown_technique(self):
        info = get_technique_info("T9999")
        assert info["id"] == "T9999"
        assert info["name"] == "Unknown"
        assert info["keywords"] == []

    def test_lowercase_input(self):
        info = get_technique_info("t1110")
        assert info["id"] == "T1110"
        assert info["name"] == "Brute Force"


class TestCatalogIntegrity:
    def test_all_techniques_have_name(self):
        for tech_id, meta in TECHNIQUE_CATALOG.items():
            assert "name" in meta
            assert "keywords" in meta
            assert isinstance(meta["keywords"], list)
            assert len(meta["keywords"]) > 0

    def test_all_technique_ids_start_with_T(self):
        for tech_id in TECHNIQUE_CATALOG:
            assert tech_id.startswith("T")

    def test_source_hints_reference_valid_techniques(self):
        for source, hints in SOURCE_HINTS.items():
            for hint in hints:
                assert hint in TECHNIQUE_CATALOG, f"{source} references unknown {hint}"
