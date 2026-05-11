import json
import logging
import time
from pathlib import Path

from src.config import Config
from src.models import FormData, ExtractionResult
from src.sap_client import SAPClient


def extract_form_data(
    pdf_path: Path,
    quilombo: str,
    client: SAPClient,
    config: Config
) -> ExtractionResult:
    """
    Extract structured data from a single PDF form.

    Args:
        pdf_path: Path to PDF file
        quilombo: Quilombo name (from CLI or folder)
        client: SAP AI Hub client
        config: Application configuration

    Returns:
        ExtractionResult with success status, data, and metadata
    """
    logger = logging.getLogger(__name__)
    start_time = time.time()
    attempts = 0

    try:
        # Read PDF
        pdf_bytes = pdf_path.read_bytes()

        # Format system prompt with field schema
        fields_json = _format_fields_json(config.form_fields)
        system_prompt = config.system_prompt.format(fields_json=fields_json)

        # Call model with retry
        logger.info(f"Processing {pdf_path.name}...")
        raw_response = client.call_with_retry(
            system_prompt=system_prompt,
            user_message="Extraia os dados deste formulário conforme instruído.",
            pdf_bytes=pdf_bytes,
            pdf_name=pdf_path.stem
        )

        # Parse JSON response
        data_dict = _parse_json_response(raw_response)

        # Create FormData object
        form_data = FormData.from_extracted_data(
            data=data_dict,
            filename=pdf_path.name,
            quilombo=quilombo
        )

        duration = time.time() - start_time
        logger.info(f"✅ {pdf_path.name} extracted successfully in {duration:.2f}s")

        return ExtractionResult(
            filename=pdf_path.name,
            success=True,
            data=form_data,
            error=None,
            attempts=attempts + 1,
            duration_seconds=duration
        )

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ {pdf_path.name} failed: {e}")

        return ExtractionResult(
            filename=pdf_path.name,
            success=False,
            data=None,
            error=str(e),
            attempts=attempts + 1,
            duration_seconds=duration
        )


def _format_fields_json(fields: list[str]) -> str:
    """
    Format field list as JSON schema for prompt.

    Args:
        fields: List of field names

    Returns:
        JSON string with fields as empty-string values
    """
    schema = {field: "" for field in fields}
    return json.dumps(schema, indent=2, ensure_ascii=False)


def _parse_json_response(text: str) -> dict[str, str]:
    """
    Parse JSON from model response, handling markdown wrappers.

    Handles:
    - Plain JSON
    - ```json ... ``` blocks
    - ``` ... ``` blocks

    Args:
        text: Raw text response from model

    Returns:
        Parsed JSON dictionary

    Raises:
        json.JSONDecodeError: If response is not valid JSON
    """
    text = text.strip()

    if text.startswith("```"):
        # Remove markdown code fence
        parts = text.split("```")
        if len(parts) > 1:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]

    return json.loads(text.strip())
