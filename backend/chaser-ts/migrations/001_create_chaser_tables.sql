CREATE TABLE IF NOT EXISTS chase_cases (
  id TEXT PRIMARY KEY,
  company TEXT NOT NULL,
  contact TEXT NOT NULL,
  email TEXT NOT NULL,
  rm TEXT NOT NULL,
  chase_rounds INTEGER NOT NULL DEFAULT 0 CHECK (chase_rounds >= 0),
  last_request_at TIMESTAMPTZ,
  draft TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS chase_documents (
  case_id TEXT NOT NULL REFERENCES chase_cases(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  requested_at TIMESTAMPTZ,
  received_at TIMESTAMPTZ,
  PRIMARY KEY (case_id, name)
);

CREATE TABLE IF NOT EXISTS chase_request_batches (
  id BIGSERIAL PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES chase_cases(id) ON DELETE CASCADE,
  sent_at TIMESTAMPTZ NOT NULL,
  document_names JSONB NOT NULL,
  response_at TIMESTAMPTZ
);
