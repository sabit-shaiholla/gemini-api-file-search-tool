from __future__ import annotations

from typing import Any

import streamlit as st

SESSION_DEFAULTS: dict[str, Any] = {
    "language": "en",
    "chat_history": [],
    "store_name": None,
    "uploaded_filename": None,
    "uploaded_path": None,
    "client": None,
    "client_api_key": None,
    "model": "gemini-2.5-flash",
    "api_key": None,
}


def init_session_state() -> None:
    """Populate Streamlit's session state with predictable defaults."""
    for key, value in SESSION_DEFAULTS.items():
        if key in st.session_state:
            continue
        if isinstance(value, (list, dict, set)):
            st.session_state[key] = value.copy()  # avoid shared mutable defaults
        else:
            st.session_state[key] = value


def reset_uploaded_pdf_state() -> None:
    """Clear file-related session state keys after cleanup."""
    st.session_state["store_name"] = None
    st.session_state["uploaded_filename"] = None
    st.session_state["uploaded_path"] = None
    st.session_state["chat_history"] = []


def append_chat_message(role: str, content: str, sources: list[Any] | None = None) -> None:
    """Persist the latest chat turn so the UI can replay it."""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    record: dict[str, Any] = {"role": role, "content": content}
    if sources:
        record["sources"] = sources
    st.session_state["chat_history"].append(record)
