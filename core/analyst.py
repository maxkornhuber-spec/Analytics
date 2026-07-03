"""KI-Schicht (v2): Screenshots, PDFs und Text analysieren; Berichte erstellen."""

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
        recent_drivers=db.get_recent_drivers(limit=30),
        active_bank_recs=db.get_bank_recs(status="aktiv", limit=100),
    )


def _file_block(uploaded_file) -> dict:
    data = uploaded_file.getvalue()
    b64 = base64.b64encode(data).decode()
    media_type = uploaded_file.type or ""
    if media_type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
        return {"type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": b64}}
    if media_type not in ("image/png", "image/jpeg", "image/webp", "image/gif"):
        media_type = "image/png"
    return {"type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64}}


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r"```(json)?", "", text).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Keine JSON-Antwort erhalten.")
    return json.loads(cleaned[start:end + 1])


def analyze_input(files: list, pasted_text: str, note: str) -> dict:
    """Analysiert beliebige Kombination aus Dateien (Bilder/PDF) und eingefuegtem Text.
    Schreibt Dossiers fort, erfasst Bankberichte separat, erkennt Setups & Duplikate."""
    content = [_file_block(f) for f in (files or [])]

    user_text = prompts.INPUT_ANALYSIS_INSTRUCTIONS
    if pasted_text:
        user_text += f"\n\n=== EINGEFUEGTER TEXT DES TRADERS ===\n{pasted_text.strip()}"
    if note:
        user_text += f"\n\nNotiz des Traders: {note}"
    content.append({"type": "text", "text": user_text})

    system = prompts.identity() + "\n\n" + _full_context()

    resp = get_ai().messages.create(
        model=MODEL, max_tokens=MAX_TOKENS, system=system,
        messages=[{"role": "user", "content": content}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text")
    result = _parse_json(raw)

    valid_codes = {d["code"] for d in db.get_dossiers()}
    touched = []

    # 1) Dossiers fortschreiben (nur Nicht-Bank-Infos)
    for a in result.get("assets", []):
        code = (a.get("code") or "").upper()
        if code not in valid_codes:
            continue
        touched.append(code)
        db.update_dossier(code, {
            "direction": a.get("direction", "Neutral"),
            "confidence": int(a.get("confidence", 0)),
            "confidence_label": a.get("confidence_label", "unklar"),
            "thesis": a.get("thesis", ""),
            "rate_outlook": a.get("rate_outlook", "Unklar"),
            "policy_rate": a.get("policy_rate", "unbekannt"),
            "spot_note": a.get("spot_note"),
            "last_change_note": a.get("kurswechsel_note") if a.get("kurswechsel") else None,
        })
        drv = a.get("driver") or {}
        if drv.get("title"):
            db.add_driver(code, drv.get("title", ""), drv.get("impact", "neutral"),
                          drv.get("summary", ""), drv.get("source_hint"))

    # 2) Bankbericht separat erfassen (loest alte Empfehlungen automatisch ab)
    br = result.get("bank_report")
    if br and br.get("bank_name"):
        for rec in br.get("recommendations", []):
            code = (rec.get("asset_code") or "").upper()
            if code in valid_codes and rec.get("stance"):
                db.add_bank_rec(br["bank_name"].strip(), code, rec["stance"],
                                rec.get("thesis", ""), br.get("report_date"))
        touched.append(f"Bank:{br['bank_name']}")

    # 3) Setups speichern
    for s in result.get("setups", []):
        if s.get("pair") and s.get("direction"):
            db.add_setup(s["pair"], s["direction"], s.get("quality", "C"),
                         s.get("rationale", ""), s.get("warning"))

    db.add_log(note or None, result.get("kommentar", ""), ", ".join(touched))
    return result


def generate_report(kind: str) -> str:
    """kind: 'taeglich' oder 'woechentlich'."""
    db.mark_stale_bank_recs(days=30)
    instructions = (prompts.DAILY_REPORT_INSTRUCTIONS if kind == "taeglich"
                    else prompts.WEEKLY_REPORT_INSTRUCTIONS)
    system = prompts.identity() + "\n\n" + _full_context()
    resp = get_ai().messages.create(
        model=MODEL, max_tokens=MAX_TOKENS, system=system,
        messages=[{"role": "user", "content": instructions}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    db.add_report(kind, text)
    return text


def run_audit() -> str:
    """Gegencheck: prueft alle gespeicherten Daten kritisch auf Konsistenz, Duplikate,
    Veraltetes, Einseitigkeit und saubere Bank-Zuordnung."""
    system = prompts.identity() + "\n\n" + _full_context()
    resp = get_ai().messages.create(
        model=MODEL, max_tokens=MAX_TOKENS, system=system,
        messages=[{"role": "user", "content": prompts.AUDIT_INSTRUCTIONS}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    db.add_report("pruefung", text)
    return text
