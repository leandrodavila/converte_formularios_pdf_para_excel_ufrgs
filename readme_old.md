# UFRGS Questionários - Legacy Scripts

**IMPORTANT**: This file contains legacy single-file scripts that have been replaced by the modular architecture.

For the current production version, see **[README.md](README.md)**.

## Migration Notes

The original monolithic scripts (`extrair_pdfs_sap.py`, `main1.py`) have been refactored into a modular architecture with:
- Configuration system (YAML-based)
- Type-safe data models (Pydantic)
- Comprehensive error handling
- Test coverage
- Detailed logging

## Legacy Scripts

### extrair_pdfs_sap.py
Original SAP AI Hub implementation with hardcoded configuration.

**Replaced by**: `src/main.py` + `config.yaml`

### main1.py
Early prototype with Anthropic API.

**Replaced by**: Modular architecture in `src/` directory

## Using Legacy Scripts

If you need to run the legacy scripts (not recommended):

1. Install dependencies:
```bash
pip install anthropic openpyxl
# or
pip install "sap-ai-sdk-gen[amazon]" openpyxl
```

2. Configure API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

3. Execute:
```bash
python extrair_pdfs_sap.py ./pasta_com_pdfs
# or
python main1.py ./pasta_com_pdfs
```

## Migrating to Modular Version

See **[README.md](README.md)** for:
- Installation instructions
- Configuration options
- Usage examples
- Feature documentation
- Troubleshooting guide