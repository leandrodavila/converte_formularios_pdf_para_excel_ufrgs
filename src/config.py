from dataclasses import dataclass
from pathlib import Path
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


def load_config(path: Path = Path("config.yaml")) -> Config:
    """
    Load and validate configuration from YAML file.

    Args:
        path: Path to YAML configuration file

    Returns:
        Config object with validated settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError("Configuration file is empty")

    # Validate required sections
    required_sections = ["sap", "extraction", "output", "form_fields", "field_headers", "system_prompt"]
    for section in required_sections:
        if section not in data:
            raise ValueError(f"Missing required configuration section: {section}")

    # Build nested dataclasses
    sap_config = SAPConfig(**data["sap"])
    extraction_config = ExtractionConfig(**data["extraction"])
    output_config = OutputConfig(**data["output"])

    return Config(
        sap=sap_config,
        extraction=extraction_config,
        output=output_config,
        form_fields=data["form_fields"],
        field_headers=data["field_headers"],
        column_widths=data.get("column_widths", {}),
        system_prompt=data["system_prompt"]
    )
