create table data_entry_update
(
    id            uuid  not null primary key,
    event_content jsonb not null,
    language      TEXT  not null,
    created_at    timestamp with time zone
);

create index idx_query_updates_by_language on data_entry (language, created_at)