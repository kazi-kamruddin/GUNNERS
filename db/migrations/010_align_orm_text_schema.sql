-- 010_align_orm_text_schema.sql
-- Migration: Align Postgres UUID / TEXT[] / JSONB / auth.users FK columns on
-- profiles, insights, posts, post_comments, post_reactions, conversations,
-- conversation_members, and direct_messages with SQLAlchemy String/Text ORM models
-- and prefixed application IDs (post_*, ins_*, conv_*, msg_*, cmt_*, rxn_*, usr_seed_*).
-- Preserves all RLS policies via (select auth.uid())::text and Supabase Auth handle_new_user().

-- =====================================================================
-- 1. Drop dependent RLS policies prior to column type alterations
-- =====================================================================
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;

DROP POLICY IF EXISTS "Allow public read access on public insights" ON public.insights;
DROP POLICY IF EXISTS "Authenticated users can create insights" ON public.insights;
DROP POLICY IF EXISTS "Users can update their own insights" ON public.insights;
DROP POLICY IF EXISTS "Users can delete their own insights" ON public.insights;

DROP POLICY IF EXISTS "Allow public read access on posts" ON public.posts;
DROP POLICY IF EXISTS "Authenticated users can create posts" ON public.posts;
DROP POLICY IF EXISTS "Authors can update their own posts" ON public.posts;
DROP POLICY IF EXISTS "Authors can delete their own posts" ON public.posts;

DROP POLICY IF EXISTS "Allow public read access on comments" ON public.post_comments;
DROP POLICY IF EXISTS "Authenticated users can create comments" ON public.post_comments;
DROP POLICY IF EXISTS "Authors can update their own comments" ON public.post_comments;
DROP POLICY IF EXISTS "Authors can delete their own comments" ON public.post_comments;

DROP POLICY IF EXISTS "Allow public read access on reactions" ON public.post_reactions;
DROP POLICY IF EXISTS "Authenticated users can add reactions" ON public.post_reactions;
DROP POLICY IF EXISTS "Users can remove their own reactions" ON public.post_reactions;

DROP POLICY IF EXISTS "Users can view conversations they belong to" ON public.conversations;
DROP POLICY IF EXISTS "Authenticated users can create conversations" ON public.conversations;

DROP POLICY IF EXISTS "Users can view members of their conversations" ON public.conversation_members;
DROP POLICY IF EXISTS "Users can join conversations" ON public.conversation_members;
DROP POLICY IF EXISTS "Users can update their own membership" ON public.conversation_members;

DROP POLICY IF EXISTS "Users can view messages in their conversations" ON public.direct_messages;
DROP POLICY IF EXISTS "Users can insert messages into their conversations" ON public.direct_messages;

-- =====================================================================
-- 2. Drop auth.users & UUID internal foreign keys prior to type changes
-- =====================================================================
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

ALTER TABLE public.insights DROP CONSTRAINT IF EXISTS insights_user_id_fkey;

ALTER TABLE public.posts DROP CONSTRAINT IF EXISTS posts_author_id_fkey;
ALTER TABLE public.posts DROP CONSTRAINT IF EXISTS posts_insight_id_fkey;

ALTER TABLE public.post_comments DROP CONSTRAINT IF EXISTS post_comments_author_id_fkey;
ALTER TABLE public.post_comments DROP CONSTRAINT IF EXISTS post_comments_post_id_fkey;

ALTER TABLE public.post_reactions DROP CONSTRAINT IF EXISTS post_reactions_user_id_fkey;
ALTER TABLE public.post_reactions DROP CONSTRAINT IF EXISTS post_reactions_post_id_fkey;

ALTER TABLE public.conversation_members DROP CONSTRAINT IF EXISTS conversation_members_user_id_fkey;
ALTER TABLE public.conversation_members DROP CONSTRAINT IF EXISTS conversation_members_conversation_id_fkey;

ALTER TABLE public.direct_messages DROP CONSTRAINT IF EXISTS direct_messages_sender_id_fkey;
ALTER TABLE public.direct_messages DROP CONSTRAINT IF EXISTS direct_messages_conversation_id_fkey;

-- =====================================================================
-- 3. Convert UUID / TEXT[] / JSONB columns cleanly to TEXT
-- =====================================================================
ALTER TABLE public.profiles
    ALTER COLUMN id TYPE TEXT USING id::text;

ALTER TABLE public.insights
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::text,
    ALTER COLUMN id SET DEFAULT (gen_random_uuid())::text,
    ALTER COLUMN user_id TYPE TEXT USING user_id::text,
    ALTER COLUMN team_ids TYPE TEXT USING array_to_string(team_ids, ','),
    ALTER COLUMN snapshot TYPE TEXT USING snapshot::text;

ALTER TABLE public.posts
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::text,
    ALTER COLUMN id SET DEFAULT (gen_random_uuid())::text,
    ALTER COLUMN author_id TYPE TEXT USING author_id::text,
    ALTER COLUMN insight_id TYPE TEXT USING insight_id::text;

ALTER TABLE public.post_comments
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::text,
    ALTER COLUMN id SET DEFAULT (gen_random_uuid())::text,
    ALTER COLUMN post_id TYPE TEXT USING post_id::text,
    ALTER COLUMN author_id TYPE TEXT USING author_id::text;

ALTER TABLE public.post_reactions
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::text,
    ALTER COLUMN id SET DEFAULT (gen_random_uuid())::text,
    ALTER COLUMN post_id TYPE TEXT USING post_id::text,
    ALTER COLUMN user_id TYPE TEXT USING user_id::text;

