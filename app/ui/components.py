from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from app.core.config import Config
from app.utils.localization import TRANSLATIONS, get_text


@dataclass(slots=True)
class SidebarEvent:
    language: str
    uploaded_file: Optional[UploadedFile]
    should_process_upload: bool
    clear_requested: bool


def render_sidebar(model_options: list[str]) -> SidebarEvent:
    with st.sidebar:
        st.subheader(get_text("api_key_warning"))
        st.caption(get_text("api_key_warning_text"))

        languages = list(TRANSLATIONS.keys())
        default_language = st.session_state.get("language", languages[0])
        try:
            language_index = languages.index(default_language)
        except ValueError:
            language_index = 0

        language = st.selectbox(get_text("language"), languages, index=language_index)
        st.session_state["language"] = language

        default_model = st.session_state.get("model", model_options[0])
        try:
            default_index = model_options.index(default_model)
        except ValueError:
            default_index = 0

        model = st.selectbox(get_text("model", language), options=model_options, index=default_index)
        st.session_state["model"] = model

        secrets_api_key = ""
        try:
            secrets_api_key = st.secrets.get("GEMINI_API_KEY", "")  # type: ignore[attr-defined]
        except Exception:
            secrets_api_key = ""

        default_api_key = (
            st.session_state.get("api_key")
            or secrets_api_key
            or os.getenv("GEMINI_API_KEY", "")
        )

        api_key_input = st.text_input(
            get_text("api_key_label", language),
            value=default_api_key,
            type="password",
            help=get_text("api_key_help", language),
        )
        if api_key_input:
            st.session_state["api_key"] = api_key_input

        st.markdown("---")
        st.header(get_text("sidebar_header", language))

        uploaded_file = st.file_uploader(get_text("choose_file", language), type=["pdf"])

        should_process_upload = bool(
            uploaded_file
            and st.session_state.get("api_key")
            and (
                st.session_state.get("store_name") is None
                or uploaded_file.name != st.session_state.get("uploaded_filename")
            )
        )

        clear_requested = False
        if st.session_state.get("store_name"):
            st.info(get_text("current_pdf", language).format(st.session_state.get("uploaded_filename")))
            clear_requested = st.button(get_text("clear_button", language), key="clear_pdf_button")

        st.markdown(get_text("about_header", language))
        st.caption(get_text("about_text", language))

    return SidebarEvent(
        language=language,
        uploaded_file=uploaded_file,
        should_process_upload=should_process_upload,
        clear_requested=clear_requested,
    )


def render_chat_history(history: list[dict], lang: str) -> None:
    if not history:
        return
    for message in history:
        role = message.get("role")
        if not role:
            continue
        with st.chat_message(role):
            st.markdown(message.get("content", ""))
            if role == "assistant":
                render_sources_section(message.get("sources"), lang)


def render_sources_section(sources: Optional[list], lang: str) -> None:
    if not sources:
        return
    with st.expander(get_text("view_sources", lang)):
        for source in sources:
            if isinstance(source, (dict, list)):
                st.json(source)
            else:
                st.markdown(f"- {source}")
