import pytest
from pathlib import Path
from src.config import Config, load_config, SAPConfig, ExtractionConfig, OutputConfig
import tempfile
import yaml


def test_load_valid_config():
    config_path = Path("tests/fixtures/sample_config.yaml")
    config = load_config(config_path)

    assert config.sap.model_name == "anthropic--claude-4.5-sonnet"
    assert config.sap.max_tokens == 2000
    assert config.extraction.retry_attempts == 3
    assert config.output.directory == "output"
    assert "codigo_participante" in config.form_fields
    assert config.field_headers["quilombo"] == "Quilombo"


def test_load_missing_config_raises_error():
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))


def test_config_dataclass_structure():
    sap_cfg = SAPConfig(
        model_name="test-model",
        auth_method="env",
        max_tokens=1000,
        temperature=0.0
    )
    assert sap_cfg.model_name == "test-model"


# YAML Parsing Error Tests
def test_invalid_yaml_syntax():
    """Test that invalid YAML syntax raises appropriate error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write("""
sap:
  model_name: "test"
  invalid: [unclosed list
""")
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid YAML syntax"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_empty_yaml_file():
    """Test that empty YAML file raises appropriate error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write("")
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Configuration file is empty"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


# Type Validation Tests
def test_sap_max_tokens_string_instead_of_int():
    """Test that string for max_tokens raises type error."""
    config_data = {
        "sap": {
            "model_name": "test",
            "auth_method": "env",
            "max_tokens": "2000",  # Should be int
            "temperature": 0.0
        },
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid type for 'sap.max_tokens'.*expected int"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_sap_temperature_string_instead_of_float():
    """Test that string for temperature raises type error."""
    config_data = {
        "sap": {
            "model_name": "test",
            "auth_method": "env",
            "max_tokens": 2000,
            "temperature": "0.5"  # Should be float/int
        },
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid type for 'sap.temperature'"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_extraction_retry_attempts_float_instead_of_int():
    """Test that float for retry_attempts raises type error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {
            "retry_attempts": 3.5,  # Should be int
            "retry_delay_seconds": 2.0,
            "backoff_multiplier": 2.0,
            "rate_limit_delay": 1.0
        },
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid type for 'extraction.retry_attempts'.*expected int"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_form_fields_string_instead_of_list():
    """Test that string for form_fields raises type error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": "not_a_list",  # Should be list
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid type for 'form_fields'.*expected list"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_field_headers_list_instead_of_dict():
    """Test that list for field_headers raises type error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": ["not", "a", "dict"],  # Should be dict
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid type for 'field_headers'.*expected dict"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_column_widths_wrong_value_type():
    """Test that non-int values in column_widths raise type error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "column_widths": {"field1": "20"},  # Should be int
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid type for 'column_widths\\[field1\\]'.*expected int"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


# Missing Field Tests
def test_missing_sap_section():
    """Test that missing sap section raises error."""
    config_data = {
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Missing required configuration section: sap"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_missing_nested_sap_field():
    """Test that missing nested field in sap section raises clear error."""
    config_data = {
        "sap": {
            "model_name": "test",
            "auth_method": "env",
            # Missing max_tokens
            "temperature": 0.0
        },
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Missing required field 'sap.max_tokens'"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_missing_nested_extraction_field():
    """Test that missing nested field in extraction section raises clear error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {
            "retry_attempts": 3,
            # Missing retry_delay_seconds
            "backoff_multiplier": 2.0,
            "rate_limit_delay": 1.0
        },
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Missing required field 'extraction.retry_delay_seconds'"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_missing_nested_output_field():
    """Test that missing nested field in output section raises clear error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {
            "directory": "out",
            # Missing excel_filename
            "log_filename": "test.log"
        },
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Missing required field 'output.excel_filename'"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


# Empty List/Dict Tests
def test_empty_form_fields():
    """Test that empty form_fields list raises error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": [],  # Empty list
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'form_fields' cannot be empty"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_empty_field_headers():
    """Test that empty field_headers dict raises error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {},  # Empty dict
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'field_headers' cannot be empty"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


# Semantic Validation Tests
def test_max_tokens_zero():
    """Test that max_tokens <= 0 raises semantic error."""
    config_data = {
        "sap": {
            "model_name": "test",
            "auth_method": "env",
            "max_tokens": 0,  # Invalid
            "temperature": 0.0
        },
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'sap.max_tokens' must be greater than 0"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_temperature_out_of_range():
    """Test that temperature outside [0, 1] raises semantic error."""
    config_data = {
        "sap": {
            "model_name": "test",
            "auth_method": "env",
            "max_tokens": 2000,
            "temperature": 1.5  # Invalid
        },
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'sap.temperature' must be between 0.0 and 1.0"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_retry_attempts_negative():
    """Test that negative retry_attempts raises semantic error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {
            "retry_attempts": -1,  # Invalid
            "retry_delay_seconds": 2.0,
            "backoff_multiplier": 2.0,
            "rate_limit_delay": 1.0
        },
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'extraction.retry_attempts' must be >= 0"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_backoff_multiplier_zero():
    """Test that backoff_multiplier <= 0 raises semantic error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {
            "retry_attempts": 3,
            "retry_delay_seconds": 2.0,
            "backoff_multiplier": 0,  # Invalid
            "rate_limit_delay": 1.0
        },
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'extraction.backoff_multiplier' must be > 0"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_column_width_negative():
    """Test that negative column width raises semantic error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "column_widths": {"field1": -10},  # Invalid
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'column_widths\\[field1\\]' must be greater than 0"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_empty_output_directory():
    """Test that empty output directory raises semantic error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {
            "directory": "",  # Invalid
            "excel_filename": "test.xlsx",
            "log_filename": "test.log"
        },
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'output.directory' cannot be empty"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_empty_system_prompt():
    """Test that empty or whitespace-only system_prompt raises semantic error."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        "system_prompt": "   "  # Whitespace only
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="'system_prompt' cannot be empty or whitespace-only"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_column_widths_optional():
    """Test that column_widths is optional and defaults to empty dict."""
    config_data = {
        "sap": {"model_name": "test", "auth_method": "env", "max_tokens": 2000, "temperature": 0.0},
        "extraction": {"retry_attempts": 3, "retry_delay_seconds": 2.0, "backoff_multiplier": 2.0, "rate_limit_delay": 1.0},
        "output": {"directory": "out", "excel_filename": "test.xlsx", "log_filename": "test.log"},
        "form_fields": ["field1"],
        "field_headers": {"field1": "Field 1"},
        # column_widths omitted
        "system_prompt": "test prompt"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        config = load_config(temp_path)
        assert config.column_widths == {}
    finally:
        temp_path.unlink()
