-- 1. Habilitar pgvector
create extension if not exists vector;

-- 2. Tabla de libros
create table if not exists books (
  id          bigint primary key generated always as identity,
  ol_key      text unique not null,
  title       text not null,
  author      text,
  year        int,
  description text not null,
  description_es text,
  cover_url   text,
  embedding   vector(1024),
  created_at  timestamptz default now()
);

-- 3. ├ìndice para b├║squeda coseno
create index if not exists books_embedding_idx
  on books using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- 4. Funci├│n de b├║squeda sem├íntica
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
  similarity     float
)
language sql stable as $$
  select
    b.id, b.ol_key, b.title, b.author, b.year, b.description, b.description_es, b.cover_url,
    1 - (b.embedding <=> query_embedding) as similarity
  from books b
  where b.embedding is not null
  order by b.embedding <=> query_embedding
  limit match_count;
$$;
