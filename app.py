"""DEIN ANALYSTENTEAM - persoenliche Fundamental-Analyse-App.

Streamlit + Supabase + Claude API. Nur fuer den privaten Gebrauch,
geschuetzt durch einen Zugangscode (in den Streamlit-Secrets).
"""

import streamlit as st

st.set_page_config(page_title="Dein Analystenteam", page_icon="📊", layout="wide")

# ---------------------------------------------------------------
# Zugangscode: nur du kommst rein
# ---------------------------------------------------------------
def check_access() -> bool:
    if st.session_state.get("authed"):
        return True
    st.title("🔒 Dein Analystenteam")
    st.caption("Private App - Zugang nur mit Code.")
    code = st.text_input("Zugangscode", type="password")
    if st.button("Öffnen", type="primary"):
        if code == st.secrets.get("APP_CODE", ""):
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("Falscher Code.")
    return False


if not check_access():
    st.stop()

from core import db, analyst  # noqa: E402  (erst nach Login laden)

DIRECTION_ICON = {"Long": "🟢", "Short": "🔴", "Neutral": "⚪"}
QUALITY_BADGE = {"A": "🟢 A - stark", "B": "🟡 B - mit Lücken", "C": "🔴 C - Finger weg"}

st.markdown(
    """<style>
    .block-container {padding-top: 2rem;}
    div[data-testid="stMetric"] {background: rgba(128,128,128,.07);
        border-radius: 12px; padding: 10px 14px;}
    </style>""",
    unsafe_allow_html=True,
)

tab_dash, tab_feed, tab_setups, tab_reports, tab_brain = st.tabs(
    ["📊 Dashboard", "📥 Daten füttern", "🎯 Setups", "📄 Berichte", "🧠 Regelbuch & Lernen"]
)

# ---------------------------------------------------------------
# 1) DASHBOARD
# ---------------------------------------------------------------
with tab_dash:
    st.subheader("Alle Dossiers auf einen Blick")
    dossiers = db.get_dossiers()

    changed = [d for d in dossiers if d.get("last_change_note")]
    for d in changed:
        st.warning(f"⚠️ **Kurswechsel {d['code']}:** {d['last_change_note']}")

    cols = st.columns(3)
    for i, d in enumerate(dossiers):
        with cols[i % 3]:
            icon = DIRECTION_ICON.get(d["direction"], "⚪")
            st.metric(
                label=f"{icon} {d['code']} - {d['name']}",
                value=d["direction"],
                delta=f"Konfidenz {d['confidence']} ({d['confidence_label']})",
                delta_color="off",
            )
            with st.expander("Dossier öffnen"):
                st.markdown(f"**These:** {d['thesis']}")
                st.markdown(f"**Zins-These:** {d['rate_outlook']}")
                st.caption(f"Zuletzt aktualisiert: {d['updated_at'][:16].replace('T', ' ')}")
                st.markdown("**Letzte Treiber:**")
                for dr in db.get_drivers_for(d["code"], limit=6):
                    src = f" _(Quelle: {dr['source_hint']})_" if dr.get("source_hint") else ""
                    st.markdown(f"- **{dr['title']}** → {dr['impact']}: {dr['summary']}{src}")

