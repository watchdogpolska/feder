import json
import logging
import time

import tiktoken
from django.conf import settings
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_llm_response(prompt, prompt_kwargs_dict):
    model = AzureChatOpenAI(
        openai_api_type=settings.OPENAI_API_TYPE,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_version=settings.OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_ENDPOINT,
        deployment_name=settings.OPENAI_API_ENGINE_35,
        temperature=settings.OPENAI_API_TEMPERATURE,
    )
    chain = prompt | model | StrOutputParser()
    start_time = time.time()
    with get_openai_callback() as cb:
        resp = chain.invoke(prompt_kwargs_dict)
    end_time = time.time()
    execution_time = end_time - start_time
    return resp, cb, execution_time


def serializable_dict(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def get_serializable_dict(obj):
    return {k: v for k, v in vars(obj).items() if serializable_dict(v)}
