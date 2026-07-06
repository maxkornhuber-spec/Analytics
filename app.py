"""DEIN ANALYSTENTEAM v2 - persoenliche Fundamental-Analyse-App.

Streamlit + Supabase + Claude API. Privat, geschuetzt durch Zugangscode.
Neu in v2: Banken-Reiter, Text- & PDF-Eingang, Zinsbild, Duplikat-Schutz.
"""

from collections import defaultdict

import streamlit as st

st.set_page_config(page_title="Dein Analystenteam", page_icon="📊", layout="wide")


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

from core import db, analyst  # noqa: E402

DIRECTION_ICON = {"Long": "🟢", "Short": "🔴", "Neutral": "🟡"}
QUALITY_BADGE = {"A": "🟢 A - stark", "B": "🟡 B - mit Lücken", "C": "🔴 C - Finger weg"}

st.markdown(
    """<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.6rem; max-width: 1250px; }

    /* App-Titelzeile */
    .team-header {
        background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
        color: #fff; border-radius: 18px; padding: 18px 26px; margin-bottom: 14px;
    }
    .team-header h1 { margin: 0; font-size: 1.5rem; font-weight: 800; letter-spacing: .3px; }
    .team-header p { margin: 4px 0 0; opacity: .75; font-size: .9rem; }

    /* Tabs als Pills */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px; padding: 8px 16px;
        background: rgba(128,128,128,.08); border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, #2c5364, #203a43) !important;
        color: #fff !important; border-color: transparent;
    }

    /* Kennzahlen-Karten */
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,.06);
        border: 1px solid rgba(128,128,128,.15);
        border-radius: 16px; padding: 14px 16px;
        box-shadow: 0 1px 6px rgba(0,0,0,.06);
    }

    /* Buttons runder */
    .stButton > button { border-radius: 12px; font-weight: 600; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(120deg, #2c5364, #203a43); border: none;
    }

    /* Container & Expander runder */
    div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
    }
    div[data-testid="stFileUploaderDropzone"] {
        border-radius: 16px; border: 2px dashed rgba(128,128,128,.35);
    }
    .stTextArea textarea, .stTextInput input { border-radius: 12px; }
    </style>""",
    unsafe_allow_html=True,
)

st.markdown(
    '''<div class="team-header">
        <h1>📊 Dein Analystenteam</h1>
        <p>Fundamental-Dossiers · Banken-Radar · Setups · Recaps — privat & lernend</p>
    </div>''',
    unsafe_allow_html=True,
)

tab_dash, tab_feed, tab_banks, tab_setups, tab_recap, tab_reports, tab_brain = st.tabs(
    ["📊 Dashboard", "📥 Daten füttern", "🏦 Banken", "🎯 Setups", "📰 Recap & Kalender", "📄 Berichte", "🧠 Regelbuch & Lernen"]
)