# ---------------------------------------------------------------
# 2) DATEN FUETTERN
# ---------------------------------------------------------------
with tab_feed:
    st.subheader("Screenshots reinschießen")
    st.caption(
        "Tipp: Ein Thema pro Ladung (z.B. nur NFP-Daten), Quelle & Datum sichtbar lassen. "
        "Die KI erkennt selbst, welche Währungen betroffen sind, und schreibt die Dossiers fort."
    )
    files = st.file_uploader(
        "Screenshots (News, Kalender, Notenbank-Statements, Charts)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
    note = st.text_area("Notiz dazu (optional)", placeholder="z.B. 'Heutige NFP-Daten, deutlich unter Erwartung'")

    if st.button("🔍 Analysieren & Dossiers fortschreiben", type="primary", disabled=not files):
        with st.spinner("Dein Analystenteam arbeitet..."):
            try:
                result = analyst.analyze_screenshots(files, note.strip())
            except Exception as e:
                st.error(f"Analyse fehlgeschlagen: {e}")
                result = None
        if result:
            st.success("Dossiers aktualisiert.")
            st.markdown(f"**Einordnung:** {result.get('kommentar', '')}")
            for a in result.get("assets", []):
                icon = DIRECTION_ICON.get(a.get("direction"), "⚪")
                st.markdown(
                    f"{icon} **{a.get('code')}** → {a.get('direction')} "
                    f"(Konfidenz {a.get('confidence')}, {a.get('confidence_label')}) - {a.get('thesis')}"
                )
                if a.get("kurswechsel"):
                    st.warning(f"⚠️ Kurswechsel bei {a.get('code')}: {a.get('kurswechsel_note')}")
            setups = result.get("setups", [])
            if setups:
                st.markdown("**Erkannte Setups:**")
                for s in setups:
                    st.markdown(f"- **{s['pair']} {s['direction']}** | {QUALITY_BADGE.get(s.get('quality'), s.get('quality'))} - {s.get('rationale')}")
                    if s.get("warning"):
                        st.error(f"🛑 {s['warning']}")
            else:
                st.info("Kein Setup aus diesen Daten - und das ist eine ehrliche Antwort, kein Fehler.")

    with st.expander("Letzte Fütterungen (Log)"):
        for log in db.get_logs():
            st.markdown(
                f"**{log['created_at'][:16].replace('T', ' ')}** | {log.get('assets') or '-'}"
                + (f" | Notiz: {log['note']}" if log.get("note") else "")
            )
            st.caption(log["result"])

# ---------------------------------------------------------------
# 3) SETUPS
# ---------------------------------------------------------------
with tab_setups:
    st.subheader("Setup-Radar")
    setups = db.get_setups()
    if not setups:
        st.info("Noch keine Setups. Fütter das Team mit Daten - Setups entstehen, wenn zwei Thesen stark gegenläufig sind.")
    for s in setups:
        box = st.container(border=True)
        with box:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### {s['pair']} · {s['direction']} · {QUALITY_BADGE.get(s['quality'], s['quality'])}")
                st.markdown(s["rationale"])
                if s.get("warning"):
                    st.error(f"🛑 Bullshit-Filter: {s['warning']}")
                st.caption(f"Erkannt: {s['created_at'][:16].replace('T', ' ')} · Status: {s['status']}")
            with c2:
                if s["status"] == "offen":
                    if st.button("✅ Getradet", key=f"t{s['id']}"):
                        db.set_setup_status(s["id"], "getradet"); st.rerun()
                    if st.button("🗑 Verwerfen", key=f"v{s['id']}"):
                        db.set_setup_status(s["id"], "verworfen"); st.rerun()

# ---------------------------------------------------------------
# 4) BERICHTE
# ---------------------------------------------------------------
with tab_reports:
    st.subheader("Tages- & Wochenanalyse")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️ Tagesbriefing erstellen", type="primary"):
            with st.spinner("Chef-Analyst schreibt das Briefing..."):
                try:
                    st.session_state["last_report"] = analyst.generate_report("taeglich")
                except Exception as e:
                    st.error(f"Fehlgeschlagen: {e}")
    with c2:
        if st.button("📅 Wochenanalyse erstellen"):
            with st.spinner("Chef-Analyst schreibt die Wochenanalyse..."):
                try:
                    st.session_state["last_report"] = analyst.generate_report("woechentlich")
                except Exception as e:
                    st.error(f"Fehlgeschlagen: {e}")

    if st.session_state.get("last_report"):
        st.markdown("---")
        st.markdown(st.session_state["last_report"])

    with st.expander("Frühere Berichte"):
        for r in db.get_reports():
            st.markdown(f"**{'☀️ Tagesbriefing' if r['kind'] == 'taeglich' else '📅 Wochenanalyse'}** · {r['created_at'][:16].replace('T', ' ')}")
            st.markdown(r["content"])
            st.markdown("---")

# ---------------------------------------------------------------
# 5) REGELBUCH & LERNEN
# ---------------------------------------------------------------
with tab_brain:
    col_rules, col_lessons = st.columns(2)

    with col_rules:
        st.subheader("📖 Dein Regelbuch")
        st.caption("Diese Regeln liest die KI bei JEDER Analyse mit.")
        new_rule = st.text_input("Neue Regel", placeholder="z.B. Zwei gegenläufige Treiber = Day-Trade-Kandidat")
        if st.button("Regel speichern", disabled=not new_rule.strip()):
            db.add_rule(new_rule.strip()); st.rerun()
        for r in db.get_rules(only_active=False):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(("✅ " if r["active"] else "⏸ ~~") + r["text"] + ("" if r["active"] else "~~"))
            with c2:
                label = "Aus" if r["active"] else "An"
                if st.button(label, key=f"r{r['id']}"):
                    db.set_rule_active(r["id"], not r["active"]); st.rerun()

    with col_lessons:
        st.subheader("🧠 Lern-Speicher")
        st.caption(
            "Hier korrigierst du dein Team: 'Das war falsch, weil...'. "
            "Jede Lektion wird DAUERHAFT gespeichert und bei jeder Analyse mitgelesen."
        )
        lesson = st.text_area("Neue Lektion / Korrektur", placeholder="z.B. 'Einzelne Fed-Redner nicht überbewerten - nur Powell und offizielle Statements zählen stark.'")
        lesson_ctx = st.text_input("Bezug (optional)", placeholder="z.B. 'USD-Analyse vom 02.07.'")
        if st.button("Lektion dauerhaft speichern", type="primary", disabled=not lesson.strip()):
            db.add_lesson(lesson.strip(), lesson_ctx.strip() or None); st.rerun()
        for l in db.get_lessons(only_active=False):
            c1, c2 = st.columns([5, 1])
            with c1:
                ctx = f" _(Bezug: {l['context']})_" if l.get("context") else ""
                st.markdown(("✅ " if l["active"] else "⏸ ~~") + l["lesson"] + ("" if l["active"] else "~~") + ctx)
            with c2:
                label = "Aus" if l["active"] else "An"
                if st.button(label, key=f"l{l['id']}"):
                    db.set_lesson_active(l["id"], not l["active"]); st.rerun()

st.markdown("---")
st.caption(
    "⚠️ Diese App liefert strukturierte Analysen als Entscheidungsgrundlage. "
    "Sie ist keine Finanzberatung und gibt keine Gewinn-Garantien - die Trade-Entscheidung liegt bei dir."
)
