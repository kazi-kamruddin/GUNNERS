-- 002_create_matches.sql
-- Migration: Competitions, Seasons, Matches, and Sync Metadata

-- 1. Create Competitions table
CREATE TABLE IF NOT EXISTS public.competitions (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    emblem_url TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Seed primary competitions
INSERT INTO public.competitions (id, code, name, country, emblem_url)
VALUES
    ('PL', 'PL', 'Premier League', 'England', 'https://crests.football-data.org/PL.png'),
    ('PD', 'PD', 'La Liga', 'Spain', 'https://crests.football-data.org/PD.png'),
    ('SA', 'SA', 'Serie A', 'Italy', 'https://crests.football-data.org/SA.png'),
    ('CL', 'CL', 'UEFA Champions League', 'Europe', 'https://crests.football-data.org/CL.png')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    country = EXCLUDED.country,
    emblem_url = EXCLUDED.emblem_url;

-- 2. Create Seasons table
CREATE TABLE IF NOT EXISTS public.seasons (
    id TEXT PRIMARY KEY,
    competition_id TEXT REFERENCES public.competitions(id) ON DELETE CASCADE,
    start_year INT NOT NULL,
    end_year INT NOT NULL,
    is_current BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Seed current seasons
INSERT INTO public.seasons (id, competition_id, start_year, end_year, is_current)
VALUES
    ('2024-2025-PL', 'PL', 2024, 2025, true),
    ('2024-2025-PD', 'PD', 2024, 2025, true),
    ('2024-2025-SA', 'SA', 2024, 2025, true),
    ('2024-2025-CL', 'CL', 2024, 2025, true)
ON CONFLICT (id) DO NOTHING;

-- 3. Enhance clubs table with crest_url and is_foundation
ALTER TABLE public.clubs ADD COLUMN IF NOT EXISTS crest_url TEXT;
ALTER TABLE public.clubs ADD COLUMN IF NOT EXISTS is_foundation BOOLEAN DEFAULT false;

UPDATE public.clubs SET
    crest_url = 'https://crests.football-data.org/57.png',
    is_foundation = true
WHERE id = 'arsenal';

UPDATE public.clubs SET
    crest_url = 'https://crests.football-data.org/86.png',
    is_foundation = true
WHERE id = 'real-madrid';

UPDATE public.clubs SET
    crest_url = 'https://crests.football-data.org/81.png',
    is_foundation = true
WHERE id = 'barcelona';

UPDATE public.clubs SET
    crest_url = 'https://crests.football-data.org/98.png',
    is_foundation = true
WHERE id = 'milan';

-- 4. Create Matches table
CREATE TABLE IF NOT EXISTS public.matches (
    id TEXT PRIMARY KEY,
    competition_id TEXT REFERENCES public.competitions(id) ON DELETE SET NULL,
    competition_name TEXT,
    season_id TEXT,
    home_team_id TEXT NOT NULL,
    home_team_name TEXT NOT NULL,
    home_team_crest TEXT,
    away_team_id TEXT NOT NULL,
    away_team_name TEXT NOT NULL,
    away_team_crest TEXT,
    matchday INT,
    utc_date TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'SCHEDULED',
    venue TEXT,
    home_score INT,
    away_score INT,
    winner TEXT,
    source TEXT DEFAULT 'football-data.org',
    last_updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_matches_utc_date ON public.matches(utc_date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_home_away ON public.matches(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_status_date ON public.matches(status, utc_date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_competition ON public.matches(competition_id);

-- 5. Create Sync Runs metadata table
CREATE TABLE IF NOT EXISTS public.sync_runs (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    matches_synced INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sync_runs_started ON public.sync_runs(started_at DESC);

-- 6. Row Level Security (RLS)
ALTER TABLE public.competitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seasons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_runs ENABLE ROW LEVEL SECURITY;

-- Drop old policies if existing
DROP POLICY IF EXISTS "Allow public read access on competitions" ON public.competitions;
DROP POLICY IF EXISTS "Allow public read access on seasons" ON public.seasons;
DROP POLICY IF EXISTS "Allow public read access on matches" ON public.matches;
DROP POLICY IF EXISTS "Allow public read access on sync_runs" ON public.sync_runs;

-- Public read policies
CREATE POLICY "Allow public read access on competitions"
    ON public.competitions FOR SELECT TO public USING (true);

CREATE POLICY "Allow public read access on seasons"
    ON public.seasons FOR SELECT TO public USING (true);

CREATE POLICY "Allow public read access on matches"
    ON public.matches FOR SELECT TO public USING (true);

CREATE POLICY "Allow public read access on sync_runs"
    ON public.sync_runs FOR SELECT TO public USING (true);

-- Explicit Schema Permissions
GRANT SELECT ON public.competitions TO anon, authenticated;
GRANT SELECT ON public.seasons TO anon, authenticated;
GRANT SELECT ON public.matches TO anon, authenticated;
GRANT SELECT ON public.sync_runs TO anon, authenticated;
