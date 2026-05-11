# UFRGS Questionários - PDF Form Extractor

Automated extraction of handwritten questionnaire data from PDF files using SAP AI Hub and Claude 4.5 Sonnet.

## Features

- Batch processing of PDF questionnaires with intelligent retry logic
- SAP AI Hub integration with Claude 4.5 Sonnet for OCR and data extraction
- Extracts 40 fields including demographics, biometrics, medical history, and clinical measurements
- Generates formatted Excel reports with automatic column sizing
- Comprehensive error handling with detailed logging
- Configuration-driven architecture for easy customization
- Type-safe data models using Pydantic
- Retry mechanism with exponential backoff for API resilience
- Rate limiting to prevent API throttling

## Prerequisites

- Python 3.10+
- SAP AI Hub account with access to Claude models
- Valid SAP AI Hub credentials (OAuth or API key)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ufrgs_questionarios
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Set up SAP AI Hub credentials

The tool supports two authentication methods:

**Option A: Environment Variable (Recommended)**
```bash
# Windows
set ANTHROPIC_API_KEY=your-sap-api-key

# Linux/Mac
export ANTHROPIC_API_KEY=your-sap-api-key
```

**Option B: Configuration File**
```yaml
sap:
  auth_method: "config"
  api_key: "your-sap-api-key"
```

### 2. Review and customize config.yaml

The default configuration is production-ready but can be customized:

```yaml
sap:
  model_name: "anthropic--claude-4.5-sonnet"
  auth_method: "env"
  max_tokens: 2000
  temperature: 0

extraction:
  retry_attempts: 3
  retry_delay_seconds: 2
  backoff_multiplier: 2
  rate_limit_delay: 1

output:
  directory: "output"
  excel_filename: "resultados_ancestralidades_sap.xlsx"
  log_filename: "extraction.log"
```

**Configuration sections:**
- `sap`: SAP AI Hub connection settings
- `extraction`: Retry logic and rate limiting
- `output`: Output directory and file naming
- `form_fields`: 40 form fields to extract (demographics, biometrics, medical)
- `field_headers`: Portuguese column headers for Excel
- `column_widths`: Custom column widths for readability
- `system_prompt`: Extraction prompt template

## Usage

### Basic Usage

Process all PDFs in a folder:
```bash
python -m src.main path/to/pdfs
```

### Advanced Options

**Specify quilombo name** (overrides folder name):
```bash
python -m src.main path/to/pdfs --quilombo "Quilombo_Morro_Alto"
```

**Use custom configuration file**:
```bash
python -m src.main path/to/pdfs --config custom_config.yaml
```

**Enable verbose logging**:
```bash
python -m src.main path/to/pdfs --verbose
```

**Combine options**:
```bash
python -m src.main data/quilombo_a --quilombo "Comunidade_A" --verbose
```

### Output

Each run creates a timestamped directory in `output/`:
```
output/
└── run_20260511_143022/
    ├── resultados_ancestralidades_sap.xlsx
    └── logs/
        └── 20260511_143022_extraction.log
```

**Excel Report Columns:**
- Quilombo (source community)
- Arquivo (PDF filename)
- 40 form fields (demographics, biometrics, medical history, clinical measurements)

**Log Files:**
- Console output: INFO level (or DEBUG with --verbose)
- File output: Always DEBUG level with full extraction details

## Architecture

### Project Structure
```
ufrgs_questionarios/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point and orchestration
│   ├── config.py            # YAML configuration loader with validation
│   ├── models.py            # Pydantic data models (FormData, ExtractionResult)
│   ├── sap_client.py        # SAP AI Hub client abstraction
│   ├── extractor.py         # PDF extraction logic with retry mechanism
│   └── excel_generator.py   # Excel report generation
├── tests/
│   ├── test_config.py       # Configuration loading tests
│   ├── test_models.py       # Data model validation tests
│   └── test_extractor.py    # Extraction logic tests
├── config.yaml              # Main configuration file
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies (pytest, coverage)
└── README.md               # This file
```

### Key Components

**1. Configuration System (config.py)**
- YAML-based configuration with Pydantic validation
- Environment variable support for sensitive credentials
- Type-safe settings with semantic validation
- Default config.yaml location with override support

**2. Data Models (models.py)**
- `FormData`: 40 validated form fields with Portuguese field names
- `ExtractionResult`: Extraction outcome with metadata (success, error, filename)
- Pydantic validation ensures data integrity throughout pipeline

**3. SAP Client (sap_client.py)**
- Abstraction layer over SAP AI Hub SDK
- Configurable authentication (environment or config file)
- Retry logic with exponential backoff
- Structured error handling

**4. Extractor (extractor.py)**
- PDF-to-image conversion and encoding
- Prompt construction from configuration
- Retry mechanism for transient failures
- JSON parsing with fallback strategies

**5. Excel Generator (excel_generator.py)**
- Formatted Excel reports with proper headers
- Auto-sized columns with custom widths for long fields
- Success/error tracking per file
- Portuguese column headers from configuration

