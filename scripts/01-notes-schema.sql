-- Notes and Paragraphs Schema with Row Level Security
CREATE TABLE IF NOT EXISTS "notes" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "owner_id" text DEFAULT auth.uid() NOT NULL,
  "title" text DEFAULT 'untitled note' NOT NULL,
  "created_at" timestamp with time zone DEFAULT now(),
  "updated_at" timestamp with time zone DEFAULT now(),
  "shared" boolean DEFAULT false
);

ALTER TABLE "notes" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS "paragraphs" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "note_id" uuid,
  "content" text NOT NULL,
  "created_at" timestamp with time zone DEFAULT now()
);

ALTER TABLE "paragraphs" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "paragraphs" ADD CONSTRAINT "paragraphs_note_id_notes_id_fk" 
  FOREIGN KEY ("note_id") REFERENCES "public"."notes"("id") ON DELETE CASCADE ON UPDATE NO ACTION;

CREATE INDEX IF NOT EXISTS "owner_idx" ON "notes" USING btree ("owner_id");
CREATE INDEX IF NOT EXISTS "note_id_idx" ON "paragraphs" USING btree ("note_id");

-- RLS Policies for notes table
CREATE POLICY "notes_select_own" ON "notes" AS PERMISSIVE FOR SELECT TO "authenticated" 
  USING (auth.uid() = "owner_id");

CREATE POLICY "notes_insert_own" ON "notes" AS PERMISSIVE FOR INSERT TO "authenticated" 
  WITH CHECK (auth.uid() = "owner_id");

CREATE POLICY "notes_update_own" ON "notes" AS PERMISSIVE FOR UPDATE TO "authenticated" 
  USING (auth.uid() = "owner_id") WITH CHECK (auth.uid() = "owner_id");

CREATE POLICY "notes_delete_own" ON "notes" AS PERMISSIVE FOR DELETE TO "authenticated" 
  USING (auth.uid() = "owner_id");

CREATE POLICY "notes_select_shared" ON "notes" AS PERMISSIVE FOR SELECT TO "authenticated" 
  USING ("shared" = true);

-- RLS Policies for paragraphs table
CREATE POLICY "paragraphs_select_own" ON "paragraphs" AS PERMISSIVE FOR SELECT TO "authenticated" 
  USING ((SELECT "owner_id" FROM "notes" WHERE "notes"."id" = "paragraphs"."note_id") = auth.uid());

CREATE POLICY "paragraphs_insert_own" ON "paragraphs" AS PERMISSIVE FOR INSERT TO "authenticated" 
  WITH CHECK ((SELECT "owner_id" FROM "notes" WHERE "notes"."id" = "paragraphs"."note_id") = auth.uid());

CREATE POLICY "paragraphs_update_own" ON "paragraphs" AS PERMISSIVE FOR UPDATE TO "authenticated" 
  USING ((SELECT "owner_id" FROM "notes" WHERE "notes"."id" = "paragraphs"."note_id") = auth.uid())
  WITH CHECK ((SELECT "owner_id" FROM "notes" WHERE "notes"."id" = "paragraphs"."note_id") = auth.uid());

CREATE POLICY "paragraphs_delete_own" ON "paragraphs" AS PERMISSIVE FOR DELETE TO "authenticated" 
  USING ((SELECT "owner_id" FROM "notes" WHERE "notes"."id" = "paragraphs"."note_id") = auth.uid());

CREATE POLICY "paragraphs_select_shared" ON "paragraphs" AS PERMISSIVE FOR SELECT TO "authenticated" 
  USING ((SELECT "shared" FROM "notes" WHERE "notes"."id" = "paragraphs"."note_id") = true);

-- Audit logging table
CREATE TABLE IF NOT EXISTS "audit_logs" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "user_id" text,
  "action" text NOT NULL,
  "table_name" text NOT NULL,
  "record_id" text,
  "changes" jsonb,
  "created_at" timestamp with time zone DEFAULT now()
);

ALTER TABLE "audit_logs" ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS "audit_user_idx" ON "audit_logs" USING btree ("user_id");
CREATE INDEX IF NOT EXISTS "audit_action_idx" ON "audit_logs" USING btree ("action");
CREATE INDEX IF NOT EXISTS "audit_created_idx" ON "audit_logs" USING btree ("created_at");

CREATE POLICY "audit_select_own" ON "audit_logs" AS PERMISSIVE FOR SELECT TO "authenticated" 
  USING (auth.uid() = "user_id" OR auth.jwt() ->> 'role' = 'admin');
