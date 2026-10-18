-- 001_create_profiles.sql
-- Migration: Setup Clubs, User Profiles, RLS, and Auth Signup Trigger

-- 1. Create clubs lookup table
CREATE TABLE IF NOT EXISTS public.clubs (
    id TEXT PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    primary_color TEXT NOT NULL,
    secondary_color TEXT NOT NULL,
    accent_color TEXT NOT NULL,
    league TEXT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Seed the 4 Foundation Clubs
INSERT INTO public.clubs (id, slug, name, short_name, primary_color, secondary_color, accent_color, league, country)
VALUES
    ('arsenal', 'arsenal', 'Arsenal FC', 'Arsenal', '#EF0107', '#FFFFFF', '#9C824A', 'Premier League', 'England'),
    ('real-madrid', 'real-madrid', 'Real Madrid CF', 'Real Madrid', '#00529F', '#FFFFFF', '#EEB028', 'La Liga', 'Spain'),
    ('barcelona', 'barcelona', 'FC Barcelona', 'Barcelona', '#A50044', '#004D98', '#EDBB00', 'La Liga', 'Spain'),
    ('milan', 'milan', 'AC Milan', 'AC Milan', '#FB090B', '#000000', '#C0C0C0', 'Serie A', 'Italy')
ON CONFLICT (id) DO UPDATE SET
    primary_color = EXCLUDED.primary_color,
    secondary_color = EXCLUDED.secondary_color,
    accent_color = EXCLUDED.accent_color;

-- 2. Create profiles table linked to auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE,
    display_name TEXT,
    favorite_club_id TEXT NOT NULL REFERENCES public.clubs(id) DEFAULT 'arsenal',
    bio TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Indexes for performant lookups
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_favorite_club ON public.profiles(favorite_club_id);

-- 3. Row Level Security (RLS)
ALTER TABLE public.clubs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop old policies if they exist to allow clean re-runs
DROP POLICY IF EXISTS "Allow public read access on clubs" ON public.clubs;
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;

-- Clubs policies (Public read-only)
CREATE POLICY "Allow public read access on clubs"
    ON public.clubs
    FOR SELECT
    TO public
    USING (true);

-- Profiles policies
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles
    FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles
    FOR INSERT
    TO authenticated
    WITH CHECK ((SELECT auth.uid()) = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING ((SELECT auth.uid()) = id)
    WITH CHECK ((SELECT auth.uid()) = id);

-- 4. Trigger Function: automatically creates a profile on new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    default_club TEXT;
    uname TEXT;
    dname TEXT;
BEGIN
    default_club := COALESCE(NEW.raw_user_meta_data->>'favorite_club_id', 'arsenal');
    
    -- Verify club exists in clubs table, fallback to arsenal
    IF NOT EXISTS (SELECT 1 FROM public.clubs WHERE id = default_club) THEN
        default_club := 'arsenal';
    END IF;

    uname := COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1));
    dname := COALESCE(NEW.raw_user_meta_data->>'display_name', uname);

    -- Ensure unique username if duplicate
    IF EXISTS (SELECT 1 FROM public.profiles WHERE username = uname) THEN
        uname := uname || '_' || substr(NEW.id::text, 1, 4);
    END IF;

    INSERT INTO public.profiles (id, username, display_name, favorite_club_id, created_at, updated_at)
    VALUES (NEW.id, uname, dname, default_club, NOW(), NOW())
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- 5. Explicit Data API Permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.clubs TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.profiles TO anon, authenticated;
