-- =========================================================
-- DEIN ANALYSTENTEAM - Supabase Datenbank-Schema
-- Einmal komplett im Supabase SQL-Editor ausfuehren.
-- =========================================================

-- 1) Dossiers: ein "Analyst" pro Waehrung / Asset
create table if not exists dossiers (
  code text primary key,              -- z.B. 'USD', 'EUR', 'XAU'
  name text not null,                 -- z.B. 'US-Dollar'
  direction text not null default 'Neutral',   -- Long | Short | Neutral
  confidence int not null default 0,            -- 0-100
  confidence_label text not null default 'keine Daten',
  thesis text not null default 'Noch keine These - Dossier wartet auf erste Daten.',
  rate_outlook text not null default 'Unklar',  -- Zins-These, z.B. 'Erhoehung erwartet'
  last_change_note text default null,           -- Hinweis bei Kurswechsel
  updated_at timestamptz not null default now()
);

-- 2) Treiber: jede Information, die ein Dossier bestaetigt/widerspricht/kippt
create table if not exists drivers (
  id uuid primary key default gen_random_uuid(),
  asset_code text not null references dossiers(code),
  title text not null,
  impact text not null,               -- bestaetigt | widerspricht | kippt | neutral
  summary text not null,
  source_hint text default null,      -- Quelle/Datum laut Screenshot
  created_at timestamptz not null default now()
);

-- 3) Setups: vom Chef-Analysten erkannte Trade-Ideen
create table if not exists setups (
  id uuid primary key default gen_random_uuid(),
  pair text not null,                 -- z.B. 'EUR/USD'
  direction text not null,            -- Long | Short
  quality text not null,              -- A | B | C  (C = Finger weg)
  rationale text not null,
  warning text default null,          -- Bullshit-Filter-Warnung
  status text not null default 'offen',  -- offen | getradet | verworfen
  created_at timestamptz not null default now()
);

-- 4) Berichte: Tages- und Wochenanalysen
create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  kind text not null,                 -- taeglich | woechentlich
  content text not null,
  created_at timestamptz not null default now()
);

-- 5) Regelbuch: deine eigenen Setup-Regeln (werden bei JEDER Analyse mitgelesen)
create table if not exists rules (
  id uuid primary key default gen_random_uuid(),
  text text not null,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

-- 6) Lern-Speicher: deine Korrekturen, dauerhaft gespeichert,
--    werden bei JEDER Analyse mitgelesen ("das bleibt so")
create table if not exists lessons (
  id uuid primary key default gen_random_uuid(),
  lesson text not null,               -- die Lektion in deinen Worten
  context text default null,          -- worauf sie sich bezog
  active boolean not null default true,
  created_at timestamptz not null default now()
);

-- 7) Analyse-Log: was die KI aus jeder Fuetterung gemacht hat
create table if not exists analysis_log (
  id uuid primary key default gen_random_uuid(),
  note text default null,             -- deine Notiz beim Upload
  result text not null,               -- Kommentar der KI
  assets text default null,           -- betroffene Assets, kommagetrennt
  created_at timestamptz not null default now()
);

-- Die 9 Start-Dossiers anlegen (8 Majors + Gold)
insert into dossiers (code, name) values
  ('USD', 'US-Dollar'),
  ('EUR', 'Euro'),
  ('GBP', 'Britisches Pfund'),
  ('JPY', 'Japanischer Yen'),
  ('CHF', 'Schweizer Franken'),
  ('AUD', 'Australischer Dollar'),
  ('CAD', 'Kanadischer Dollar'),
  ('NZD', 'Neuseeland-Dollar'),
  ('XAU', 'Gold')
on conflict (code) do nothing;

-- Startregeln (kannst du in der App jederzeit aendern)
insert into rules (text) values
  ('Zwei gleichzeitige, gegenlaeufige starke Treiber = Day-Trade-Kandidat.'),
  ('Fokus auf die US-Session: Setups bevorzugen, die dort aktiv sind.'),
  ('Kein Trade direkt gegen eine frische Notenbank-Aussage.');
