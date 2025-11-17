from __future__ import annotations

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "page_title": "PDF Chat with Gemini",
        "page_icon": "📄",
        "main_title": "Chat with your PDF using Google Gemini",
        "subtitle": "Upload a PDF and start asking questions!",
        "language": "Language",
        "model": "Model",
        "api_key_label": "Enter your Gemini API Key",
        "api_key_help": "Get your API key from https://aistudio.google.com/app/apikey",
        "api_key_warning": "⚠️ Security Notice",
        "api_key_warning_text": "Your API key is stored only in your local session and is not sent to any server.",
        "api_key_required": "Please enter your API key to proceed.",
        "sidebar_header": "PDF Upload",
        "choose_file": "Choose a PDF file",
        "processing": "Processing file...",
        "upload_success": "✅ Uploaded successfully: {}",
        "current_pdf": "📄 Current PDF: {}",
        "clear_button": "🗑️ Clear PDF and start over",
        "about_header": "### About",
        "about_text": "This app allows you to chat with your PDF documents using Google Gemini models. Upload a PDF and ask questions about its content!",
        "upload_prompt": "Please upload a PDF to get started.",
        "chat_input": "Ask a question about your PDF...",
        "thinking": "🤔 Thinking...",
        "view_sources": "📚 View Sources",
        "error_response": "Sorry, I could not generate a response. Please try again.",
        "footer": "Built with Streamlit and Google Gemini",
        "error_api_key": "GEMINI_API_KEY environment variable not set. Please set it to use the app.",
        "error_pdf_extract": "Error extracting text from PDF: {}",
        "error_save_file": "Error saving file: {}",
        "error_create_store": "Error creating file search store: {}",
        "error_upload_store": "Error uploading file to search store: {}",
        "error_query": "Error querying file search: {}",
        "error_cleanup": "Error during cleanup: {}",
    }
}


def get_text(key: str, lang: str = "en") -> str:
    """Return translated copy for the given key, defaulting to English."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
