-- Migration 004: return cosine similarity for display, keep RRF for ranking

drop function if exists search_books_hybrid(vector, text, integer, double precision, double precision, integer);

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
  similarity     float,
  match_type     text
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
      coalesce(fulltext_weight / (rrf_k + f.rank), 0.0) as rrf_score,
      case
        when s.id is not null and f.id is not null then 'hybrid'
        when s.id is not null                      then 'semantic'
        else                                            'fulltext'
      end as match_type
    from semantic_ranked s
    full outer join fulltext_ranked f on s.id = f.id
  )
  select
    b.id, b.ol_key, b.title, b.author, b.year,
    b.description, b.description_es, b.cover_url, b.extras,
    -- similitud coseno real para mostrar al usuario (RRF solo para ordenar)
    round((1 - (b.embedding <=> query_embedding))::numeric, 4)::float as similarity,
    r.match_type
  from rrf_scores r
  join books b on b.id = r.id
  order by r.rrf_score desc
  limit match_count;
$$;
