CREATE TABLE
  "listings" (
    "id" uuid PRIMARY KEY,
    "title" text NOT NULL,
    "date_created" timestamptz NOT NULL DEFAULT now (),
    "deadline" timestamptz NOT NULL,
    "is_encrypted" boolean NOT NULL,
    "is_visible" boolean NOT NULL,
    "questions" jsonb
  );