import type { APIRoute } from "astro";
import { createSupabaseAdmin } from "@/lib/supabase/server";

export const prerender = false;

export const GET: APIRoute = async () => {
  const supabase = createSupabaseAdmin();

  const { data, error } = await supabase
    .from("tumor_analyses")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }

  return Response.json({ analyses: data });
};
