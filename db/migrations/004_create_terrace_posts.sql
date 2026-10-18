-- 004_create_terrace_posts.sql
-- Migration: The Terrace Community Feeds, Insight Posts, Comments, and Reactions

-- 1. Create Posts table
CREATE TABLE IF NOT EXISTS public.posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    author_name TEXT NOT NULL DEFAULT 'Supporter',
    author_club_id TEXT REFERENCES public.clubs(id) DEFAULT 'arsenal',
    club_id TEXT REFERENCES public.clubs(id) ON DELETE SET NULL, -- NULL means Global Terrace
    content TEXT NOT NULL,
    insight_id UUID REFERENCES public.insights(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Indexes for feed queries
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON public.posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_club_id ON public.posts(club_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_insight_id ON public.posts(insight_id);

-- 2. Create Comments table
CREATE TABLE IF NOT EXISTS public.post_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE NOT NULL,
    author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    author_name TEXT NOT NULL DEFAULT 'Supporter',
    author_club_id TEXT REFERENCES public.clubs(id) DEFAULT 'arsenal',
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_post_comments_post_id ON public.post_comments(post_id, created_at ASC);

-- 3. Create Reactions table
CREATE TABLE IF NOT EXISTS public.post_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES public.posts(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    reaction_type TEXT NOT NULL DEFAULT 'cheer',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(post_id, user_id, reaction_type)
);

CREATE INDEX IF NOT EXISTS idx_post_reactions_post_id ON public.post_reactions(post_id);

-- 4. Row Level Security (RLS)
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_reactions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Allow public read access on posts" ON public.posts;
DROP POLICY IF EXISTS "Authenticated users can create posts" ON public.posts;
DROP POLICY IF EXISTS "Authors can update their own posts" ON public.posts;
DROP POLICY IF EXISTS "Authors can delete their own posts" ON public.posts;

DROP POLICY IF EXISTS "Allow public read access on comments" ON public.post_comments;
DROP POLICY IF EXISTS "Authenticated users can create comments" ON public.post_comments;
DROP POLICY IF EXISTS "Authors can delete their own comments" ON public.post_comments;

DROP POLICY IF EXISTS "Allow public read access on reactions" ON public.post_reactions;
DROP POLICY IF EXISTS "Authenticated users can add reactions" ON public.post_reactions;
DROP POLICY IF EXISTS "Users can remove their own reactions" ON public.post_reactions;

-- Posts policies
CREATE POLICY "Allow public read access on posts"
    ON public.posts FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can create posts"
    ON public.posts FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = author_id OR author_id IS NULL);

CREATE POLICY "Authors can update their own posts"
    ON public.posts FOR UPDATE
    TO authenticated
    USING (auth.uid() = author_id)
    WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Authors can delete their own posts"
    ON public.posts FOR DELETE
    TO authenticated
    USING (auth.uid() = author_id);

-- Comments policies
CREATE POLICY "Allow public read access on comments"
    ON public.post_comments FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can create comments"
    ON public.post_comments FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = author_id OR author_id IS NULL);

CREATE POLICY "Authors can delete their own comments"
    ON public.post_comments FOR DELETE
    TO authenticated
    USING (auth.uid() = author_id);

-- Reactions policies
CREATE POLICY "Allow public read access on reactions"
    ON public.post_reactions FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can add reactions"
    ON public.post_reactions FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can remove their own reactions"
    ON public.post_reactions FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- Explicit Permissions
GRANT SELECT ON public.posts TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.posts TO authenticated;

GRANT SELECT ON public.post_comments TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.post_comments TO authenticated;

GRANT SELECT ON public.post_reactions TO anon, authenticated;
GRANT INSERT, DELETE ON public.post_reactions TO authenticated;
