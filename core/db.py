"""Datenbank-Schicht: alle Zugriffe auf Supabase an einer Stelle."""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


# ---------- Dossiers ----------

def get_dossiers() -> list:
    res = get_client().table("dossiers").select("*").order("code").execute()
    return res.data or []


def update_dossier(code: str, fields: dict) -> None:
    fields["updated_at"] = "now()"
    get_client().table("dossiers").update(fields).eq("code", code).execute()


# ---------- Treiber ----------

def add_driver(asset_code: str, title: str, impact: str, summary: str, source_hint=None) -> None:
    get_client().table("drivers").insert({
        "asset_code": asset_code,
        "title": title,
        "impact": impact,
        "summary": summary,
        "source_hint": source_hint,
    }).execute()


def get_recent_drivers(limit: int = 30) -> list:
    res = (
        get_client().table("drivers").select("*")
        .order("created_at", desc=True).limit(limit).execute()
    )
    return res.data or []


def get_drivers_for(asset_code: str, limit: int = 15) -> list:
    res = (
        get_client().table("drivers").select("*").eq("asset_code", asset_code)
        .order("created_at", desc=True).limit(limit).execute()
    )
    return res.data or []


# ---------- Setups ----------

def add_setup(pair: str, direction: str, quality: str, rationale: str, warning=None) -> None:
    get_client().table("setups").insert({
        "pair": pair, "direction": direction, "quality": quality,
        "rationale": rationale, "warning": warning,
    }).execute()


def get_setups(limit: int = 50) -> list:
    res = (
        get_client().table("setups").select("*")
        .order("created_at", desc=True).limit(limit).execute()
    )
    return res.data or []


def set_setup_status(setup_id: str, status: str) -> None:
    get_client().table("setups").update({"status": status}).eq("id", setup_id).execute()


# ---------- Berichte ----------

def add_report(kind: str, content: str) -> None:
    get_client().table("reports").insert({"kind": kind, "content": content}).execute()


def get_reports(limit: int = 20) -> list:
    res = (
        get_client().table("reports").select("*")
        .order("created_at", desc=True).limit(limit).execute()
    )
    return res.data or []


# ---------- Regelbuch ----------

def get_rules(only_active: bool = True) -> list:
    q = get_client().table("rules").select("*").order("created_at")
    if only_active:
        q = q.eq("active", True)
    return q.execute().data or []


def add_rule(text: str) -> None:
    get_client().table("rules").insert({"text": text}).execute()


def set_rule_active(rule_id: str, active: bool) -> None:
    get_client().table("rules").update({"active": active}).eq("id", rule_id).execute()


# ---------- Lern-Speicher ----------

def get_lessons(only_active: bool = True) -> list:
    q = get_client().table("lessons").select("*").order("created_at")
    if only_active:
        q = q.eq("active", True)
    return q.execute().data or []


def add_lesson(lesson: str, context=None) -> None:
    get_client().table("lessons").insert({"lesson": lesson, "context": context}).execute()


def set_lesson_active(lesson_id: str, active: bool) -> None:
    get_client().table("lessons").update({"active": active}).eq("id", lesson_id).execute()


# ---------- Analyse-Log ----------

def add_log(note, result: str, assets: str) -> None:
    get_client().table("analysis_log").insert({
        "note": note, "result": result, "assets": assets,
    }).execute()


def get_logs(limit: int = 20) -> list:
    res = (
        get_client().table("analysis_log").select("*")
        .order("created_at", desc=True).limit(limit).execute()
    )
    return res.data or []
