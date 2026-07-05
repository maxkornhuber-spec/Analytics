-- =========================================================
-- UPDATE v3 - im Supabase SQL-Editor ausfuehren (einmalig)
-- Recap, Kalender & Historie
-- =========================================================

-- Kalender-Events (manuell oder von der KI aus Kalender-Screenshots uebernommen)
create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  event_date date not null,
  title text not null,                 -- z.B. 'NFP-Daten'
  asset_code text default null,        -- betroffenes Asset, z.B. 'USD'
  note text default null,              -- deine Notiz / KI-Hinweis, z.B. 'USD-Long nicht mehr valide falls schwach'
  created_at timestamptz not null default now()
);
create index if not exists idx_events_date on events (event_date);

-- Tages-Schnappschuesse aller Dossiers (fuer 'Wie stand USD am X?')
create table if not exists dossier_history (
  id uuid primary key default gen_random_uuid(),
  snap_date date not null,
  asset_code text not null,
  direction text not null,
  confidence int not null,
  thesis text not null,
  created_at timestamptz not null default now(),
  unique (snap_date, asset_code)
);

-- Tages-Recaps
create table if not exists recaps (
  id uuid primary key default gen_random_uuid(),
  recap_date date not null,
  content text not null,               -- KI-Recap
  user_note text default null,         -- deine eigene Ergaenzung
  created_at timestamptz not null default now()
);
