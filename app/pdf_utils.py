from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Optional

from streamlit.runtime.uploaded_file_manager import UploadedFile


def save_uploaded_file(uploaded_file: UploadedFile) -> str:
    """Persist the uploaded PDF to a temp file and return the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getvalue())
        return temp_file.name
    except Exception as exc:  # pragma: no cover - streamlit handles messaging
        raise RuntimeError(str(exc)) from exc


def cleanup_local_file(path: Optional[str]) -> None:
    """Remove stale temp files without surfacing errors to the UI."""
    if not path:
        return
    target = Path(path)
    if target.exists():
        try:
            target.unlink()
        except OSError:
            pass
