-- 008_overhaul_schema_and_rls.sql
-- Migration: Phase 1 Overhaul — RLS Hardening, Schema Parity, OAuth Trigger, Storage Buckets, and Indexes
-- Safe and idempotent whether run after 001..007.sql or seed_community.py.

-- =====================================================================
-- 1. Private helper for non-recursive conversation membership RLS
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS private;
GRANT USAGE ON SCHEMA private TO authenticated;

CREATE OR REPLACE FUNCTION private.is_conversation_member(p_conv_id TEXT)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public
AS $$
    SELECT (select auth.uid()) IS NOT NULL AND EXISTS (
        SELECT 1
        FROM public.conversation_members cm
        WHERE cm.conversation_id::text = p_conv_id
          AND cm.user_id::text = (select auth.uid())::text
    );
$$;

REVOKE ALL ON FUNCTION private.is_conversation_member(TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION private.is_conversation_member(TEXT) TO authenticated;

-- =====================================================================
-- 2. Tighten permissive RLS from 005 (Direct Messaging)
-- =====================================================================
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.direct_messages ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.conversations FROM anon;
REVOKE ALL ON public.conversation_members FROM anon;
REVOKE ALL ON public.direct_messages FROM anon;

DROP POLICY IF EXISTS "Users can view conversations they belong to" ON public.conversations;
DROP POLICY IF EXISTS "Authenticated users can create conversations" ON public.conversations;

CREATE POLICY "Users can view conversations they belong to"
    ON public.conversations FOR SELECT
    TO authenticated
    USING (private.is_conversation_member(id::text));

CREATE POLICY "Authenticated users can create conversations"
    ON public.conversations FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL);

DROP POLICY IF EXISTS "Users can view members of their conversations" ON public.conversation_members;
DROP POLICY IF EXISTS "Users can join conversations" ON public.conversation_members;
DROP POLICY IF EXISTS "Users can update their own membership" ON public.conversation_members;

CREATE POLICY "Users can view members of their conversations"
    ON public.conversation_members FOR SELECT
    TO authenticated
    USING (
        user_id::text = (select auth.uid())::text
        OR private.is_conversation_member(conversation_id::text)
    );

CREATE POLICY "Users can join conversations"
    ON public.conversation_members FOR INSERT
    TO authenticated
    WITH CHECK (
        (select auth.uid()) IS NOT NULL
        AND (
            user_id::text = (select auth.uid())::text
            OR private.is_conversation_member(conversation_id::text)
        )
    );

CREATE POLICY "Users can update their own membership"
    ON public.conversation_members FOR UPDATE
    TO authenticated
    USING (user_id::text = (select auth.uid())::text)
    WITH CHECK (user_id::text = (select auth.uid())::text);

DROP POLICY IF EXISTS "Users can view messages in their conversations" ON public.direct_messages;
DROP POLICY IF EXISTS "Users can insert messages into their conversations" ON public.direct_messages;

CREATE POLICY "Users can view messages in their conversations"
    ON public.direct_messages FOR SELECT
    TO authenticated
    USING (private.is_conversation_member(conversation_id::text));

CREATE POLICY "Users can insert messages into their conversations"
    ON public.direct_messages FOR INSERT
    TO authenticated
    WITH CHECK (
        (select auth.uid()) IS NOT NULL
        AND sender_id::text = (select auth.uid())::text
        AND private.is_conversation_member(conversation_id::text)
    );

GRANT SELECT, INSERT ON public.conversations TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.conversation_members TO authenticated;
GRANT SELECT, INSERT ON public.direct_messages TO authenticated;

-- =====================================================================
-- 3. Tighten permissive RLS from 007 (Tactical Boards)
-- =====================================================================
ALTER TABLE public.tactical_boards ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Tactical boards are viewable by everyone" ON public.tactical_boards;
DROP POLICY IF EXISTS "Tactical boards are viewable when public or owned" ON public.tactical_boards;
DROP POLICY IF EXISTS "Authenticated users can create tactical boards" ON public.tactical_boards;
DROP POLICY IF EXISTS "Users can update their own tactical boards" ON public.tactical_boards;
DROP POLICY IF EXISTS "Users can delete their own tactical boards" ON public.tactical_boards;

