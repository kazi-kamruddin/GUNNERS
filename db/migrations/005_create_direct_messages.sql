-- 005_create_direct_messages.sql
-- Migration: Realtime 1-on-1 Direct Messaging (The Dressing Room)

-- 1. Create Conversations table
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 2. Create Conversation Members table (for 1-on-1 private debates)
CREATE TABLE IF NOT EXISTS public.conversation_members (
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    joined_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    last_read_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    PRIMARY KEY (conversation_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_conv_members_user ON public.conversation_members(user_id);

-- 3. Create Direct Messages table
CREATE TABLE IF NOT EXISTS public.direct_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE NOT NULL,
    sender_id UUID REFERENCES auth.users(id) ON DELETE SET NULL NOT NULL,
    sender_name TEXT NOT NULL DEFAULT 'Supporter',
    sender_club_id TEXT REFERENCES public.clubs(id) DEFAULT 'arsenal',
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_direct_messages_conv ON public.direct_messages(conversation_id, created_at ASC);

-- 4. Row Level Security (RLS)
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.direct_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view conversations they belong to" ON public.conversations;
DROP POLICY IF EXISTS "Authenticated users can create conversations" ON public.conversations;

DROP POLICY IF EXISTS "Users can view members of their conversations" ON public.conversation_members;
DROP POLICY IF EXISTS "Users can join conversations" ON public.conversation_members;

DROP POLICY IF EXISTS "Users can view messages in their conversations" ON public.direct_messages;
DROP POLICY IF EXISTS "Users can insert messages into their conversations" ON public.direct_messages;

-- Conversations RLS
CREATE POLICY "Users can view conversations they belong to"
    ON public.conversations FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.conversation_members
            WHERE conversation_members.conversation_id = conversations.id
            AND conversation_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Authenticated users can create conversations"
    ON public.conversations FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Conversation Members RLS
CREATE POLICY "Users can view members of their conversations"
    ON public.conversation_members FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.conversation_members cm
            WHERE cm.conversation_id = conversation_members.conversation_id
            AND cm.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can join conversations"
    ON public.conversation_members FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Direct Messages RLS
CREATE POLICY "Users can view messages in their conversations"
    ON public.direct_messages FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.conversation_members
            WHERE conversation_members.conversation_id = direct_messages.conversation_id
            AND conversation_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages into their conversations"
    ON public.direct_messages FOR INSERT
    TO authenticated
    WITH CHECK (
        auth.uid() = sender_id AND
        EXISTS (
            SELECT 1 FROM public.conversation_members
            WHERE conversation_members.conversation_id = direct_messages.conversation_id
            AND conversation_members.user_id = auth.uid()
        )
    );

-- Enable Supabase Realtime publication
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND schemaname = 'public' 
        AND tablename = 'direct_messages'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.direct_messages;
    END IF;
EXCEPTION
    WHEN OTHERS THEN NULL;
END $$;

-- Permissions
GRANT SELECT, INSERT ON public.conversations TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.conversation_members TO authenticated;
GRANT SELECT, INSERT ON public.direct_messages TO authenticated;