# ---------------------------------------------------------------
# 1) DASHBOARD
# ---------------------------------------------------------------
with tab_dash:
    st.subheader("Alle Dossiers auf einen Blick")
    dossiers = db.get_dossiers()

    for d in [x for x in dossiers if x.get("last_change_note")]:
        st.warning(f"⚠️ **Kurswechsel {d['code']}:** {d['last_change_note']}")


    with st.expander("🌐 Zins-Spreads (10J) — Fair-Value-Anker"):
        import re as _re

        def _y(txt):
            if not txt:
                return None
            m = _re.search(r"-?\d+[.,]?\d*", str(txt))
            return float(m.group().replace(",", ".")) if m else None

        yields = {d["code"]: _y(d.get("yield_10y")) for d in dossiers}
        usd = yields.get("USD")
        rows = []
        for code in ["EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]:
            if usd is not None and yields.get(code) is not None:
                spread = yields[code] - usd
                rows.append(f"**{code}/USD**: {spread:+.2f} %-Punkte (10J {code} {yields[code]:.2f}% vs. USD {usd:.2f}%)")
        if rows:
            st.markdown("  \n".join(rows))
            st.caption("Merke: Läuft der Spread dem Kurs voraus, ist das ein Divergenz-Signal.")
        else:
            st.caption("Fütter die 10J-Renditen der Währungen (Text oder Screenshot), dann rechnet die App hier die Spreads automatisch.")

    cols = st.columns(3)
    for i, d in enumerate(dossiers):
        with cols[i % 3]:
            icon = DIRECTION_ICON.get(d["direction"], "🟡")
            ns = d.get("narrative_score", 0) or 0
            arrow = " ↗" if ns > 0 else " ↘" if ns < 0 else ""
            tend = f" · Tendenz {ns:+d}{arrow}" if ns != 0 else ""
            st.metric(
                label=f"{icon} {d['code']} - {d['name']}",
                value=d["direction"] + arrow,
                delta=f"Konfidenz {d['confidence']} ({d['confidence_label']}){tend}",
                delta_color="off",
            )
            with st.expander("Dossier öffnen"):
                st.markdown(f"**These:** {d['thesis']}")
                st.markdown(f"**Zins-These:** {d['rate_outlook']}")
                st.markdown(f"**Leitzins:** {d.get('policy_rate', 'unbekannt')}")
                ns = d.get("narrative_score", 0)
                st.markdown(f"**Narrativ-Score:** {'🟢' if ns > 0 else '🔴' if ns < 0 else '⚪'} {ns:+d} (−3 bis +3)")
                if d.get("priced_in"):
                    st.markdown(f"**Eingepreist:** {d['priced_in']}")
                if d.get("yield_10y"):
                    st.markdown(f"**10J-Rendite:** {d['yield_10y']}")
                if d.get("spot_note"):
                    st.markdown(f"**Marktstand:** {d['spot_note']}")
                st.caption(f"Zuletzt aktualisiert: {d['updated_at'][:16].replace('T', ' ')}")
                st.markdown("**Letzte Treiber:**")
                for dr in db.get_drivers_for(d["code"], limit=6):
                    src = f" _(Quelle: {dr['source_hint']})_" if dr.get("source_hint") else ""
                    st.markdown(f"- **{dr['title']}** → {dr['impact']}: {dr['summary']}{src}")

# ---------------------------------------------------------------
# 2) DATEN FUETTERN (v2: Dropzone + separates Textfeld)
# ---------------------------------------------------------------
with tab_feed:
    st.subheader("Daten reinschießen")
    st.caption("Ein Thema pro Ladung. Quelle & Datum sichtbar/mitkopieren - die KI prüft Aktualität und Duplikate selbst.")

    st.markdown("**📎 Screenshots & PDFs** — einfach in die Fläche ziehen:")
    files = st.file_uploader(
        "Dateien hierher ziehen oder klicken",
        type=["png", "jpg", "jpeg", "webp", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.markdown("**📝 Text einfügen** — kopierte News, Berichte, Kalender-Daten:")
    pasted = st.text_area(
        "Text hier einfügen",
        height=180,
        placeholder="Hier kopierten Text einfügen (News-Artikel, Notenbank-Statement, Bankbericht ...) - am besten inkl. Quelle und Datum.",
        label_visibility="collapsed",
    )

    note = st.text_input("Notiz dazu (optional)", placeholder="z.B. 'NFP-Daten von gestern, deutlich unter Erwartung'")

    has_input = bool(files) or bool(pasted.strip())
    if st.button("🔍 Analysieren & Dossiers fortschreiben", type="primary", disabled=not has_input):
        with st.spinner("Dein Analystenteam arbeitet..."):
            try:
                result = analyst.analyze_input(files or [], pasted, note.strip())
            except Exception as e:
                st.error(f"Analyse fehlgeschlagen: {e}")
                result = None
        if result:
            st.success("Analyse abgeschlossen.")
            st.markdown(f"**Einordnung:** {result.get('kommentar', '')}")

            for dup in result.get("duplikate", []) or []:
                st.info(f"♻️ Duplikat erkannt - nicht erneut gespeichert: {dup}")

            for a in result.get("assets", []):
                icon = DIRECTION_ICON.get(a.get("direction"), "⚪")
                st.markdown(
                    f"{icon} **{a.get('code')}** → {a.get('direction')} "
                    f"(Konfidenz {a.get('confidence')}, {a.get('confidence_label')}) - {a.get('thesis')}"
                )
                if a.get("kurswechsel"):
                    st.warning(f"⚠️ Kurswechsel bei {a.get('code')}: {a.get('kurswechsel_note')}")

            br = result.get("bank_report")
            if br and br.get("bank_name"):
                st.markdown(f"🏦 **Bankbericht erkannt: {br['bank_name']}**" +
                            (f" (Bericht vom {br['report_date']})" if br.get("report_date") else ""))
                for rec in br.get("recommendations", []):
                    st.markdown(f"- [{rec.get('asset_code')}] {rec.get('stance')}: {rec.get('thesis')}")
                st.caption("Bank-Empfehlungen werden separat im Banken-Reiter geführt und verändern deine Dossiers nicht.")

            setups = result.get("setups", [])
            if setups:
                st.markdown("**Erkannte Setups:**")
                for s in setups:
                    st.markdown(f"- **{s['pair']} {s['direction']}** | {QUALITY_BADGE.get(s.get('quality'), s.get('quality'))} - {s.get('rationale')}")
                    if s.get("warning"):
                        st.error(f"🛑 {s['warning']}")
            else:
                st.info("Kein Setup aus diesen Daten - ehrliche Antwort, kein Fehler.")

    with st.expander("Letzte Fütterungen (Log)"):
        for log in db.get_logs():
            st.markdown(
                f"**{log['created_at'][:16].replace('T', ' ')}** | {log.get('assets') or '-'}"
                + (f" | Notiz: {log['note']}" if log.get("note") else "")
            )
            st.caption(log["result"])

# ---------------------------------------------------------------
# 3) BANKEN (v2)
# ---------------------------------------------------------------
with tab_banks:
    st.subheader("🏦 Bank-Empfehlungen")
    db.mark_stale_bank_recs(days=30)
    active = db.get_bank_recs(status="aktiv")

    if not active:
        st.info("Noch keine Bank-Empfehlungen. Fütter einfach einen Bankbericht (Screenshot, PDF oder Text) - die Bank wird automatisch erkannt und hier angelegt.")
    else:
        # Konsens je Asset
        st.markdown("**Konsens je Asset:**")
        by_asset = defaultdict(lambda: {"Long": 0, "Short": 0, "Neutral": 0})
        for r in active:
            by_asset[r["asset_code"]][r.get("stance", "Neutral")] += 1
        cons_lines = []
        for asset, c in sorted(by_asset.items()):
            cons_lines.append(f"**{asset}**: {c['Long']} Long / {c['Short']} Short / {c['Neutral']} Neutral")
        st.markdown("  \n".join(cons_lines))

        st.markdown("---")
        # Karten pro Bank
        by_bank = defaultdict(list)
        for r in active:
            by_bank[r["bank_name"]].append(r)
        for bank, recs in sorted(by_bank.items()):
            box = st.container(border=True)
            with box:
                st.markdown(f"### {bank}")
                for r in sorted(recs, key=lambda x: x["asset_code"]):
                    icon = DIRECTION_ICON.get(r["stance"], "⚪")
                    date_txt = f" · Bericht: {r['report_date']}" if r.get("report_date") else ""
                    st.markdown(f"{icon} **{r['asset_code']} {r['stance']}** - {r['thesis']}{date_txt}")
                    if r.get("change_note"):
                        st.caption(f"🔄 Meinungswechsel: {r['change_note']}")

    with st.expander("Abgelöste & veraltete Empfehlungen (Historie)"):
        history = [r for r in db.get_bank_recs() if r["status"] != "aktiv"]
        if not history:
            st.caption("Noch keine Historie.")
        for r in history:
            tag = "🔄 abgelöst" if r["status"] == "abgeloest" else "⏳ veraltet"
            st.markdown(f"{tag} · **{r['bank_name']}** [{r['asset_code']}] {r['stance']} - {r['thesis']} "
                        f"_({r['created_at'][:10]})_")

# ---------------------------------------------------------------
# 4) SETUPS
# ---------------------------------------------------------------
with tab_setups:
    st.subheader("Setup-Radar")
    setups = db.get_setups()
    if not setups:
        st.info("Noch keine Setups. Setups entstehen, wenn zwei Thesen stark gegenläufig sind.")
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
# RECAP & KALENDER (v3)
# ---------------------------------------------------------------
with tab_recap:
    from datetime import date, timedelta

    st.subheader("📰 Tages-Recap")
    if st.button("Recap für heute erstellen", type="primary"):
        with st.spinner("Recap wird geschrieben..."):
            try:
                st.session_state["last_recap"] = analyst.generate_recap()
            except Exception as e:
                st.error(f"Fehlgeschlagen: {e}")
    if st.session_state.get("last_recap"):
        st.markdown(st.session_state["last_recap"])

    with st.expander("Frühere Recaps (mit eigenen Notizen)"):
        for r in db.get_recaps():
            st.markdown(f"**📰 Recap {r['recap_date']}**")
            st.markdown(r["content"])
            new_note = st.text_area("Deine Notiz", value=r.get("user_note") or "",
                                    key=f"rn{r['id']}", height=80)
            if st.button("Notiz speichern", key=f"rb{r['id']}"):
                db.set_recap_note(r["id"], new_note.strip()); st.rerun()
            st.markdown("---")

    st.markdown("---")
    st.subheader("🗓 Kalender — nächste 14 Tage")
    today = date.today()
    dossiers_now = {d["code"]: d for d in db.get_dossiers()}
    stance_line = " · ".join(
        f"{DIRECTION_ICON.get(d['direction'], '⚪')} {c} {d['direction']}"
        for c, d in dossiers_now.items() if d["direction"] != "Neutral"
    )
    st.caption("Aktuelle Ausrichtungen: " + (stance_line if stance_line else "alle Neutral"))

    events = db.get_events(today.isoformat(), (today + timedelta(days=14)).isoformat())
    if not events:
        st.info("Keine anstehenden Events. Trag unten welche ein - oder fütter einen Wirtschaftskalender, die KI übernimmt Termine automatisch.")
    else:
        by_date = {}
        for e in events:
            by_date.setdefault(e["event_date"], []).append(e)
        for d_iso in sorted(by_date):
            st.markdown(f"**{d_iso}**")
            for e in by_date[d_iso]:
                asset = f"[{e['asset_code']}] " if e.get("asset_code") else ""
                note = f" — _{e['note']}_" if e.get("note") else ""
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.markdown(f"- {asset}**{e['title']}**{note}")
                with c2:
                    if st.button("🗑", key=f"ev{e['id']}"):
                        db.delete_event(e["id"]); st.rerun()

    with st.expander("➕ Event manuell eintragen"):
        ev_date = st.date_input("Datum", value=today, key="ev_date")
        ev_title = st.text_input("Event", placeholder="z.B. NFP-Daten", key="ev_title")
        ev_asset = st.selectbox("Asset (optional)", ["-"] + sorted(dossiers_now.keys()), key="ev_asset")
        ev_note = st.text_input("Notiz (optional)", placeholder="z.B. USD-Long-These prüfen falls schwach", key="ev_note")
        if st.button("Event speichern", disabled=not ev_title.strip()):
            db.add_event(ev_date.isoformat(), ev_title.strip(),
                         None if ev_asset == "-" else ev_asset, ev_note.strip() or None)
            st.rerun()

    st.markdown("---")
    st.subheader("🕰 Historie — wie stand eine Währung an Tag X?")
    hist_date = st.date_input("Datum wählen", value=today, key="hist_date")
    snaps = db.get_history_for_date(hist_date.isoformat())
    if not snaps:
        st.caption("Für diesen Tag gibt es (noch) keinen Schnappschuss. Schnappschüsse entstehen automatisch bei jeder Analyse und jedem Recap.")
    else:
        for s in snaps:
            icon = DIRECTION_ICON.get(s["direction"], "⚪")
            st.markdown(f"{icon} **{s['asset_code']}** {s['direction']} (Konfidenz {s['confidence']}) — {s['thesis']}")

# ---------------------------------------------------------------
# 5) BERICHTE
# ---------------------------------------------------------------
with tab_reports:
    st.subheader("Tages- & Wochenanalyse")
    c1, c2, c3 = st.columns(3)
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
    with c3:
        if st.button("🔎 Daten-Check (Gegencheck)"):
            with st.spinner("Unabhängiger Prüfer kontrolliert alle gespeicherten Daten..."):
                try:
                    st.session_state["last_report"] = analyst.run_audit()
                except Exception as e:
                    st.error(f"Fehlgeschlagen: {e}")

    if st.session_state.get("last_report"):
        st.markdown("---")
        st.markdown(st.session_state["last_report"])

    with st.expander("Frühere Berichte"):
        for r in db.get_reports():
            kind_label = {'taeglich': '☀️ Tagesbriefing', 'woechentlich': '📅 Wochenanalyse', 'pruefung': '🔎 Daten-Check'}.get(r['kind'], r['kind'])
            st.markdown(f"**{kind_label}** · {r['created_at'][:16].replace('T', ' ')}")
            st.markdown(r["content"])
            st.markdown("---")

# ---------------------------------------------------------------
# 6) REGELBUCH & LERNEN
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
                if st.button("Aus" if r["active"] else "An", key=f"r{r['id']}"):
                    db.set_rule_active(r["id"], not r["active"]); st.rerun()

    with col_lessons:
        st.subheader("🧠 Lern-Speicher")
        st.caption("Korrekturen ('das war falsch, weil...') werden DAUERHAFT gespeichert und bei jeder Analyse mitgelesen.")
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
                if st.button("Aus" if l["active"] else "An", key=f"l{l['id']}"):
                    db.set_lesson_active(l["id"], not l["active"]); st.rerun()

st.markdown("---")
st.caption(
    "⚠️ Diese App liefert strukturierte Analysen als Entscheidungsgrundlage. "
    "Keine Finanzberatung, keine Gewinn-Garantien - die Trade-Entscheidung liegt bei dir."
)
