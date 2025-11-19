from __future__ import annotations

import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    PAGE_TITLE: Final[str] = "File Query System with Gemini"
    PAGE_ICON: Final[str] = "🤖"
    
    # Model Configuration
    # User requested gemini-3.0-pro, avoiding 1.5 series.
    MODEL_OPTIONS: Final[list[str]] = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
        "gemini-3-pro-preview",
    ]
    
    # Store Configuration
    STORE_NAME_PREFIX: Final[str] = "streams-pdf-chat"
    
    # Timeouts (in seconds)
    UPLOAD_TIMEOUT: Final[int] = 300
    POLL_INTERVAL: Final[int] = 2
    
    @staticmethod
    def get_api_key() -> str | None:
        """Retrieve API key from environment."""
        return os.getenv("GEMINI_API_KEY")
