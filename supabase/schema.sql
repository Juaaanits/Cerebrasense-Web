create table public.tumor_analyses (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  user_id uuid references auth.users(id),
  image_path text not null,
  original_filename text not null,

  predicted_label text not null,
  confidence numeric not null,
  probabilities jsonb not null,

  model_version text,
  status text not null default 'completed',
  error_message text
);

alter table public.tumor_analyses enable row level security;

insert into storage.buckets (id, name, public)
values ('brain-scans', 'brain-scans', false)
on conflict (id) do nothing;


create policy "Users can read own analyses"
on public.tumor_analyses
for select
to authenticated
using (auth.uid() = user_id);

create policy "Users can insert own analyses"
on public.tumor_analyses
for insert
to authenticated
with check (auth.uid() = user_id);
