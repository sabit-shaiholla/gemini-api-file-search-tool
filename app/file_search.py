from __future__ import annotations

import random
import string
import time
from typing import Optional

from google import genai
from google.genai import types

STORE_NAME_PREFIX = "streams-pdf-chat"


class OperationTimeoutError(TimeoutError):
    """Raised when an Operations API call fails to complete in time."""


def generate_random_id(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def build_store_name(prefix: str = STORE_NAME_PREFIX) -> str:
    return f"{prefix}-{generate_random_id()}"


def ensure_client(
    api_key: str,
    existing_client: Optional[genai.Client] = None,
    existing_api_key: Optional[str] = None,
) -> genai.Client:
    if existing_client is not None and existing_api_key == api_key:
        return existing_client
    return genai.Client(api_key=api_key)


def wait_for_operation(client: genai.Client, operation: types.Operation, poll_interval: int = 2, timeout: int = 300) -> types.Operation:
    start = time.time()
    current = operation
    while not getattr(current, "done", False):
        if time.time() - start > timeout:
            raise OperationTimeoutError("Operation timed out")
        time.sleep(poll_interval)
        current = client.operations.get(current)
    error = getattr(current, "error", None)
    if error:
        message = getattr(error, "message", "Operation failed")
        raise RuntimeError(message)
    return current


def create_file_search_store(client: genai.Client, display_name: str) -> types.FileSearchStore:
    return client.file_search_stores.create(config={"display_name": display_name})


def upload_file_to_store(
    client: genai.Client,
    store_name: str,
    file_path: str,
    display_name: str,
) -> types.File:
    upload_operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=store_name,
        config={
            "display_name": display_name,
            "custom_metadata": [
                {"key": "source", "string_value": "streamlit_upload"},
                {"key": "timestamp", "numeric_value": int(time.time())},
            ],
        },
    )
    completed = wait_for_operation(client, upload_operation)
    return completed.response


def query_file_search(
    client: genai.Client,
    conversation: list[types.Content],
    store_name: str,
    model: str,
) -> types.GenerateContentResponse:
    return client.models.generate_content(
        model=model,
        contents=conversation,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name],
                    )
                )
            ]
        ),
    )


def cleanup_store(client: genai.Client, store_name: str) -> None:
    client.file_search_stores.delete(name=store_name, config={"force": True})
