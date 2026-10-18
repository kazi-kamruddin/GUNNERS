-- 003_create_insights.sql
-- Migration: Reusable & Shareable Analytics Insights

CREATE TABLE IF NOT EXISTS public.insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    author_name TEXT NOT NULL DEFAULT 'Supporter',
    author_club_id TEXT REFERENCES public.clubs(id) DEFAULT 'arsenal',
    title TEXT NOT NULL,
    description TEXT,
    metric TEXT NOT NULL,
    team_ids TEXT[] NOT NULL,
    venue TEXT NOT NULL DEFAULT 'all',
    competition_id TEXT REFERENCES public.competitions(id) ON DELETE SET NULL,
    chart_type TEXT NOT NULL DEFAULT 'bar',
    snapshot JSONB NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Indexes for performant feed retrieval
CREATE INDEX IF NOT EXISTS idx_insights_created_at ON public.insights(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_insights_user_id ON public.insights(user_id);
CREATE INDEX IF NOT EXISTS idx_insights_metric ON public.insights(metric);

-- Row Level Security (RLS)
ALTER TABLE public.insights ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read access on public insights" ON public.insights;
DROP POLICY IF EXISTS "Authenticated users can create insights" ON public.insights;
DROP POLICY IF EXISTS "Users can update their own insights" ON public.insights;
DROP POLICY IF EXISTS "Users can delete their own insights" ON public.insights;

-- Public read access
CREATE POLICY "Allow public read access on public insights"
    ON public.insights FOR SELECT
    TO public
    USING (is_public = true OR (auth.uid() IS NOT NULL AND auth.uid() = user_id));

-- Authenticated creation
CREATE POLICY "Authenticated users can create insights"
    ON public.insights FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- Author update/delete
CREATE POLICY "Users can update their own insights"
    ON public.insights FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own insights"
    ON public.insights FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- Explicit Permissions
GRANT SELECT ON public.insights TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.insights TO authenticated;
