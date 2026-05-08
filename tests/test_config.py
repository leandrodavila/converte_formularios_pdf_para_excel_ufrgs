import pytest
from pathlib import Path
from src.config import Config, load_config, SAPConfig, ExtractionConfig, OutputConfig


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
