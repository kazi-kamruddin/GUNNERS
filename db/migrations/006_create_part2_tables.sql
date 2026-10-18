-- 006_create_part2_tables.sql
-- Migration: Part 2 Features (Players, Predictions, Notifications)

-- 1. Create Players Table
CREATE TABLE IF NOT EXISTS public.players (
    id TEXT PRIMARY KEY,
    club_id TEXT REFERENCES public.clubs(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    position TEXT NOT NULL, -- Goalkeeper, Defender, Midfielder, Attacker
    jersey_number INTEGER NOT NULL,
    nationality TEXT NOT NULL,
    appearances INTEGER DEFAULT 0 NOT NULL,
    goals INTEGER DEFAULT 0 NOT NULL,
    assists INTEGER DEFAULT 0 NOT NULL,
    clean_sheets INTEGER DEFAULT 0 NOT NULL,
    minutes_played INTEGER DEFAULT 0 NOT NULL,
    yellow_cards INTEGER DEFAULT 0 NOT NULL,
    red_cards INTEGER DEFAULT 0 NOT NULL,
    photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_players_club ON public.players(club_id);
CREATE INDEX IF NOT EXISTS idx_players_position ON public.players(position);

-- 2. Create Predictions Table
CREATE TABLE IF NOT EXISTS public.predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    user_name TEXT NOT NULL DEFAULT 'Supporter',
    user_club_id TEXT REFERENCES public.clubs(id) DEFAULT 'arsenal',
    match_id TEXT NOT NULL,
    predicted_home_score INTEGER NOT NULL,
    predicted_away_score INTEGER NOT NULL,
    points_awarded INTEGER DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE (user_id, match_id)
);

CREATE INDEX IF NOT EXISTS idx_predictions_user ON public.predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_match ON public.predictions(match_id);

-- 3. Create Notifications Table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type TEXT NOT NULL, -- comment, cheer, direct_message, prediction_result
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    link TEXT NOT NULL DEFAULT '/',
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON public.notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON public.notifications(created_at DESC);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.players ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Players RLS: Public read-only
DROP POLICY IF EXISTS "Public can view players" ON public.players;
CREATE POLICY "Public can view players"
    ON public.players FOR SELECT
    TO public
    USING (true);

-- Predictions RLS: Users can view all predictions, but only insert/update their own
DROP POLICY IF EXISTS "Users can view predictions" ON public.predictions;
CREATE POLICY "Users can view predictions"
    ON public.predictions FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS "Users can insert own predictions" ON public.predictions;
CREATE POLICY "Users can insert own predictions"
    ON public.predictions FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own predictions" ON public.predictions;
CREATE POLICY "Users can update own predictions"
    ON public.predictions FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Notifications RLS: Users can only see and update their own notifications
DROP POLICY IF EXISTS "Users can view own notifications" ON public.notifications;
CREATE POLICY "Users can view own notifications"
    ON public.notifications FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own notifications" ON public.notifications;
CREATE POLICY "Users can update own notifications"
    ON public.notifications FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Permissions
GRANT SELECT ON public.players TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.predictions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.notifications TO authenticated;
