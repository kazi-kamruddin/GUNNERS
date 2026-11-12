-- 009_realtime_and_rls_fixes.sql
-- Migration: Enable Supabase Realtime on notifications, add missing RLS policies
-- on notifications / players / predictions (compatible with varchar & uuid user_id),
-- and restrict SECURITY DEFINER trigger execution away from anon/authenticated RPCs.

-- =====================================================================
-- 1. Enable Supabase Realtime on public.notifications
-- =====================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime')
       AND NOT EXISTS (
           SELECT 1
           FROM pg_publication_tables
           WHERE pubname = 'supabase_realtime'
             AND schemaname = 'public'
             AND tablename = 'notifications'
       ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.notifications;
    END IF;
END $$;

-- =====================================================================
-- 2. RLS Policies for public.notifications (required for Realtime delivery)
-- =====================================================================
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own notifications" ON public.notifications;
CREATE POLICY "Users can view own notifications"
    ON public.notifications FOR SELECT
    TO authenticated
    USING (user_id::text = (select auth.uid())::text);

DROP POLICY IF EXISTS "Users can update own notifications" ON public.notifications;
CREATE POLICY "Users can update own notifications"
    ON public.notifications FOR UPDATE
    TO authenticated
    USING (user_id::text = (select auth.uid())::text)
    WITH CHECK (user_id::text = (select auth.uid())::text);

GRANT SELECT, UPDATE ON public.notifications TO authenticated;

-- =====================================================================
-- 3. RLS Policies for public.players & public.predictions
-- =====================================================================
ALTER TABLE public.players ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can view players" ON public.players;
CREATE POLICY "Public can view players"
    ON public.players FOR SELECT
    TO public
    USING (true);

DROP POLICY IF EXISTS "Public can view predictions" ON public.predictions;
DROP POLICY IF EXISTS "Users can view predictions" ON public.predictions;
CREATE POLICY "Public can view predictions"
    ON public.predictions FOR SELECT
    TO public
    USING (true);

DROP POLICY IF EXISTS "Users can insert own predictions" ON public.predictions;
CREATE POLICY "Users can insert own predictions"
    ON public.predictions FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) IS NOT NULL AND user_id::text = (select auth.uid())::text);

DROP POLICY IF EXISTS "Users can update own predictions" ON public.predictions;
CREATE POLICY "Users can update own predictions"
    ON public.predictions FOR UPDATE
    TO authenticated
    USING (user_id::text = (select auth.uid())::text)
    WITH CHECK (user_id::text = (select auth.uid())::text);

GRANT SELECT ON public.players, public.predictions TO anon, authenticated;
GRANT INSERT, UPDATE ON public.predictions TO authenticated;

-- =====================================================================
-- 4. Revoke direct RPC access to handle_new_user() trigger function
-- =====================================================================
DO $$
BEGIN
    IF to_regprocedure('public.handle_new_user()') IS NOT NULL THEN
        REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC;
        REVOKE ALL ON FUNCTION public.handle_new_user() FROM anon, authenticated;
        GRANT EXECUTE ON FUNCTION public.handle_new_user() TO postgres, supabase_auth_admin, service_role;
    END IF;
END $$;
