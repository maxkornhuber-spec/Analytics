# 🔄 UPDATE auf v2 – in 3 Schritten (ca. 5 Minuten)

## Was ist neu in v2

- **🏦 Banken-Reiter**: Bankberichte (JP Morgan, ING, ...) werden automatisch erkannt und SEPARAT geführt. Neuer Bericht derselben Bank ersetzt die alte Empfehlung automatisch (mit Meinungswechsel-Notiz). Nach 30 Tagen gelten Empfehlungen als veraltet. Konsens-Übersicht je Asset.
- **📥 Neuer Daten-Eingang**: große Ziehfläche für Screenshots **und PDFs** + separates Textfeld für kopierte Texte/Berichte.
- **Zinsbild**: Jedes Dossier führt jetzt den Leitzins + Erwartung; Zinsdifferenzen fließen in Setup-Bewertungen ein.
- **Datums-Intelligenz**: Die KI prüft das Datum der Info gegen heute, warnt bei veralteten Daten (>14 Tage) und sagt es offen, wenn kein Datum erkennbar ist.
- **Duplikat-Schutz**: Bereits gefütterte Infos werden erkannt und nicht doppelt gespeichert (Meldung "♻️ Duplikat erkannt").
- **Berichte**: Tages-/Wochenanalyse vergleichen deine Thesen jetzt mit dem Banken-Konsens und warnen bei einseitig gefütterten Dossiers.

**Neu in v2.1 (schon enthalten):**
- **🔎 Daten-Check (Gegencheck)**: Button im Berichte-Reiter. Ein unabhängiger Prüfer kontrolliert ALLE gespeicherten Daten: Konsistenz, Duplikate, Veraltetes, einseitige Dossiers, saubere Bank-Zuordnung — mit Gesamturteil und konkreten Handlungsempfehlungen. Perfekt nach dem großen Sonntags-Füttern.
- **Marktstände**: Kopierst du aktuelle Kurse rein (z.B. "EUR/USD 1.0850"), übernimmt die App sie automatisch als "Marktstand" ins jeweilige Dossier.
- **Strikte Trennung bestätigt**: Bankmeinungen berühren die Dossiers nie; neue Bankliste löst alte Empfehlungen automatisch ab (kurze "abgelöst"-Notiz in der Historie).

## Schritt 1: SQL-Update in Supabase

Supabase → SQL Editor → kompletten Inhalt von **`update_v2.sql`** einfügen → Run.
(Falls wieder die RLS-Frage kommt: "Laufen ohne RLS".)

## Schritt 2: 4 Dateien auf GitHub ersetzen

Im Repo jeweils die Datei öffnen → Stift-Symbol (Bearbeiten) → kompletten Inhalt löschen → neuen Inhalt aus diesem ZIP reinkopieren → "Änderungen übernehmen":

1. `app.py`
2. `core/prompts.py`
3. `core/db.py`
4. `core/analyst.py`

(Alternativ: Dateien per "Upload files" hochladen – gleiche Namen überschreiben die alten.)

## Schritt 3: App neu starten

Streamlit Cloud → deine App → Menü (⋮) → **Reboot**. Fertig.

## Kurztest danach

1. App öffnen → neuer Reiter **🏦 Banken** ist da.
2. "Daten füttern": Ziehfläche für Dateien + Textfeld sind getrennt sichtbar.
3. Einen beliebigen Bankbericht (Text reicht) füttern → Bank erscheint automatisch im Banken-Reiter.
