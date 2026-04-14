-- Migration 005: cache for HyDE-generated descriptions

create table if not exists hyde_cache (
  query_normalized text primary key,
  hyde_description text not null,
  created_at       timestamptz default now()
);
