-- Migration 001: add extras jsonb column to books
alter table books add column if not exists extras jsonb;

-- Drop old function to allow changing return type
drop function if exists search_books(vector, integer);

-- Update search_books function to return extras
create or replace function search_books(
  query_embedding vector(1024),
  match_count     int default 5
)
returns table (
  id             bigint,
  ol_key         text,
  title          text,
  author         text,
  year           int,
  description    text,
  description_es text,
  cover_url      text,
  extras         jsonb,
  similarity     float
)
language sql stable as $$
  select
    b.id, b.ol_key, b.title, b.author, b.year, b.description, b.description_es, b.cover_url, b.extras,
    1 - (b.embedding <=> query_embedding) as similarity
  from books b
  where b.embedding is not null
  order by b.embedding <=> query_embedding
  limit match_count;
$$;
