import json
import pytest
from pathlib import Path
from unittest.mock import Mock
from src.extractor import extract_form_data, _format_fields_json, _parse_json_response
from src.config import Config, SAPConfig, ExtractionConfig, OutputConfig


def test_format_fields_json():
    fields = ["codigo_participante", "data_coleta", "nome_completo"]
    result = _format_fields_json(fields)

    parsed = json.loads(result)
    assert parsed["codigo_participante"] == ""
    assert parsed["data_coleta"] == ""
    assert parsed["nome_completo"] == ""


def test_parse_json_response_plain():
    raw = '{"codigo_participante": "001", "data_coleta": "2026-05-08"}'
    result = _parse_json_response(raw)

    assert result["codigo_participante"] == "001"
    assert result["data_coleta"] == "2026-05-08"


def test_parse_json_response_with_markdown():
    raw = '```json\n{"codigo_participante": "001"}\n```'
    result = _parse_json_response(raw)

    assert result["codigo_participante"] == "001"


def test_parse_json_response_with_generic_fence():
    raw = '```\n{"codigo_participante": "002"}\n```'
    result = _parse_json_response(raw)

    assert result["codigo_participante"] == "002"


def test_extract_form_data_success(tmp_path):
    # Create a dummy PDF
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy content")

    # Mock client
    mock_client = Mock()
    mock_client.call_with_retry.return_value = '{"codigo_participante": "001", "data_coleta": "2026-05-08", "nome_completo": "Test"}'

    # Mock config
    config = Config(
        sap=SAPConfig("test-model", "env", 1000, 0),
        extraction=ExtractionConfig(3, 2, 2, 1),
        output=OutputConfig("output", "test.xlsx", "test.log"),
        form_fields=["codigo_participante", "data_coleta", "nome_completo"],
        field_headers={},
        column_widths={},
        system_prompt="Extract {fields_json}"
    )

    result = extract_form_data(pdf_path, "Test Quilombo", mock_client, config)

    assert result.success is True
    assert result.data is not None
    assert result.data.quilombo == "Test Quilombo"
    assert result.data.arquivo == "test.pdf"
    assert result.data.codigo_participante == "001"
    assert result.error is None


def test_extract_form_data_failure(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy")

    mock_client = Mock()
    mock_client.call_with_retry.side_effect = Exception("API Error")

    config = Config(
        sap=SAPConfig("test-model", "env", 1000, 0),
        extraction=ExtractionConfig(3, 2, 2, 1),
        output=OutputConfig("output", "test.xlsx", "test.log"),
        form_fields=["codigo_participante"],
        field_headers={},
        column_widths={},
        system_prompt="Extract {fields_json}"
    )

    result = extract_form_data(pdf_path, "Test", mock_client, config)

    assert result.success is False
    assert result.data is None
    assert "API Error" in result.error
