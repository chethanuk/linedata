DROP INDEX idx_query_count_text;
create index idx_query_count_text on data_entry(language, label, approval_status)