**6. Main CLI (main.py)**
- Argument parsing with argparse
- Quilombo resolution (CLI arg > folder name)
- Batch processing with progress indicators
- Summary statistics and error reporting

## Field Definitions

The system extracts 40 fields organized into categories:

**Demographics (10 fields)**
- Participant code, collection date, full name
- Birth location, biological sex, gender, age, birth date
- Race/color, maternal/paternal information

**Medical History (10 fields)**
- Current medications, treatment changes, adverse reactions
- Blood pressure readings, glucose tests, cholesterol tests
- Personal diagnoses, family history

**Biometrics (9 fields)**
- Height, weight, BMI
- Body fat percentage, muscle mass percentage, visceral fat
- Waist, belly, hip circumferences

**Clinical Measurements (11 fields)**
- Heart rate, blood glucose, body temperature
- Systolic and diastolic blood pressure
- Fasting hours

See `config.yaml` for complete field list and Portuguese headers.

## Error Handling

### Retry Logic
- 3 retry attempts by default
- 2-second initial delay with 2x backoff multiplier
- Handles transient API errors, rate limits, network issues

### Error Types
- **Configuration errors**: Invalid YAML, missing credentials, validation failures
- **API errors**: Authentication failures, rate limits, model errors
- **Extraction errors**: Invalid JSON responses, missing required fields
- **File errors**: Missing PDFs, invalid file formats, permission issues

### Logging
- All errors logged to timestamped log files in `output/run_*/logs/`
- Console output shows real-time progress with success/failure indicators
- Failed extractions tracked in final summary report

## Troubleshooting

### Authentication Issues

**Problem**: `❌ Erro ao conectar ao SAP AI Hub: Authentication failed`

**Solution**:
```bash
# Verify environment variable is set
echo $ANTHROPIC_API_KEY  # Linux/Mac
echo %ANTHROPIC_API_KEY%  # Windows

# Verify API key format
# Should start with appropriate prefix for SAP AI Hub

# Try config-based auth instead
# Edit config.yaml:
sap:
  auth_method: "config"
  api_key: "your-key-here"
```

### JSON Parsing Errors

**Problem**: `❌ Extraction error: Invalid JSON response`

**Symptoms**: Claude returns markdown-wrapped JSON (```json ... ```)

**Auto-handled by**:
- `extractor.py` includes fallback parsing logic
- Strips markdown code fences automatically
- Falls back to raw content parsing

**If persistent**: Check `system_prompt` in config.yaml emphasizes "APENAS JSON válido, sem markdown"

### Rate Limiting

**Problem**: `⚠️ Rate limit hit, retrying...`

**Solution**:
- Default 1-second delay between requests prevents most rate limits
- Increase `rate_limit_delay` in config.yaml if needed:
```yaml
extraction:
  rate_limit_delay: 2  # Increase to 2 seconds
```

### Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'sap_ai_sdk_gen'`

**Solution**:
```bash
pip install -r requirements.txt

# Or manually
pip install "sap-ai-sdk-gen[amazon]>=1.0.0" openpyxl PyYAML
```

### Empty Extraction Results

**Problem**: All fields extracted as empty strings

**Possible causes**:
1. PDF image quality too low
2. Handwriting illegible
3. Model token limit too low

**Solutions**:
- Verify PDF opens correctly and is readable
- Increase `max_tokens` in config.yaml (default 2000):
```yaml
sap:
  max_tokens: 4000
```
- Check logs for truncated responses

### File Permission Errors

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Ensure output directory is writable
chmod -R u+w output/  # Linux/Mac

# Run as administrator if needed on Windows
# Or change output directory in config.yaml
```

## Testing

Run the test suite:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Test Coverage
- Configuration loading and validation
- Data model validation (required fields, types)
- Extraction retry logic
- Excel generation
- Error handling scenarios

## Development

### Code Quality
- Type hints throughout codebase
- Pydantic models for data validation
- Comprehensive error handling
- Detailed logging at DEBUG level

### Adding New Fields

1. Add field to `config.yaml`:
```yaml
form_fields:
  - new_field_name

field_headers:
  new_field_name: "Display Name"

column_widths:
  new_field_name: 25  # Optional custom width
```

2. Update `FormData` model in `src/models.py`:
```python
class FormData(BaseModel):
    # ... existing fields ...
    new_field_name: str
```

3. Run tests to verify:
```bash
pytest tests/test_config.py -v
pytest tests/test_models.py -v
```

### Custom System Prompt

Edit `system_prompt` in `config.yaml`:
```yaml
system_prompt: |
  Your custom extraction instructions here.
  
  Use {fields_json} placeholder for field list injection.
  
  Retorne APENAS JSON válido.
```

## License

Internal UFRGS research project. Not for redistribution.

## Support

For issues or questions:
1. Check logs in `output/run_*/logs/` for detailed error messages
2. Review Troubleshooting section above
3. Contact project maintainers

## Version History

- **v1.0.0** (2026-05-11): Initial modular release
  - Migrated from monolithic script to modular architecture
  - Added configuration system with validation
  - Implemented comprehensive error handling and retry logic
  - Added test suite with pytest
  - Created Excel report generation
  - Added detailed logging and progress indicators
