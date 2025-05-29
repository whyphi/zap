-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2025-05-07T22:48:27.934Z

CREATE TABLE "listings" (
  "id" uuid PRIMARY KEY,
  "title" text NOT NULL,
  "date_created" timestamptz NOT NULL DEFAULT now(),
  "deadline" timestamptz NOT NULL,
  "is_encrypted" boolean NOT NULL,
  "is_visible" boolean NOT NULL,
  "questions" jsonb
);

CREATE TABLE "applications" (
  "id" uuid PRIMARY KEY,
  "listing_id" uuid NOT NULL,
  "date_applied" timestamptz NOT NULL DEFAULT now(),
  "email" text NOT NULL,
  "first_name" text NOT NULL,
  "last_name" text NOT NULL,
  "preferred_name" text,
  "gpa" float,
  "grad_month" text NOT NULL,
  "grad_year" integer NOT NULL,
  "has_gpa" boolean NOT NULL,
  "image" text NOT NULL,
  "website" text,
  "linkedin" text,
  "resume" text NOT NULL,
  "major" text NOT NULL,
  "minor" text,
  "phone" text NOT NULL,
  "colleges" jsonb,
  "responses" jsonb
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "name" text NOT NULL,
  "email" text NOT NULL,
  "class" text,
  "college" text,
  "family" text,
  "grad_year" integer,
  "is_eboard" boolean,
  "is_new_user" boolean,
  "major" text,
  "minor" text,
  "team" text
);

CREATE TABLE "roles" (
  "id" uuid PRIMARY KEY,
  "name" text UNIQUE
);

CREATE TABLE "user_roles" (
  "user_id" uuid NOT NULL,
  "role_id" uuid NOT NULL,
  PRIMARY KEY ("user_id", "role_id")
);

CREATE TABLE "event_timeframes_rush" (
  "id" uuid PRIMARY KEY,
  "name" text,
  "default_rush_category" boolean,
  "date_created" timestamptz DEFAULT now()
);

CREATE TABLE "events_rush" (
  "id" uuid PRIMARY KEY,
  "timeframe_id" uuid NOT NULL,
  "name" text,
  "code" text,
  "location" text,
  "date" timestamptz,
  "deadline" timestamptz,
  "event_cover_image" text,
  "event_cover_image_name" text,
  "event_cover_image_version" text,
  "date_created" timestamptz DEFAULT now(),
  "last_modified" timestamptz DEFAULT now(),
  "num_attendees" int
);

CREATE TABLE "events_rush_attendees" (
  "id" uuid PRIMARY KEY,
  "event_id" uuid NOT NULL,
  "name" text,
  "email" text,
  "checkin_time" timestamptz DEFAULT now()
);

CREATE TABLE "event_timeframes_member" (
  "id" uuid PRIMARY KEY,
  "name" text,
  "spreadsheet_id" text,
  "date_created" timestamptz DEFAULT now()
);

CREATE TABLE "events_member" (
  "id" uuid PRIMARY KEY,
  "timeframe_id" uuid NOT NULL,
  "name" text,
  "date_created" timestamptz DEFAULT now(),
  "speadsheet_tab" text,
  "speadsheet_col" text
);

CREATE TABLE "tags" (
  "id" uuid PRIMARY KEY,
  "name" text UNIQUE
);

CREATE TABLE "event_tags" (
  "events_member_id" uuid NOT NULL,
  "tag_id" uuid NOT NULL,
  PRIMARY KEY ("events_member_id", "tag_id")
);

CREATE TABLE "events_member_attendees" (
  "id" uuid PRIMARY KEY,
  "event_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "name" text,
  "checkin_time" timestamptz DEFAULT now()
);

COMMENT ON TABLE "applications" IS 'events data are queried using the applications.email from the events_rush_attendees table';

COMMENT ON TABLE "user_roles" IS 'Primary key can be composite';

COMMENT ON TABLE "event_tags" IS 'Primary key can be composite';

ALTER TABLE "applications" ADD FOREIGN KEY ("listing_id") REFERENCES "listings" ("id");

ALTER TABLE "user_roles" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "user_roles" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("id");

ALTER TABLE "events_rush" ADD FOREIGN KEY ("timeframe_id") REFERENCES "event_timeframes_rush" ("id");

ALTER TABLE "events_rush_attendees" ADD FOREIGN KEY ("event_id") REFERENCES "events_rush" ("id");

ALTER TABLE "events_member" ADD FOREIGN KEY ("timeframe_id") REFERENCES "event_timeframes_member" ("id");

ALTER TABLE "event_tags" ADD FOREIGN KEY ("events_member_id") REFERENCES "events_member" ("id");

ALTER TABLE "event_tags" ADD FOREIGN KEY ("tag_id") REFERENCES "tags" ("id");

ALTER TABLE "events_member_attendees" ADD FOREIGN KEY ("event_id") REFERENCES "events_member" ("id");

ALTER TABLE "events_member_attendees" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
