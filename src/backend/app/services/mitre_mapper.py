"""
MITRE ATT&CK mapper.

Maps alert characteristics (source, title, description) to MITRE ATT&CK
techniques. Uses a keyword-based approach for simplicity and auditability.

Reference: https://attack.mitre.org/techniques/enterprise/
"""

# ============ Technique catalog ============
# Each entry: technique_id -> {name, keywords}
TECHNIQUE_CATALOG: dict[str, dict] = {
    "T1110": {
        "name": "Brute Force",
        "keywords": [
            "brute force",
            "bruteforce",
            "failed login",
            "failed password",
            "authentication failure",
            "invalid user",
            "repeated login",
            "password spray",
            "credential stuffing",
        ],
    },
    "T1078": {
        "name": "Valid Accounts",
        "keywords": [
            "valid account",
            "compromised account",
            "suspicious login",
            "anomalous login",
            "impossible travel",
            "unusual sign-in",
        ],
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "keywords": [
            "powershell",
            "cmd.exe",
            "bash script",
            "python script",
            "wscript",
            "cscript",
            "command execution",
            "shell script",
        ],
    },
    "T1055": {
        "name": "Process Injection",
        "keywords": [
            "process injection",
            "dll injection",
            "code injection",
            "shellcode injection",
            "reflective loading",
        ],
    },
    "T1053": {
        "name": "Scheduled Task/Job",
        "keywords": [
            "scheduled task",
            "cron job",
            "at job",
            "schtasks",
            "task scheduler",
            "systemd timer",
        ],
    },
    "T1547": {
        "name": "Boot or Logon Autostart Execution",
        "keywords": [
            "registry run key",
            "startup folder",
            "autostart",
            "persistence",
            "boot execute",
        ],
    },
    "T1486": {
        "name": "Data Encrypted for Impact",
        "keywords": [
            "ransomware",
            "encrypted files",
            "file encryption",
            "ransom note",
            "crypto locker",
            "locked files",
        ],
    },
    "T1041": {
        "name": "Exfiltration Over C2 Channel",
        "keywords": [
            "data exfiltration",
            "exfil",
            "data leak",
            "outbound transfer",
            "exfiltration over c2",
            "large upload",
        ],
    },
    "T1071": {
        "name": "Application Layer Protocol",
        "keywords": [
            "c2",
            "c&c",
            "command and control",
            "beacon",
            "cobalt strike",
            "metasploit",
            "reverse shell",
        ],
    },
    "T1566": {
        "name": "Phishing",
        "keywords": [
            "phishing",
            "spearphishing",
            "malicious attachment",
            "malicious link",
            "suspicious email",
            "spoofed email",
        ],
    },
    "T1190": {
        "name": "Exploit Public-Facing Application",
        "keywords": [
            "exploit",
            "cve-",
            "sql injection",
            "sqli",
            "rce",
            "remote code execution",
            "path traversal",
            "lfi",
            "rfi",
        ],
    },
    "T1046": {
        "name": "Network Service Scanning",
        "keywords": [
            "port scan",
            "network scan",
            "nmap",
            "service scan",
            "port scanning",
            "reconnaissance",
        ],
    },
    "T1498": {
        "name": "Network Denial of Service",
        "keywords": [
            "ddos",
            "dos attack",
            "denial of service",
            "flood",
            "syn flood",
            "udp flood",
            "amplification",
        ],
    },
    "T1021": {
        "name": "Remote Services",
        "keywords": [
            "rdp",
            "ssh login",
            "smb login",
            "winrm",
            "remote desktop",
            "vnc",
            "remote service",
        ],
    },
    "T1003": {
        "name": "OS Credential Dumping",
        "keywords": [
            "mimikatz",
            "lsass dump",
            "credential dump",
            "sam dump",
            "ntds.dit",
            "secretsdump",
            "hash dump",
        ],
    },
    "T1105": {
        "name": "Ingress Tool Transfer",
        "keywords": [
            "file download",
            "ingress transfer",
            "wget",
            "curl download",
            "download from internet",
            "tool transfer",
        ],
    },
}


# ============ Source-based hints ============
SOURCE_HINTS: dict[str, list[str]] = {
    "wazuh": ["T1078", "T1059", "T1110"],
    "suricata": ["T1071", "T1046", "T1498"],
    "zeek": ["T1071", "T1046"],
    "sigma": [],
    "yara": ["T1055", "T1105"],
    "misp": [],
}


def _normalize(text: str) -> str:
    """Lowercase + collapse whitespace for matching."""
    return " ".join(text.lower().split())


def map_to_mitre(
    title: str = "",
    description: str = "",
    source: str = "",
    raw_data: str = "",
) -> list[str]:
    """
    Map alert characteristics to MITRE ATT&CK technique IDs.

    Returns a sorted, deduplicated list of technique IDs (e.g., ["T1110", "T1078"]).

    The mapping is keyword-based. If an alert contains any keyword from a
    technique, that technique is considered "matched". Additionally,
    source-specific hints are added (e.g., Wazuh alerts hint at T1078).
    """
    techniques: set[str] = set()

    # Combine all text fields for keyword matching
    combined = _normalize(" ".join([title or "", description or "", raw_data or ""]))

    # Keyword-based matching
    for tech_id, meta in TECHNIQUE_CATALOG.items():
        for keyword in meta["keywords"]:
            if keyword in combined:
                techniques.add(tech_id)
                break  # one match is enough

    # Source hints
    if source:
        source_key = source.strip().lower()
        for hint_source, hints in SOURCE_HINTS.items():
            if hint_source in source_key:
                techniques.update(hints)
                break

    return sorted(techniques)


def get_technique_info(technique_id: str) -> dict:
    """
    Get metadata for a technique ID.

    Returns:
        {"id": "T1110", "name": "Brute Force", "keywords": [...]} or
        {"id": tech_id, "name": "Unknown", "keywords": []}
    """
    meta = TECHNIQUE_CATALOG.get(technique_id.upper())
    if meta:
        return {
            "id": technique_id.upper(),
            "name": meta["name"],
            "keywords": meta["keywords"],
        }
    return {"id": technique_id.upper(), "name": "Unknown", "keywords": []}
