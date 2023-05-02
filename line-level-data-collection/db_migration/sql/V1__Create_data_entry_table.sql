create table data_entry
(
    version         INT   not null,
    source          TEXT  not null,
    id              UUID  not null unique,
    language        TEXT  not null,
    label_type      TEXT,
    label           TEXT,
    user_id         TEXT  not null,
    device_id       TEXT  not null,
    strokes         jsonb not null,
    extra_metadata  jsonb,
    approval_status INT   not null,
    created_at      timestamp with time zone
);