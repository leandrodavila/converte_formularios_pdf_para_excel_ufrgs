from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml


@dataclass
class SAPConfig:
    model_name: str
    auth_method: str
    max_tokens: int
    temperature: float


@dataclass
class ExtractionConfig:
    retry_attempts: int
    retry_delay_seconds: float
    backoff_multiplier: float
    rate_limit_delay: float


@dataclass
class OutputConfig:
    directory: str
    excel_filename: str
    log_filename: str


@dataclass
class Config:
    sap: SAPConfig
    extraction: ExtractionConfig
    output: OutputConfig
    form_fields: list[str]
    field_headers: dict[str, str]
    column_widths: dict[str, int]
    system_prompt: str


def _validate_sap_config(data: dict[str, Any]) -> None:
    """Validate SAP configuration section types and values."""
    required_fields = {
        "model_name": str,
        "auth_method": str,
        "max_tokens": int,
        "temperature": (int, float)
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field 'sap.{field}'")

        value = data[field]
        if not isinstance(value, expected_type):
            type_name = expected_type.__name__ if isinstance(expected_type, type) else "number"
            raise ValueError(
                f"Invalid type for 'sap.{field}': expected {type_name}, got {type(value).__name__}"
            )

    # Semantic validation
    if data["max_tokens"] <= 0:
        raise ValueError("'sap.max_tokens' must be greater than 0")

    if not (0.0 <= data["temperature"] <= 1.0):
        raise ValueError("'sap.temperature' must be between 0.0 and 1.0")


def _validate_extraction_config(data: dict[str, Any]) -> None:
    """Validate extraction configuration section types and values."""
    required_fields = {
        "retry_attempts": int,
        "retry_delay_seconds": (int, float),
        "backoff_multiplier": (int, float),
        "rate_limit_delay": (int, float)
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field 'extraction.{field}'")

        value = data[field]
        if not isinstance(value, expected_type):
            type_name = expected_type.__name__ if isinstance(expected_type, type) else "number"
            raise ValueError(
                f"Invalid type for 'extraction.{field}': expected {type_name}, got {type(value).__name__}"
            )

    # Semantic validation
    if data["retry_attempts"] < 0:
        raise ValueError("'extraction.retry_attempts' must be >= 0")

    if data["retry_delay_seconds"] < 0:
        raise ValueError("'extraction.retry_delay_seconds' must be >= 0")

    if data["backoff_multiplier"] <= 0:
        raise ValueError("'extraction.backoff_multiplier' must be > 0")

    if data["rate_limit_delay"] < 0:
        raise ValueError("'extraction.rate_limit_delay' must be >= 0")


def _validate_output_config(data: dict[str, Any]) -> None:
    """Validate output configuration section types and values."""
    required_fields = {
        "directory": str,
        "excel_filename": str,
        "log_filename": str
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field 'output.{field}'")

        value = data[field]
        if not isinstance(value, expected_type):
            raise ValueError(
                f"Invalid type for 'output.{field}': expected {expected_type.__name__}, got {type(value).__name__}"
            )

    # Semantic validation
    if not data["directory"]:
        raise ValueError("'output.directory' cannot be empty")

    if not data["excel_filename"]:
        raise ValueError("'output.excel_filename' cannot be empty")

    if not data["log_filename"]:
        raise ValueError("'output.log_filename' cannot be empty")


def load_config(path: Path = Path("config.yaml")) -> Config:
    """
    Load and validate configuration from YAML file.

    Args:
        path: Path to YAML configuration file

    Returns:
        Config object with validated settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid or has wrong types
        yaml.YAMLError: If YAML syntax is invalid

    Note:
        The 'column_widths' field is optional and defaults to an empty dict if not provided.
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax in configuration file: {e}") from e

    if not data:
        raise ValueError("Configuration file is empty")

    # Validate required sections
    required_sections = ["sap", "extraction", "output", "form_fields", "field_headers", "system_prompt"]
    for section in required_sections:
        if section not in data:
            raise ValueError(f"Missing required configuration section: {section}")

    # Validate nested configuration sections
    try:
        _validate_sap_config(data["sap"])
        _validate_extraction_config(data["extraction"])
        _validate_output_config(data["output"])
    except ValueError as e:
        raise ValueError(f"Configuration validation error: {e}") from e

    # Validate form_fields
    if not isinstance(data["form_fields"], list):
        raise ValueError(
            f"Invalid type for 'form_fields': expected list, got {type(data['form_fields']).__name__}"
        )

    if not data["form_fields"]:
        raise ValueError("'form_fields' cannot be empty")

    for i, field in enumerate(data["form_fields"]):
        if not isinstance(field, str):
            raise ValueError(
                f"Invalid type for 'form_fields[{i}]': expected str, got {type(field).__name__}"
            )

    # Validate field_headers
    if not isinstance(data["field_headers"], dict):
        raise ValueError(
            f"Invalid type for 'field_headers': expected dict, got {type(data['field_headers']).__name__}"
        )

    if not data["field_headers"]:
        raise ValueError("'field_headers' cannot be empty")

    for key, value in data["field_headers"].items():
        if not isinstance(key, str):
            raise ValueError(
                f"Invalid type for 'field_headers' key: expected str, got {type(key).__name__}"
            )
        if not isinstance(value, str):
            raise ValueError(
                f"Invalid type for 'field_headers[{key}]': expected str, got {type(value).__name__}"
            )

    # Validate column_widths (optional)
    column_widths = data.get("column_widths", {})
    if not isinstance(column_widths, dict):
        raise ValueError(
            f"Invalid type for 'column_widths': expected dict, got {type(column_widths).__name__}"
        )

    for key, value in column_widths.items():
        if not isinstance(key, str):
            raise ValueError(
                f"Invalid type for 'column_widths' key: expected str, got {type(key).__name__}"
            )
        if not isinstance(value, int):
            raise ValueError(
                f"Invalid type for 'column_widths[{key}]': expected int, got {type(value).__name__}"
            )
        if value <= 0:
            raise ValueError(
                f"'column_widths[{key}]' must be greater than 0, got {value}"
            )

    # Validate system_prompt
    if not isinstance(data["system_prompt"], str):
        raise ValueError(
            f"Invalid type for 'system_prompt': expected str, got {type(data['system_prompt']).__name__}"
        )

    if not data["system_prompt"].strip():
        raise ValueError("'system_prompt' cannot be empty or whitespace-only")

    # Build nested dataclasses (no need for try/except since we validated above)
    sap_config = SAPConfig(**data["sap"])
    extraction_config = ExtractionConfig(**data["extraction"])
    output_config = OutputConfig(**data["output"])

    return Config(
        sap=sap_config,
        extraction=extraction_config,
        output=output_config,
        form_fields=data["form_fields"],
        field_headers=data["field_headers"],
        column_widths=column_widths,
        system_prompt=data["system_prompt"]
    )
