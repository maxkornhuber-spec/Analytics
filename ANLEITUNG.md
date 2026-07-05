# 🚀 Dein Analystenteam – Schritt-für-Schritt-Anleitung

Von null bis zur laufenden App in ca. 15 Minuten. Reihenfolge genau einhalten.

---

## Schritt 1: Supabase vorbereiten (Datenbank)

1. Auf https://supabase.com einloggen → **New Project** anlegen (Name egal, z.B. `analystenteam`).
2. Links im Menü **SQL Editor** öffnen.
3. Den kompletten Inhalt der Datei **`schema.sql`** einfügen → **Run** klicken.
   → Damit entstehen alle Tabellen + die 9 Start-Dossiers (8 Majors + Gold) + 3 Startregeln.
4. Links im Menü **Project Settings → API** öffnen und dir zwei Werte kopieren:
   - **Project URL** (beginnt mit `https://...supabase.co`)
   - **anon public key** (langer Schlüssel)

## Schritt 2: Code auf GitHub laden

1. Auf https://github.com ein **neues privates Repository** anlegen (z.B. `analystenteam`). **Privat ist wichtig.**
2. Alle Dateien aus diesem Projekt hochladen (per GitHub-Webseite "Add file → Upload files" oder per Git):
   - `app.py`
   - `core/` (kompletter Ordner: `__init__.py`, `db.py`, `analyst.py`, `prompts.py`)
   - `requirements.txt`
   - `schema.sql`
   - `.gitignore`
   - `ANLEITUNG.md` (optional)
3. **Nicht hochladen:** eine echte `secrets.toml` mit deinen Schlüsseln (die `.gitignore` verhindert das bei Git automatisch).

## Schritt 3: App auf Streamlit Cloud starten

1. Auf https://share.streamlit.io einloggen (mit deinem GitHub-Account).
2. **New app** → dein Repository `analystenteam` wählen → Main file: **`app.py`** → Deploy.
3. In der App-Übersicht: **Settings → Secrets** öffnen und Folgendes eintragen (deine echten Werte einsetzen):

```toml
SUPABASE_URL = "https://DEIN-PROJEKT.supabase.co"
SUPABASE_KEY = "DEIN-SUPABASE-ANON-KEY"
ANTHROPIC_API_KEY = "sk-ant-DEIN-KEY"
APP_CODE = "DEIN-GEHEIMER-ZUGANGSCODE"
```

4. **Save** → App startet neu. Fertig.

> Den **ANTHROPIC_API_KEY** bekommst du unter https://console.anthropic.com → API Keys.
> Den **APP_CODE** denkst du dir selbst aus – das ist dein privater Zugangscode. Ohne ihn kommt niemand rein.

## Schritt 4: Erste Nutzung (Sonntag-Ready)

1. App öffnen → Zugangscode eingeben.
2. **🧠 Regelbuch & Lernen**: deine 3 Startregeln prüfen, eigene Regeln ergänzen (klein anfangen, 3–5 Regeln).
3. **📥 Daten füttern**: Screenshots hochladen – ein Thema pro Ladung, Quelle & Datum sichtbar lassen. Optional eine Notiz dazu. → **Analysieren** klicken.
4. **📊 Dashboard**: die Dossiers beobachten – Ausrichtung, Konfidenz, These, Kurswechsel-Warnungen.
5. **🎯 Setups**: erkannte Trade-Ideen mit Qualität A/B/C. Bei C sagt dir der Bullshit-Filter klar "Finger weg".
6. **📄 Berichte**: morgens **Tagesbriefing**, am Wochenende **Wochenanalyse** auf Knopfdruck.

## So lernst du dein Team an (die nächsten 2 Wochen)

- War eine Einschätzung **falsch**? → **🧠 Lern-Speicher** → Lektion eintragen ("Das war falsch, weil...").
  Jede Lektion wird **dauerhaft gespeichert** und bei **jeder** künftigen Analyse mitgelesen. Nichts geht verloren.
- Eine Lektion war doch nicht gut? → auf **Aus** stellen (sie bleibt gespeichert, wird aber nicht mehr angewendet).
- Gleiche Logik beim Regelbuch: Regeln jederzeit ergänzen, an- und ausschalten.
- Wöchentliche Routine: Welche Warnung war richtig, welche falsch? → Regeln/Lektionen nachschärfen.

## Lokal testen (optional)

```bash
pip install -r requirements.txt
# Datei .streamlit/secrets.toml anlegen (Vorlage: secrets.toml.example) und Werte eintragen
streamlit run app.py
```

## Wichtige Hinweise

- **Kosten:** Jede Analyse und jeder Bericht kostet API-Guthaben auf deinem Anthropic-Account (wenige Cent pro Aufruf, Screenshots kosten etwas mehr als Text).
- **Privat:** Repository privat halten, `APP_CODE` niemandem geben, Schlüssel nur in den Secrets speichern – nie im Code.
- **Keine Finanzberatung:** Die App liefert strukturierte Entscheidungsgrundlagen, keine Gewinn-Garantien. Die Trade-Entscheidung liegt immer bei dir.
