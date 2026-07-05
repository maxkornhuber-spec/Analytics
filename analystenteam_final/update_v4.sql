-- =========================================================
-- UPDATE v4 - im Supabase SQL-Editor ausfuehren (einmalig)
-- Narrativ-Score, Einpreisung, 10Y-Renditen
-- =========================================================

alter table dossiers add column if not exists narrative_score int not null default 0;   -- -3 bis +3
alter table dossiers add column if not exists priced_in text default null;              -- was ist eingepreist
alter table dossiers add column if not exists yield_10y text default null;              -- 10J-Rendite, z.B. '4.35%'

-- Narrativ-Score auch in der Historie mitschreiben (fuer Divergenz-Erkennung)
alter table dossier_history add column if not exists narrative_score int not null default 0;
