import os

from django.core.management.base import BaseCommand
from openai import AzureOpenAI

from feder.letters.models import Letter
from feder.llm_evaluation.models import LlmLetterRequest


class Command(BaseCommand):
    help = "Test Azure LLM chat availability."

    def add_arguments(self, parser):
        parser.add_argument(
            "--monitoring-pk", help="PK of monitoring to test", required=False
        )
        parser.add_argument("--letter-pk", help="PK of letter to test", required=False)

    def handle(self, *args, **options):
        print("Testing Azure LLM chat completion.")

        endpoint = os.getenv(
            "AZURE_ENDPOINT",
            "--",
        )
        deployment = os.getenv("OPENAI_API_ENGINE_4", "gpt-5-mini")
        subscription_key = os.getenv("OPENAI_API_KEY", "--")
        api_version = os.getenv("OPENAI_API_VERSION", "2025-01-01-preview")

        # Initialize Azure OpenAI client with key-based authentication
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=subscription_key,
            api_version=api_version,
        )

        # Prepare the chat prompt
        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an AI assistant that helps people find"
                        + " information.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": "Tell me best banana joke"}],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Sure! Here's a classic banana joke for you:\n\n"
                        + "Why did the banana go to the doctor?\n"
                        + "Because it wasn't peeling well!",
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": "explain it"}]},
        ]

        # Include speech result if speech is enabled
        messages = chat_prompt

        # Generate the completion
        completion = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=6553,
            stop=None,
            stream=False,
        )

        print(completion.to_json())

        print("Testing_letter evaluation.")
        letter = Letter.objects.get(pk=options["letter_pk"])
        LlmLetterRequest.categorize_letter(letter)
        print(f"Letter {letter.pk} evaluated with AI: {letter.ai_evaluation}")