ALTER TABLE public.conversations
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::text,
    ALTER COLUMN id SET DEFAULT (gen_random_uuid())::text;

ALTER TABLE public.conversation_members
    ALTER COLUMN conversation_id TYPE TEXT USING conversation_id::text,
    ALTER COLUMN user_id TYPE TEXT USING user_id::text;

ALTER TABLE public.direct_messages
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::text,
    ALTER COLUMN id SET DEFAULT (gen_random_uuid())::text,
    ALTER COLUMN conversation_id TYPE TEXT USING conversation_id::text,
    ALTER COLUMN sender_id TYPE TEXT USING sender_id::text;

-- =====================================================================
-- 4. Restore internal relational foreign keys (now TEXT -> TEXT)
-- =====================================================================
ALTER TABLE public.posts
    ADD CONSTRAINT posts_insight_id_fkey
    FOREIGN KEY (insight_id) REFERENCES public.insights(id) ON DELETE SET NULL;

ALTER TABLE public.post_comments
    ADD CONSTRAINT post_comments_post_id_fkey
    FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;

ALTER TABLE public.post_reactions
    ADD CONSTRAINT post_reactions_post_id_fkey
    FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;

ALTER TABLE public.conversation_members
    ADD CONSTRAINT conversation_members_conversation_id_fkey
    FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;

ALTER TABLE public.direct_messages
    ADD CONSTRAINT direct_messages_conversation_id_fkey
    FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;

-- =====================================================================
-- 5. Restore & harden RLS policies using (select auth.uid())::text
-- =====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.direct_messages ENABLE ROW LEVEL SECURITY;

-- Profiles
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL AND (select auth.uid())::text = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND (select auth.uid())::text = id)
    WITH CHECK ((select auth.uid()) IS NOT NULL AND (select auth.uid())::text = id);

-- Insights
CREATE POLICY "Allow public read access on public insights"
    ON public.insights FOR SELECT
    TO public
    USING (
        is_public = true
        OR ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text)
    );

CREATE POLICY "Authenticated users can create insights"
    ON public.insights FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text);

CREATE POLICY "Users can update their own insights"
    ON public.insights FOR UPDATE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text)
    WITH CHECK ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text);

CREATE POLICY "Users can delete their own insights"
    ON public.insights FOR DELETE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text);

-- Posts
CREATE POLICY "Allow public read access on posts"
    ON public.posts FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can create posts"
    ON public.posts FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text);

CREATE POLICY "Authors can update their own posts"
    ON public.posts FOR UPDATE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text)
    WITH CHECK ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text);

CREATE POLICY "Authors can delete their own posts"
    ON public.posts FOR DELETE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text);

-- Post comments
CREATE POLICY "Allow public read access on comments"
    ON public.post_comments FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can create comments"
    ON public.post_comments FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text);

CREATE POLICY "Authors can update their own comments"
    ON public.post_comments FOR UPDATE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text)
    WITH CHECK ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text);

CREATE POLICY "Authors can delete their own comments"
    ON public.post_comments FOR DELETE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND author_id = (select auth.uid())::text);

-- Post reactions
CREATE POLICY "Allow public read access on reactions"
    ON public.post_reactions FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can add reactions"
    ON public.post_reactions FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text);

CREATE POLICY "Users can remove their own reactions"
    ON public.post_reactions FOR DELETE
    TO authenticated
    USING ((select auth.uid()) IS NOT NULL AND user_id = (select auth.uid())::text);

-- Conversations & Direct Messages (preserving 008 hardening)
CREATE POLICY "Users can view conversations they belong to"
    ON public.conversations FOR SELECT
    TO authenticated
    USING (private.is_conversation_member(id));

CREATE POLICY "Authenticated users can create conversations"
    ON public.conversations FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL);

CREATE POLICY "Users can view members of their conversations"
    ON public.conversation_members FOR SELECT
    TO authenticated
    USING (
        user_id = (select auth.uid())::text
        OR private.is_conversation_member(conversation_id)
    );

CREATE POLICY "Users can join conversations"
    ON public.conversation_members FOR INSERT
    TO authenticated
    WITH CHECK (
        (select auth.uid()) IS NOT NULL
        AND (
            user_id = (select auth.uid())::text
            OR private.is_conversation_member(conversation_id)
        )
    );

CREATE POLICY "Users can update their own membership"
    ON public.conversation_members FOR UPDATE
    TO authenticated
    USING (user_id = (select auth.uid())::text)
    WITH CHECK (user_id = (select auth.uid())::text);

CREATE POLICY "Users can view messages in their conversations"
    ON public.direct_messages FOR SELECT
    TO authenticated
    USING (private.is_conversation_member(conversation_id));

CREATE POLICY "Users can insert messages into their conversations"
    ON public.direct_messages FOR INSERT
    TO authenticated
    WITH CHECK (
        (select auth.uid()) IS NOT NULL
        AND sender_id = (select auth.uid())::text
        AND private.is_conversation_member(conversation_id)
    );

-- =====================================================================
-- 6. Ensure auth.users signup trigger inserts NEW.id::text cleanly
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
    VALUES (NEW.id::text, uname, dname, default_club, avatar, NOW(), NOW())
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF to_regprocedure('public.handle_new_user()') IS NOT NULL THEN
        REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC;
        REVOKE ALL ON FUNCTION public.handle_new_user() FROM anon, authenticated;
        GRANT EXECUTE ON FUNCTION public.handle_new_user() TO postgres, supabase_auth_admin, service_role;
    END IF;
END $$;