CREATE POLICY "Tactical boards are viewable when public or owned"
    ON public.tactical_boards FOR SELECT
    TO public
    USING (
        is_public = true
        OR (
            (select auth.uid()) IS NOT NULL
            AND (select auth.uid())::text = user_id::text
        )
    );

CREATE POLICY "Authenticated users can create tactical boards"
    ON public.tactical_boards FOR INSERT
    TO authenticated
    WITH CHECK (
        (select auth.uid()) IS NOT NULL
        AND (select auth.uid())::text = user_id::text
    );

CREATE POLICY "Users can update their own tactical boards"
    ON public.tactical_boards FOR UPDATE
    TO authenticated
    USING (
        (select auth.uid()) IS NOT NULL
        AND (select auth.uid())::text = user_id::text
    )
    WITH CHECK (
        (select auth.uid()) IS NOT NULL
        AND (select auth.uid())::text = user_id::text
    );

CREATE POLICY "Users can delete their own tactical boards"
    ON public.tactical_boards FOR DELETE
    TO authenticated
    USING (
        (select auth.uid()) IS NOT NULL
        AND (select auth.uid())::text = user_id::text
    );

GRANT SELECT ON public.tactical_boards TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.tactical_boards TO authenticated;

-- =====================================================================
-- 4. Overhaul Schema Parity Columns
-- =====================================================================
ALTER TABLE public.posts ADD COLUMN IF NOT EXISTS image_url TEXT;

ALTER TABLE public.clubs ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

ALTER TABLE public.matches ADD COLUMN IF NOT EXISTS goalscorers JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.matches ADD COLUMN IF NOT EXISTS lineups JSONB DEFAULT '{}'::jsonb;
ALTER TABLE public.matches ADD COLUMN IF NOT EXISTS highlights JSONB DEFAULT '[]'::jsonb;

ALTER TABLE public.players ADD COLUMN IF NOT EXISTS portrait_url TEXT;
ALTER TABLE public.players ADD COLUMN IF NOT EXISTS action_url TEXT;
ALTER TABLE public.players ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE public.players ADD COLUMN IF NOT EXISTS date_of_birth TEXT;
ALTER TABLE public.players ADD COLUMN IF NOT EXISTS height TEXT;
ALTER TABLE public.players ADD COLUMN IF NOT EXISTS joined_date TEXT;

-- =====================================================================
-- 5. OAuth-Resilient Auth Signup Trigger Function (001)
-- =====================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    default_club TEXT;
    raw_uname TEXT;
    base_uname TEXT;
    uname TEXT;
    dname TEXT;
    avatar TEXT;
    id_suffix TEXT;
