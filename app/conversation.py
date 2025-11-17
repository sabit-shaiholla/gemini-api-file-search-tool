from __future__ import annotations

from typing import Any, Iterable, List, Sequence

from google.genai import types


def _as_iterable(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def parse_response(response: types.GenerateContentResponse | None) -> tuple[str, list[Any]]:
    if not response or not getattr(response, "candidates", None):
        return "", []

    candidate = response.candidates[0]
    content = getattr(candidate, "content", None)
    parts = _as_iterable(getattr(content, "parts", None)) if content else []

    answer_fragments: list[str] = []
    sources: list[Any] = []

    for part in parts:
        text_value = getattr(part, "text", None)
        if text_value:
            answer_fragments.append(text_value)
        file_data = getattr(part, "file_data", None)
        if file_data:
            label = getattr(file_data, "display_name", None) or getattr(file_data, "file_uri", None) or getattr(file_data, "file_id", None)
            if label and label not in sources:
                sources.append(label)

    _append_citations(candidate, sources)
    _append_grounding(candidate, sources)

    return "\n\n".join(answer_fragments).strip(), sources


def build_conversation_contents(history: Sequence[dict[str, Any]]) -> list[types.Content]:
    conversation: list[types.Content] = []
    for message in history:
        content = message.get("content")
        role = message.get("role")
        if not content or not role:
            continue
        api_role = "model" if role == "assistant" else "user"
        conversation.append(
            types.Content(role=api_role, parts=[types.Part(text=content)])
        )
    return conversation


def _append_citations(candidate: types.Candidate, sources: list[Any]) -> None:
    citation_meta = getattr(candidate, "citation_metadata", None)
    if not citation_meta:
        return
    citations = _as_iterable(getattr(citation_meta, "citations", None))
    for citation in citations:
        cited = getattr(citation, "uri", None) or getattr(citation, "title", None)
        if cited and cited not in sources:
            sources.append(cited)


def _append_grounding(candidate: types.Candidate, sources: list[Any]) -> None:
    grounding_meta = getattr(candidate, "grounding_metadata", None)
    if not grounding_meta:
        return
    chunks = _as_iterable(getattr(grounding_meta, "grounding_chunks", None))
    for chunk in chunks:
        payload = chunk.to_json_dict() if hasattr(chunk, "to_json_dict") else chunk
        if payload:
            sources.append(payload)
    supports = _as_iterable(getattr(grounding_meta, "grounding_supports", None))
    for support in supports:
        payload = support.to_json_dict() if hasattr(support, "to_json_dict") else support
        if payload:
            sources.append(payload)
