-- Migration 002: full-text search vector + hybrid search function

-- 1. Add search_vector column
alter table books add column if not exists search_vector tsvector;

-- 2. Backfill existing rows
update books
set search_vector = to_tsvector('simple',
  coalesce(title, '')        || ' ' ||
  coalesce(author, '')       || ' ' ||
  coalesce(description_es, '') || ' ' ||
  coalesce(description, ''));

-- 3. GIN index for fast full-text lookup
create index if not exists books_search_vector_idx on books using gin(search_vector);

-- 4. Trigger to keep search_vector up to date on insert/update
create or replace function books_search_vector_update() returns trigger as $$
begin
  new.search_vector := to_tsvector('simple',
    coalesce(new.title, '')          || ' ' ||
    coalesce(new.author, '')         || ' ' ||
    coalesce(new.description_es, '') || ' ' ||
    coalesce(new.description, ''));
  return new;
end;
$$ language plpgsql;

drop trigger if exists books_search_vector_trigger on books;
create trigger books_search_vector_trigger
  before insert or update on books
  for each row execute function books_search_vector_update();

-- 5. Hybrid search: semantic (HyDE embedding) + full-text, combined with RRF
create or replace function search_books_hybrid(
  query_embedding  vector(1024),
  query_text       text,
  match_count      int   default 8,
  semantic_weight  float default 0.7,
  fulltext_weight  float default 0.3,
  rrf_k            int   default 60
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
  with semantic_ranked as (
    select id,
           row_number() over (order by embedding <=> query_embedding) as rank
    from books
    where embedding is not null
    order by embedding <=> query_embedding
    limit 60
  ),
  fulltext_ranked as (
    select b.id,
           row_number() over (order by ts_rank_cd(b.search_vector, q) desc) as rank
    from books b,
         websearch_to_tsquery('simple', query_text) q
    where b.search_vector @@ q
    order by ts_rank_cd(b.search_vector, q) desc
    limit 60
  ),
  rrf_scores as (
    select
      coalesce(s.id, f.id) as id,
      coalesce(semantic_weight / (rrf_k + s.rank), 0.0) +
      coalesce(fulltext_weight / (rrf_k + f.rank), 0.0) as score
    from semantic_ranked s
    full outer join fulltext_ranked f on s.id = f.id
  )
  select
    b.id, b.ol_key, b.title, b.author, b.year,
    b.description, b.description_es, b.cover_url, b.extras,
    r.score as similarity
  from rrf_scores r
  join books b on b.id = r.id
  order by r.score desc
  limit match_count;
$$;
