-- Run once in your Supabase project's SQL editor.
create table if not exists public.paperloom_records (
  user_id uuid not null references auth.users(id) on delete cascade,
  id text not null,
  kind text not null check (kind in ('paper','concept')),
  body jsonb not null,
  modified double precision not null,
  primary key (user_id,id)
);
alter table public.paperloom_records enable row level security;
drop policy if exists "Owner only" on public.paperloom_records;
create policy "Owner only" on public.paperloom_records for all to authenticated
using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
grant select,insert,update,delete on public.paperloom_records to authenticated;
-- Atomic upsert: stale concurrent clients cannot overwrite newer records.
create or replace function public.paperloom_put(records jsonb) returns void
language plpgsql security invoker set search_path=public as $$
begin
 insert into public.paperloom_records(user_id,id,kind,body,modified)
 select auth.uid(),x.id,x.kind,x.body,x.modified
 from jsonb_to_recordset(records) as x(id text,kind text,body jsonb,modified double precision)
 on conflict(user_id,id) do update set body=excluded.body,modified=excluded.modified
 where excluded.modified > paperloom_records.modified;
end; $$;
revoke all on function public.paperloom_put(jsonb) from public;
grant execute on function public.paperloom_put(jsonb) to authenticated;
insert into storage.buckets(id,name,public) values('paperloom','paperloom',false) on conflict(id) do nothing;
drop policy if exists "Paperloom PDFs" on storage.objects;
create policy "Paperloom PDFs" on storage.objects for all to authenticated
using(bucket_id='paperloom' and (storage.foldername(name))[1]=(select auth.uid())::text)
with check(bucket_id='paperloom' and (storage.foldername(name))[1]=(select auth.uid())::text);
