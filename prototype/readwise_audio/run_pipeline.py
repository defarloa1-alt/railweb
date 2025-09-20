"""Small runner to exercise the prototype in DRY_RUN mode.

This script supports toggling audio generation via CLI flags so the
visual n8n depiction can keep an audio module that is opt-in.
"""
from __future__ import annotations

from fetcher import fetch_highlights, filter_highlights
from llm_prompt import build_prompt, call_llm
from tts import synthesize_elevenlabs
from stitcher import generate_ffmpeg_concat_cmd
import os
import json
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _set_env_if_provided(key: str, value: str | None) -> None:
    if value:
        os.environ[key] = value


def run(dry_run: bool = True, generate_audio: bool = False) -> None:
    _set_env_if_provided("DRY_RUN", "1" if dry_run else "0")

    try:
        highlights = fetch_highlights()
    except Exception:
        logger.exception("Failed to fetch highlights")
        highlights = []

    logger.info("Fetched %d highlights (raw)", len(highlights))

    # apply user filters before building the prompt
    if any((os.getenv("FILTER_TAGS"), os.getenv("FILTER_KEYWORDS"), os.getenv("MAX_HIGHLIGHTS"))):
        tags = os.getenv("FILTER_TAGS")
        kws = os.getenv("FILTER_KEYWORDS")
        maxh = os.getenv("MAX_HIGHLIGHTS")
        tags_list = [t.strip() for t in tags.split(",")] if tags else None
        kw_list = [k.strip() for k in kws.split(",")] if kws else None
        highlights = filter_highlights(highlights, tags_whitelist=tags_list, keywords=kw_list, max_items=maxh)
        logger.info("Filtered to %d highlights", len(highlights))

    prompt = build_prompt(highlights)
    logger.debug("Built prompt: %s", prompt)
    llm_out = call_llm(prompt)
    logger.info("LLM output keys: %s", list(llm_out.keys()))

    audio_generated = False
    audio_path: str | None = None

    if generate_audio:
        # split script into segments (naive by sentences)
        script = llm_out.get("script", "") or ""
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        segment_paths: list[str] = []
        for i, s in enumerate(sentences):
            try:
                seg = synthesize_elevenlabs(s)
            except Exception:
                logger.exception("TTS failed for segment %d", i)
                continue
            if seg.get("path"):
                logger.info("Wrote segment: %s", seg["path"])
                segment_paths.append(seg["path"])
        if segment_paths:
            out_path = Path.cwd() / "out_audio.mp3"
            cmd = generate_ffmpeg_concat_cmd(segment_paths, str(out_path))
            logger.info("Run to stitch segments: %s", " ".join(cmd))
            audio_generated = True
            audio_path = str(out_path)
    else:
        logger.info("Audio generation skipped (generate_audio=False)")

    # write provenance metadata next to output
    metadata = {
        "run_id": os.getenv("RUN_ID") or "local-dry-run",
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "llm": {"model": os.getenv("OPENAI_MODEL") or "gpt-4o"},
        "tts_provider": os.getenv("TTS_PROVIDER") or "elevenlabs",
        "audio_generated": audio_generated,
        "audio_path": audio_path,
        "highlights_provenance": [
            {"id": h.get("id"), "title": h.get("title"), "provenance": h.get("provenance")} for h in highlights
        ],
    }
    meta_path = Path.cwd() / "out_audio.metadata.json"
    try:
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        logger.info("Wrote metadata: %s", meta_path)
    except Exception:
        logger.exception("Failed to write metadata to %s", meta_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Readwise→Audio prototype")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false",
                        help="Disable dry-run mode (will call external APIs).")
    parser.add_argument("--audio", dest="generate_audio", action="store_true",
                        help="Enable audio generation (disabled by default).")
    parser.add_argument("--max-highlights", dest="max_highlights", type=int, default=None,
                        help="Limit number of highlights to process (DRY_RUN: helps demo).")
    parser.add_argument("--filter-tags", dest="filter_tags", type=str, default=None,
                        help="Comma-separated list of tags to include (e.g. 'safety,scale-converter')")
    parser.add_argument("--filter-keywords", dest="filter_keywords", type=str, default=None,
                        help="Comma-separated keywords to match in title/excerpt.")
    args = parser.parse_args()

    # Support passing filters via CLI or environment for convenience
    if args.filter_tags:
        os.environ["FILTER_TAGS"] = args.filter_tags
    if args.filter_keywords:
        os.environ["FILTER_KEYWORDS"] = args.filter_keywords
    if args.max_highlights:
        os.environ["MAX_HIGHLIGHTS"] = str(args.max_highlights)

    run(dry_run=args.dry_run, generate_audio=args.generate_audio)
