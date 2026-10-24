-- Migration 007: Create Tactical Boards table & extend Terrace posts
CREATE TABLE IF NOT EXISTS public.tactical_boards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    author_name VARCHAR(100) NOT NULL DEFAULT 'Supporter',
    author_club_id VARCHAR(50) NOT NULL DEFAULT 'arsenal',
    title VARCHAR(150) NOT NULL,
    formation VARCHAR(20) NOT NULL DEFAULT '4-3-3',
    lineup JSONB NOT NULL DEFAULT '[]'::jsonb,
    annotations JSONB NOT NULL DEFAULT '[]'::jsonb,
    tactical_notes TEXT,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for club-based and author queries
CREATE INDEX IF NOT EXISTS idx_tactical_boards_club ON public.tactical_boards(author_club_id);
CREATE INDEX IF NOT EXISTS idx_tactical_boards_created ON public.tactical_boards(created_at DESC);

-- Enable RLS
ALTER TABLE public.tactical_boards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tactical boards are viewable by everyone" 
    ON public.tactical_boards FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create tactical boards" 
    ON public.tactical_boards FOR INSERT WITH CHECK (true);

-- Extend posts table to link to tactical boards
ALTER TABLE public.posts ADD COLUMN IF NOT EXISTS tactical_board_id UUID REFERENCES public.tactical_boards(id) ON DELETE SET NULL;
