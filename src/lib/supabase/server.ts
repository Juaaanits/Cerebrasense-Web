import { createClient } from "@supabase/supabase-js";

export function createSupabaseAdmin() {
  const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
  const supabaseSecretKey = import.meta.env.SUPABASE_SECRET_KEY;

  if (!supabaseUrl || !supabaseSecretKey) {
    throw new Error("Missing Supabase server environment variables.");
  }

  return createClient(
    supabaseUrl,
    supabaseSecretKey,
    {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    },
  );
}
