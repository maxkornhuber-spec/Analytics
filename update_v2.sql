-- =========================================================
-- UPDATE v2 - im Supabase SQL-Editor ausfuehren
-- (einmalig, nach dem ersten Schema. Sicher wiederholbar.)
-- =========================================================

-- Zins-Feld fuer jedes Dossier (Leitzins + Erwartung)
alter table dossiers add column if not exists policy_rate text not null default 'unbekannt';

-- Bank-Empfehlungen: eine Zeile pro Bank + Asset + Bericht
create table if not exists bank_recs (
  id uuid primary key default gen_random_uuid(),
  bank_name text not null,            -- z.B. 'JP Morgan' (entsteht automatisch beim ersten Bericht)
  asset_code text not null,           -- USD, EUR, ..., XAU
  stance text not null,               -- Long | Short | Neutral
  thesis text not null,               -- Kernaussage der Bank
  report_date text default null,      -- Datum laut Bericht (falls erkennbar)
  status text not null default 'aktiv',   -- aktiv | abgeloest | veraltet
  change_note text default null,      -- z.B. 'Vorher Long (12.06.) -> jetzt Neutral'
  created_at timestamptz not null default now()
);

create index if not exists idx_bank_recs_active on bank_recs (bank_name, asset_code, status);

-- v2.1: Marktstand je Dossier (aktuelle Kurse/Niveaus)
alter table dossiers add column if not exists spot_note text default null;
