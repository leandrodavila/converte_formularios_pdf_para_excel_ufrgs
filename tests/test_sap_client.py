import pytest
from unittest.mock import Mock, patch
from src.sap_client import SAPClient, create_sap_client
from src.config import SAPConfig, ExtractionConfig


def test_create_sap_client_bedrock():
    sap_cfg = SAPConfig(
        model_name="anthropic--claude-4.5-sonnet",
        auth_method="env",
        max_tokens=2000,
        temperature=0
    )
    extraction_cfg = ExtractionConfig(
        retry_attempts=3,
        retry_delay_seconds=2,
        backoff_multiplier=2,
        rate_limit_delay=1
    )

    with patch("src.sap_client.BedrockSAPClient") as mock_bedrock:
        mock_instance = Mock()
        mock_bedrock.return_value = mock_instance

        client = create_sap_client(sap_cfg, extraction_cfg)

        assert client is mock_instance
        mock_bedrock.assert_called_once()


def test_retry_logic_on_failure():
    sap_cfg = SAPConfig(
        model_name="test-model",
        auth_method="env",
        max_tokens=1000,
        temperature=0
    )
    extraction_cfg = ExtractionConfig(
        retry_attempts=3,
        retry_delay_seconds=0.1,  # Fast for testing
        backoff_multiplier=2,
        rate_limit_delay=0
    )

    # Create a concrete test client
    class TestSAPClient(SAPClient):
        def call_model(self, system_prompt, user_message, pdf_bytes, pdf_name):
            # This will be mocked
            pass

    client = TestSAPClient(sap_cfg, extraction_cfg)

    # Mock the call_model method to fail twice then succeed
    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("API Error")
        return "success response"

    client.call_model = Mock(side_effect=side_effect)

    # Test parameters
    test_system_prompt = "test system"
    test_user_message = "test message"
    test_pdf_bytes = b"test pdf"
    test_pdf_name = "test.pdf"

    # Call with retry and verify it succeeds after 3 attempts
    result = client.call_with_retry(
        test_system_prompt,
        test_user_message,
        test_pdf_bytes,
        test_pdf_name
    )

    # Verify the result is correct
    assert result == "success response"

    # Verify call_model was called 3 times (2 failures + 1 success)
    assert client.call_model.call_count == 3

    # Verify all calls had the correct parameters
    client.call_model.assert_called_with(
        test_system_prompt,
        test_user_message,
        test_pdf_bytes,
        test_pdf_name
    )


def test_retry_exhaustion_raises():
    """Test that call_with_retry raises after exhausting all retries"""
    sap_cfg = SAPConfig(
        model_name="test-model",
        auth_method="env",
        max_tokens=1000,
        temperature=0
    )
    extraction_cfg = ExtractionConfig(
        retry_attempts=3,
        retry_delay_seconds=0.1,  # Fast for testing
        backoff_multiplier=2,
        rate_limit_delay=0
    )

    # Create a concrete test client
    class TestSAPClient(SAPClient):
        def call_model(self, system_prompt, user_message, pdf_bytes, pdf_name):
            pass

    client = TestSAPClient(sap_cfg, extraction_cfg)

    # Mock the call_model method to always fail
    client.call_model = Mock(side_effect=Exception("API Error"))

    # Test parameters
    test_system_prompt = "test system"
    test_user_message = "test message"
    test_pdf_bytes = b"test pdf"
    test_pdf_name = "test.pdf"

    # Call with retry and verify it raises after exhausting retries
    with pytest.raises(Exception, match="API Error"):
        client.call_with_retry(
            test_system_prompt,
            test_user_message,
            test_pdf_bytes,
            test_pdf_name
        )

    # Verify call_model was called exactly retry_attempts times
    assert client.call_model.call_count == 3


def test_create_sap_client_openai_fallback():
    """Test that create_sap_client falls back to OpenAI when Bedrock fails"""
    sap_cfg = SAPConfig(
        model_name="test-model",
        auth_method="env",
        max_tokens=1000,
        temperature=0
    )
    extraction_cfg = ExtractionConfig(
        retry_attempts=3,
        retry_delay_seconds=2,
        backoff_multiplier=2,
        rate_limit_delay=1
    )

    # Mock BedrockSAPClient to raise ImportError
    # Mock OpenAISAPClient to return successfully
    with patch("src.sap_client.BedrockSAPClient") as mock_bedrock, \
         patch("src.sap_client.OpenAISAPClient") as mock_openai:

        mock_bedrock.side_effect = ImportError("Bedrock not available")
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance

        client = create_sap_client(sap_cfg, extraction_cfg)

        # Verify OpenAI client was created
        assert client is mock_openai_instance
        mock_bedrock.assert_called_once()
        mock_openai.assert_called_once()

