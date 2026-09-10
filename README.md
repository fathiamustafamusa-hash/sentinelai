# SentinelAI - AI-Powered Enterprise SOC

An integrated Security Operations Center (SOC) platform powered by AI, combining leading Blue Team tools (Wazuh, Suricata, Zeek, MISP, TheHive, Cortex) with AI technologies (OpenAI, Ollama) for threat detection and incident response.

## Vision

Build a production-ready SOC platform, cloud-deployable, compliant with MITRE ATT&CK, Sigma, and YARA standards.

## Architecture

    SentinelAI/
    ├── src/backend/       # FastAPI + SQLAlchemy + Celery
    ├── src/frontend/      # React + TypeScript
    ├── src/ai/            # Detection + LLM + Threat Intel
    ├── src/ingestion/     # Collectors + Parsers
    ├── docker/            # SOC services configuration
    ├── docs/              # Professional documentation
    ├── tests/             # Unit and integration tests
    └── .github/workflows  # CI/CD

## Status

Under Development - Phase 0.

## License

MIT - see LICENSE file.