BEGIN
    default_club := COALESCE(NULLIF(trim(NEW.raw_user_meta_data->>'favorite_club_id'), ''), 'arsenal');

    -- Verify club exists in clubs table, fallback to arsenal
    IF NOT EXISTS (SELECT 1 FROM public.clubs WHERE id = default_club) THEN
        default_club := 'arsenal';
    END IF;

    id_suffix := substr(replace(NEW.id::text, '-', ''), 1, 6);
    raw_uname := NULLIF(trim(NEW.raw_user_meta_data->>'username'), '');

    IF raw_uname IS NOT NULL THEN
        uname := lower(regexp_replace(raw_uname, '[^a-zA-Z0-9_]+', '_', 'g'));
        uname := trim(BOTH '_' FROM uname);
        IF uname = '' THEN
            uname := 'gooner_' || id_suffix;
        END IF;
    ELSE
        base_uname := lower(
            regexp_replace(
                COALESCE(NULLIF(split_part(COALESCE(NEW.email, ''), '@', 1), ''), 'gooner'),
                '[^a-z0-9_]+',
                '_',
                'g'
            )
        );
        base_uname := trim(BOTH '_' FROM base_uname);
        IF base_uname = '' THEN
            base_uname := 'gooner';
        END IF;
        uname := left(base_uname, 40) || '_' || id_suffix;
    END IF;

    -- Guard against any remaining collision on profiles_username_key
    IF EXISTS (SELECT 1 FROM public.profiles WHERE lower(username) = lower(uname)) THEN
        uname := left(uname, 32) || '_' || substr(replace(NEW.id::text, '-', ''), 1, 10);
    END IF;

    dname := COALESCE(
        NULLIF(trim(NEW.raw_user_meta_data->>'full_name'), ''),
        NULLIF(trim(NEW.raw_user_meta_data->>'name'), ''),
        NULLIF(trim(NEW.raw_user_meta_data->>'display_name'), ''),
        NULLIF(split_part(COALESCE(NEW.email, ''), '@', 1), ''),
        uname
    );

    avatar := COALESCE(
        NULLIF(trim(NEW.raw_user_meta_data->>'avatar_url'), ''),
        NULLIF(trim(NEW.raw_user_meta_data->>'picture'), '')
    );

    INSERT INTO public.profiles (id, username, display_name, favorite_club_id, avatar_url, created_at, updated_at)
    VALUES (NEW.id, uname, dname, default_club, avatar, NOW(), NOW())
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF to_regclass('auth.users') IS NOT NULL THEN
        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        CREATE TRIGGER on_auth_user_created
            AFTER INSERT ON auth.users
            FOR EACH ROW
            EXECUTE FUNCTION public.handle_new_user();
    END IF;
END $$;

-- =====================================================================
-- 6. Supabase Storage Buckets & RLS (avatars, terrace-media)
-- =====================================================================
INSERT INTO storage.buckets (id, name, public)
VALUES
    ('avatars', 'avatars', true),
    ('terrace-media', 'terrace-media', true)
ON CONFLICT (id) DO NOTHING;

-- Avatars bucket policies (upsert requires SELECT + INSERT + UPDATE)
DROP POLICY IF EXISTS "Public read access for avatars" ON storage.objects;
DROP POLICY IF EXISTS "Users can upload their own avatar" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own avatar" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own avatar" ON storage.objects;

CREATE POLICY "Public read access for avatars"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'avatars');

CREATE POLICY "Users can upload their own avatar"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    );

CREATE POLICY "Users can update their own avatar"
    ON storage.objects FOR UPDATE
    TO authenticated
    USING (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    )
    WITH CHECK (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    );

CREATE POLICY "Users can delete their own avatar"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'avatars'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    );

-- Terrace-media bucket policies (upsert requires SELECT + INSERT + UPDATE)
DROP POLICY IF EXISTS "Public read access for terrace media" ON storage.objects;
DROP POLICY IF EXISTS "Users can upload their own terrace media" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own terrace media" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own terrace media" ON storage.objects;

CREATE POLICY "Public read access for terrace media"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'terrace-media');

CREATE POLICY "Users can upload their own terrace media"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'terrace-media'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    );

CREATE POLICY "Users can update their own terrace media"
    ON storage.objects FOR UPDATE
    TO authenticated
    USING (
        bucket_id = 'terrace-media'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    )
    WITH CHECK (
        bucket_id = 'terrace-media'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    );

CREATE POLICY "Users can delete their own terrace media"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'terrace-media'
        AND (storage.foldername(name))[1] = (select auth.uid())::text
    );

-- =====================================================================
-- 7. Useful Performance Indexes
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON public.posts(author_id);
CREATE INDEX IF NOT EXISTS idx_insights_user_id ON public.insights(user_id);
CREATE INDEX IF NOT EXISTS idx_tactical_boards_user_id ON public.tactical_boards(user_id);
