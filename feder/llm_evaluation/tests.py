import json
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from langchain_core.messages import AIMessage

from feder.letters.factories import IncomingLetterFactory
from feder.llm_evaluation.models import (
    AzureChatOpenAI,
    LlmLetterRequest,
    letter_categorization,
)

settings.OPENAI_API_TYPE = "azure"
settings.OPENAI_API_KEY = "YOUR_API_KEY"
settings.OPENAI_API_VERSION = "2023-07-01-preview"
settings.AZURE_ENDPOINT = "YOUR_ENDPOINT"
settings.OPENAI_API_ENGINE_35 = "gpt-35-turbo-16k"
settings.OPENAI_API_ENGINE_4 = "gpt-4"
settings.OPENAI_API_TEMPERATURE = 0


EXPECTED_RESPONSE_DICT = {
    "content": (
        "Why did the lion eat the tightrope walker?\n"
        + "Because he wanted a well-balanced meal!"
    ),
    "additional_kwargs": {},
    "response_metadata": {
        "token_usage": {
            "completion_tokens": "20",
            "prompt_tokens": "350",
            "total_tokens": "370",
        },
        "model_name": "gpt-35-turbo-16k",
        "system_fingerprint": None,
        "prompt_filter_results": [
            {
                "prompt_index": "0",
                "content_filter_results": {
                    "hate": {"filtered": False, "severity": "safe"},
                    "self_harm": {"filtered": False, "severity": "safe"},
                    "sexual": {"filtered": False, "severity": "safe"},
                    "violence": {"filtered": False, "severity": "safe"},
                },
            }
        ],
        "finish_reason": "stop",
        "logprobs": None,
        "content_filter_results": {
            "hate": {"filtered": False, "severity": "safe"},
            "self_harm": {"filtered": False, "severity": "safe"},
            "sexual": {"filtered": False, "severity": "safe"},
            "violence": {"filtered": False, "severity": "safe"},
        },
    },
    "type": "ai",
    "name": None,
    "id": "run-e98a1d1b-a086-4013-9f25-64997f03f703-0",
    "example": False,
    "tool_calls": [],
    "invalid_tool_calls": [],
}


class TestAzureChatOpenAI(TestCase):

    def test_azure_chat_openai_response_schema_format(self):
        model = AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_key="YOUR_API_KEY",
            openai_api_version="2023-05-15",
            azure_endpoint="YOUR_ENDPOINT",
            deployment_name="YOUR_DEPLOYMENT_NAME",
            temperature=0.5,
        )

        response_format = model.output_schema.schema()["definitions"]["AIMessage"][
            "properties"
        ]
        print(response_format)
        print(set(response_format.keys()))
        print(set(EXPECTED_RESPONSE_DICT.keys()))
        self.assertEqual(
            set(response_format.keys()),
            set(
                EXPECTED_RESPONSE_DICT.keys()
                + [
                    "usage_metadata",
                ]  # TODO: check schema changes
            ),
        )


class TestLlmLetterRequest(TestCase):

    @patch("feder.llm_evaluation.models.AzureChatOpenAI.invoke")
    def test_azure_chat_openai_response_format(self, mock_invoke):
        model = AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_key="YOUR_API_KEY",
            openai_api_version="2023-05-15",
            azure_endpoint="YOUR_ENDPOINT",
            deployment_name="YOUR_DEPLOYMENT_NAME",
            temperature=0.5,
        )
        chain = letter_categorization | model
        # Set the mock response to a valid Azure Chat OpenAI response
        mock_invoke.return_value = AIMessage(**EXPECTED_RESPONSE_DICT)

        # Call the invoke method and check the response format
        resp_object = chain.invoke(
            {
                "intro": "This is an intro",
                "institution": "Institution Name",
                "monitoring_response": "This is a monitoring response",
            }
        )
        resp = resp_object.__dict__
        # Assert that the response has the correct keys
        self.assertIn("content", resp)
        self.assertIn("additional_kwargs", resp)
        self.assertIn("response_metadata", resp)
        self.assertIn("type", resp)
        self.assertIn("name", resp)
        self.assertIn("id", resp)
        self.assertIn("example", resp)
        self.assertIn("tool_calls", resp)
        self.assertIn("invalid_tool_calls", resp)

        # Assert that the response_metadata has the correct keys
        self.assertIn("token_usage", resp["response_metadata"])
        self.assertIn("model_name", resp["response_metadata"])
        self.assertIn("system_fingerprint", resp["response_metadata"])
        self.assertIn("prompt_filter_results", resp["response_metadata"])
        self.assertIn("finish_reason", resp["response_metadata"])
        self.assertIn("logprobs", resp["response_metadata"])
        self.assertIn("content_filter_results", resp["response_metadata"])

    @patch("feder.llm_evaluation.models.AzureChatOpenAI.invoke")
    def test_categorize_letter(self, mock_azure_chat_openai_invoke):
        # Mock the AzureChatOpenAI instance and its invoke method returned value
        mock_azure_chat_openai_invoke.return_value = AIMessage(**EXPECTED_RESPONSE_DICT)

        # Create an IncomingLetter instance
        letter = IncomingLetterFactory()

        # Call the categorize_letter method
        LlmLetterRequest.categorize_letter(letter)

        # Fetch the LlmLetterRequest instance created by categorize_letter
        llm_request = LlmLetterRequest.objects.get(evaluated_letter=letter)

        # Assert that the response data matches the expected format
        self.assertEqual(EXPECTED_RESPONSE_DICT["content"], llm_request.response)

        # TODO: Add mock and test the callback

        # Assert that the LlmLetterRequest status was updated correctly
        self.assertEqual(llm_request.status, LlmLetterRequest.STATUS.done)
