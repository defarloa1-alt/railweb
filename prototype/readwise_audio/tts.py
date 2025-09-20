"""TTS wrapper that supports DRY_RUN and an ElevenLabs POST.

This module is portable across platforms: temporary files are written
using the system temp directory and `pathlib.Path`.

The DRY_RUN flag is consulted at call time so callers can set
environment variables before invoking the function.
"""
from __future__ import annotations

import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _is_dry_run() -> bool:
    v = os.getenv("DRY_RUN", "0")
    return v.lower() in ("1", "true", "yes", "on")


def synthesize_elevenlabs(text: str, voice: str = "alloy") -> Dict[str, Optional[str]]:
    """Return a dict with keys: path (local file) and provider_response (raw text).

    In DRY_RUN the function writes a short mp3 placeholder into the system
    temp directory. For real calls we require the ELEVENLABS_API_KEY env var.
    """
    if _is_dry_run():
        tmp = Path(tempfile.gettempdir())
        out_path = tmp / f"elevenlabs_{hash(text) & 0xffff}.mp3"
        try:
            # create a tiny placeholder file (valid MP3 header not required for tests)
            out_path.write_bytes(b"ID3")
            logger.debug("Wrote DRY_RUN placeholder tts file: %s", out_path)
        except Exception:
            logger.exception("Failed to write placeholder TTS file to %s", out_path)
        return {"path": str(out_path), "provider_response": None}

    import requests

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is required for real TTS calls")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    body = {"text": text, "voice_settings": {"stability": 0.6, "similarity_boost": 0.7}}

    resp = requests.post(url, json=body, headers=headers)
    resp.raise_for_status()

    tmp = Path(tempfile.gettempdir())
    out_path = tmp / f"elevenlabs_{hash(text) & 0xffff}.mp3"
    out_path.write_bytes(resp.content)
    logger.debug("Wrote tts file from ElevenLabs: %s", out_path)
    return {"path": str(out_path), "provider_response": resp.text}
