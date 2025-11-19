from __future__ import annotations

import random
import string
import time
from typing import Optional

from google import genai
from google.genai import types

from app.core.config import Config
from app.core.exceptions import GeminiServiceError, OperationTimeoutError


class GeminiService:
    """Service for interacting with Google Gemini API."""

    @staticmethod
    def generate_random_id(length: int = 8) -> str:
        """Generate a random string ID."""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def build_store_name(prefix: str = Config.STORE_NAME_PREFIX) -> str:
        """Build a unique store name."""
        return f"{prefix}-{GeminiService.generate_random_id()}"

    @staticmethod
    def ensure_client(
        api_key: str,
        existing_client: Optional[genai.Client] = None,
        existing_api_key: Optional[str] = None,
    ) -> genai.Client:
        """Ensure a valid Gemini client exists."""
        if existing_client is not None and existing_api_key == api_key:
            return existing_client
        return genai.Client(api_key=api_key)

    @staticmethod
    def wait_for_operation(
        client: genai.Client, 
        operation: types.Operation, 
        poll_interval: int = Config.POLL_INTERVAL, 
        timeout: int = Config.UPLOAD_TIMEOUT
    ) -> types.Operation:
        """Wait for a long-running operation to complete."""
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
            raise GeminiServiceError(message)
        return current

    @staticmethod
    def create_file_search_store(client: genai.Client, display_name: str) -> types.FileSearchStore:
        """Create a new file search store."""
        try:
            return client.file_search_stores.create(config={"display_name": display_name})
        except Exception as e:
            raise GeminiServiceError(f"Failed to create store: {e}") from e

    @staticmethod
    def upload_file_to_store(
        client: genai.Client,
        store_name: str,
        file_path: str,
        display_name: str,
    ) -> types.File:
        """Upload a file to the search store."""
        try:
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
            completed = GeminiService.wait_for_operation(client, upload_operation)
            return completed.response
        except Exception as e:
            raise GeminiServiceError(f"Failed to upload file: {e}") from e

    @staticmethod
    def query_file_search(
        client: genai.Client,
        conversation: list[types.Content],
        store_name: str,
        model: str,
    ) -> types.GenerateContentResponse:
        """Query the file search store."""
        try:
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
        except Exception as e:
            raise GeminiServiceError(f"Failed to query model: {e}") from e

    @staticmethod
    def cleanup_store(client: genai.Client, store_name: str) -> None:
        """Delete the file search store."""
        try:
            client.file_search_stores.delete(name=store_name, config={"force": True})
        except Exception as e:
            raise GeminiServiceError(f"Failed to cleanup store: {e}") from e
