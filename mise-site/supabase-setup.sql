create table if not exists public.mise_user_data (
  id uuid primary key references auth.users (id) on delete cascade,
  data jsonb not null default '{"recipes": [], "categories": []}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.mise_user_data enable row level security;
revoke all on public.mise_user_data from anon;
grant select, insert, update on public.mise_user_data to authenticated;

drop policy if exists "Users can read their own recipe library" on public.mise_user_data;
create policy "Users can read their own recipe library"
  on public.mise_user_data for select to authenticated
  using (auth.uid() is not null and auth.uid() = id);

drop policy if exists "Users can create their own recipe library" on public.mise_user_data;
create policy "Users can create their own recipe library"
  on public.mise_user_data for insert to authenticated
  with check (auth.uid() is not null and auth.uid() = id);

drop policy if exists "Users can update their own recipe library" on public.mise_user_data;
create policy "Users can update their own recipe library"
  on public.mise_user_data for update to authenticated
  using (auth.uid() is not null and auth.uid() = id)
  with check (auth.uid() is not null and auth.uid() = id);
