from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from app.conversation import build_conversation_contents, parse_response
from app.file_search import (
    build_store_name,
    cleanup_store,
    create_file_search_store,
    ensure_client,
    query_file_search,
    upload_file_to_store,
)
from app.localization import get_text
from app.pdf_utils import cleanup_local_file, save_uploaded_file
from app.state import append_chat_message, init_session_state, reset_uploaded_pdf_state
from app.ui import SidebarEvent, render_chat_history, render_sidebar, render_sources_section

load_dotenv()

MODEL_OPTIONS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
]


def main() -> None:
    st.set_page_config(
        page_title=get_text("page_title"),
        page_icon=get_text("page_icon"),
        layout="wide",
    )

    init_session_state()

    sidebar_event = render_sidebar(MODEL_OPTIONS)
    lang = sidebar_event.language

    handle_upload_flow(sidebar_event, lang)
    if sidebar_event.clear_requested:
        handle_clear_flow(lang)
        return

    st.title(get_text("page_title", lang))
    st.subheader(get_text("main_title", lang))
    st.write(get_text("subtitle", lang))

    if not ensure_api_key(lang):
        return

    if not st.session_state.get("store_name"):
        st.info(get_text("upload_prompt", lang))

    render_chat_history(st.session_state["chat_history"], lang)
    handle_chat_flow(lang)

    st.markdown("---")
    st.caption(get_text("footer", lang))


def handle_upload_flow(sidebar_event: SidebarEvent, lang: str) -> None:
    uploaded_file = sidebar_event.uploaded_file
    if not sidebar_event.should_process_upload or not uploaded_file:
        if uploaded_file and not st.session_state.get("api_key"):
            st.info(get_text("api_key_required", lang))
        return

    api_key = st.session_state.get("api_key")
    if not api_key:
        st.info(get_text("api_key_required", lang))
        return

    existing_store = st.session_state.get("store_name")
    existing_client = st.session_state.get("client")
    if existing_store and existing_client:
        safe_cleanup_remote_store(existing_client, existing_store, lang, bubble_up=False)
    cleanup_local_file(st.session_state.get("uploaded_path"))

    with st.spinner(get_text("processing", lang)):
        try:
            saved_path = save_uploaded_file(uploaded_file)
        except RuntimeError as exc:
            st.error(get_text("error_save_file", lang).format(exc))
            return

        client = ensure_client(api_key, st.session_state.get("client"))
        st.session_state["client"] = client
        store_name = build_store_name()

        try:
            store = create_file_search_store(client, store_name)
        except Exception as exc:
            cleanup_local_file(saved_path)
            st.error(get_text("error_create_store", lang).format(exc))
            return

        try:
            upload_file_to_store(client, store.name, saved_path, uploaded_file.name)
        except Exception as exc:
            cleanup_local_file(saved_path)
            safe_cleanup_remote_store(client, store.name, lang, bubble_up=False)
            st.error(get_text("error_upload_store", lang).format(exc))
            return

        st.session_state["store_name"] = store.name
        st.session_state["uploaded_filename"] = uploaded_file.name
        st.session_state["uploaded_path"] = saved_path
        st.session_state["chat_history"] = []
        st.success(get_text("upload_success", lang).format(uploaded_file.name))


def handle_clear_flow(lang: str) -> None:
    client = st.session_state.get("client")
    store_name = st.session_state.get("store_name")
    if client and store_name:
        safe_cleanup_remote_store(client, store_name, lang)
    cleanup_local_file(st.session_state.get("uploaded_path"))
    reset_uploaded_pdf_state()
    st.rerun()


def handle_chat_flow(lang: str) -> None:
    prompt = st.chat_input(get_text("chat_input", lang))
    if not prompt:
        return

    if not st.session_state.get("store_name"):
        st.warning(get_text("upload_prompt", lang))
        return

    append_chat_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    conversation = build_conversation_contents(st.session_state["chat_history"])

    with st.chat_message("assistant"):
        with st.spinner(get_text("thinking", lang)):
            try:
                response = query_file_search(
                    st.session_state["client"],
                    conversation,
                    st.session_state["store_name"],
                    st.session_state["model"],
                )
            except Exception as exc:
                st.error(get_text("error_query", lang).format(exc))
                append_chat_message("assistant", get_text("error_response", lang))
                return

            answer, sources = parse_response(response)
            if not answer:
                answer = get_text("error_response", lang)
            st.markdown(answer)
            render_sources_section(sources, lang)

    append_chat_message("assistant", answer, sources)


def ensure_api_key(lang: str) -> bool:
    api_key = st.session_state.get("api_key")
    if not api_key:
        st.warning(get_text("api_key_required", lang))
        return False
    try:
        st.session_state["client"] = ensure_client(api_key, st.session_state.get("client"))
    except Exception:
        st.error(get_text("error_api_key", lang))
        return False
    return True


def safe_cleanup_remote_store(client, store_name: str, lang: str | None, bubble_up: bool = True) -> None:
    try:
        cleanup_store(client, store_name)
    except Exception as exc:
        if bubble_up:
            st.error(get_text("error_cleanup", lang or "en").format(exc))


if __name__ == "__main__":
    main()

