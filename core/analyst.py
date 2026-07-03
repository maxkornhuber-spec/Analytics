"""KI-Schicht: Aufrufe an die Claude API (Screenshot-Analyse, Chef-Analyst, Berichte)."""

import base64
import json
import re

import streamlit as st
import anthropic

from core import db, prompts

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4000


@st.cache_resource
def get_ai() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def _full_context() -> str:
    return prompts.build_context(
        dossiers=db.get_dossiers(),
        rules=db.get_rules(),
        lessons=db.get_lessons(),
        recent_drivers=db.get_recent_drivers(limit=25),
    )


def _image_block(uploaded_file) -> dict:
    data = uploaded_file.getvalue()
    media_type = uploaded_file.type or "image/png"
    if media_type not in ("image/png", "image/jpeg", "image/webp", "image/gif"):
        media_type = "image/png"
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64.b64encode(data).decode(),
        },
    }


def _parse_json(text: str) -> dict:
    """Robustes Parsen: entfernt Markdown-Zaeune, findet das JSON-Objekt."""
    cleaned = re.sub(r"```(json)?", "", text).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Keine JSON-Antwort erhalten.")
    return json.loads(cleaned[start:end + 1])


def analyze_screenshots(files: list, note: str) -> dict:
    """Analysiert Screenshots, schreibt Dossiers fort, erkennt Setups.

    Gibt das geparste Ergebnis zurueck und speichert alles in Supabase.
    """
    content = [ _image_block(f) for f in files ]
    user_text = prompts.SCREENSHOT_ANALYSIS_INSTRUCTIONS
    if note:
        user_text += f"\n\nNotiz des Traders zu diesen Screenshots: {note}"
    content.append({"type": "text", "text": user_text})

    system = prompts.ANALYST_IDENTITY + "\n\n" + _full_context()

    resp = get_ai().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text")
    result = _parse_json(raw)

    # Dossiers fortschreiben + Treiber speichern
    valid_codes = {d["code"] for d in db.get_dossiers()}
    touched = []
    for a in result.get("assets", []):
        code = a.get("code", "").upper()
        if code not in valid_codes:
            continue
        touched.append(code)
        db.update_dossier(code, {
            "direction": a.get("direction", "Neutral"),
            "confidence": int(a.get("confidence", 0)),
            "confidence_label": a.get("confidence_label", "unklar"),
            "thesis": a.get("thesis", ""),
            "rate_outlook": a.get("rate_outlook", "Unklar"),
            "last_change_note": a.get("kurswechsel_note") if a.get("kurswechsel") else None,
        })
        drv = a.get("driver") or {}
        if drv.get("title"):
            db.add_driver(
                asset_code=code,
                title=drv.get("title", ""),
                impact=drv.get("impact", "neutral"),
                summary=drv.get("summary", ""),
                source_hint=drv.get("source_hint"),
            )

    # Setups speichern
    for s in result.get("setups", []):
        if s.get("pair") and s.get("direction"):
            db.add_setup(
                pair=s["pair"], direction=s["direction"],
                quality=s.get("quality", "C"),
                rationale=s.get("rationale", ""),
                warning=s.get("warning"),
            )

    db.add_log(note or None, result.get("kommentar", ""), ", ".join(touched))
    return result


def generate_report(kind: str) -> str:
    """kind: 'taeglich' oder 'woechentlich'."""
    instructions = (
        prompts.DAILY_REPORT_INSTRUCTIONS if kind == "taeglich"
        else prompts.WEEKLY_REPORT_INSTRUCTIONS
    )
    system = prompts.ANALYST_IDENTITY + "\n\n" + _full_context()
    resp = get_ai().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": instructions}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    db.add_report(kind, text)
    return text
