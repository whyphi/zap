CREATE TABLE
	"applications" (
		"id" uuid PRIMARY KEY,
		"listing_id" uuid NOT NULL,
		"date_applied" timestamptz NOT NULL DEFAULT now (),
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

COMMENT ON TABLE "applications" IS 'events data are queried using the applications.email from the events_rush_attendees table';

ALTER TABLE "applications" ADD FOREIGN KEY ("listing_id") REFERENCES "listings" ("id") ON DELETE CASCADE;