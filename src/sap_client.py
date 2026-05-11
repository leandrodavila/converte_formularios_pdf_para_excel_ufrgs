import base64
import logging
import time
from abc import ABC, abstractmethod

from src.config import SAPConfig, ExtractionConfig


class SAPClient(ABC):
    """Abstract base for SAP AI Hub clients"""

    def __init__(self, config: SAPConfig, extraction_config: ExtractionConfig):
        self.config = config
        self.extraction_config = extraction_config
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def call_model(
        self,
        system_prompt: str,
        user_message: str,
        pdf_bytes: bytes,
        pdf_name: str
    ) -> str:
        """
        Call the model and return raw text response.

        Args:
            system_prompt: System instructions
            user_message: User request
            pdf_bytes: PDF file as bytes
            pdf_name: PDF filename (for API)

        Returns:
            Raw text response from model
        """
        pass

    def call_with_retry(
        self,
        system_prompt: str,
        user_message: str,
        pdf_bytes: bytes,
        pdf_name: str
    ) -> str:
        """
        Wrapper with exponential backoff retry logic.

        Args:
            system_prompt: System instructions
            user_message: User request
            pdf_bytes: PDF file as bytes
            pdf_name: PDF filename

        Returns:
            Raw text response from model

        Raises:
            Exception: After max retries exhausted
        """
        attempts = 0
        delay = self.extraction_config.retry_delay_seconds

        while attempts < self.extraction_config.retry_attempts:
            try:
                return self.call_model(system_prompt, user_message, pdf_bytes, pdf_name)
            except Exception as e:
                attempts += 1
                if attempts >= self.extraction_config.retry_attempts:
                    self.logger.error(
                        f"Failed after {attempts} attempts: {e}"
                    )
                    raise

                self.logger.warning(
                    f"Attempt {attempts}/{self.extraction_config.retry_attempts} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
                delay *= self.extraction_config.backoff_multiplier

        raise Exception("Retry logic error - should not reach here")


class BedrockSAPClient(SAPClient):
    """Amazon Bedrock interface for SAP AI Hub"""

    def __init__(self, config: SAPConfig, extraction_config: ExtractionConfig):
        super().__init__(config, extraction_config)
        from gen_ai_hub.proxy.native.amazon.clients import Session
        session = Session()
        self.client = session.client(model_name=config.model_name)

    def call_model(
        self,
        system_prompt: str,
        user_message: str,
        pdf_bytes: bytes,
        pdf_name: str
    ) -> str:
        """Call Claude via Bedrock converse API with PDF document"""
        response = self.client.converse(
            messages=[{
                "role": "user",
                "content": [
                    {
                        "document": {
                            "format": "pdf",
                            "name": pdf_name,
                            "source": {"bytes": pdf_bytes}
                        }
                    },
                    {"text": user_message}
                ]
            }],
            system=[{"text": system_prompt}],
            inferenceConfig={
                "maxTokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
        )
        return response["output"]["message"]["content"][0]["text"].strip()


class OpenAISAPClient(SAPClient):
    """OpenAI-compatible interface for SAP AI Hub (Harmonized API)"""

    def __init__(self, config: SAPConfig, extraction_config: ExtractionConfig):
        super().__init__(config, extraction_config)
        from gen_ai_hub.proxy.native.openai.clients import OpenAI
        self.client = OpenAI()

    def call_model(
        self,
        system_prompt: str,
        user_message: str,
        pdf_bytes: bytes,
        pdf_name: str
    ) -> str:
        """Call Claude via OpenAI-compatible API with base64-encoded PDF"""
        pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

        response = self.client.chat.completions.create(
            model_name=self.config.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:application/pdf;base64,{pdf_b64}"
                            }
                        },
                        {"type": "text", "text": user_message}
                    ]
                }
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        return response.choices[0].message.content.strip()


def create_sap_client(
    sap_config: SAPConfig,
    extraction_config: ExtractionConfig
) -> SAPClient:
    """
    Factory function to create appropriate SAP client.
    Tries Bedrock first, falls back to OpenAI interface.

    Args:
        sap_config: SAP configuration
        extraction_config: Extraction configuration

    Returns:
        SAPClient instance (Bedrock or OpenAI)

    Raises:
        ImportError: If SAP SDK not installed
    """
    try:
        return BedrockSAPClient(sap_config, extraction_config)
    except ImportError:
        try:
            return OpenAISAPClient(sap_config, extraction_config)
        except ImportError:
            raise ImportError(
                "SAP AI SDK not found. Install with:\n"
                '  pip install "sap-ai-sdk-gen[amazon]"'
            )
