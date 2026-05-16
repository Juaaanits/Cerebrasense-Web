/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_SUPABASE_URL: string;
  readonly PUBLIC_SUPABASE_PUBLISHABLE_KEY: string;
  readonly SUPABASE_SECRET_KEY: string;
  readonly MODEL_API_URL: string;
  readonly MODEL_API_TOKEN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
