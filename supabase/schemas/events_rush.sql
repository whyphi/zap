CREATE TABLE
    event_timeframes_rush (
        id uuid PRIMARY KEY,
        listing_id uuid UNIQUE NOT NULL,
        name text NOT NULL,
        default_rush_timeframe boolean NOT NULL DEFAULT false,
        date_created timestamptz NOT NULL DEFAULT now (),
        FOREIGN KEY (listing_id) REFERENCES listings (id) ON DELETE CASCADE
    );

CREATE TABLE
    events_rush (
        id uuid PRIMARY KEY,
        timeframe_id uuid NOT NULL,
        name text NOT NULL,
        code text NOT NULL,
        location text NOT NULL,
        date timestamptz NOT NULL,
        deadline timestamptz NOT NULL,
        event_cover_image text NOT NULL,
        event_cover_image_name text NOT NULL,
        event_cover_image_version text NOT NULL,
        date_created timestamptz NOT NULL DEFAULT now (),
        last_modified timestamptz NOT NULL DEFAULT now (),
        FOREIGN KEY (timeframe_id) REFERENCES event_timeframes_rush (id) ON DELETE CASCADE
    );

CREATE TABLE
    events_rush_attendees (
        event_id uuid NOT NULL,
        rushee_id uuid NOT NULL,
        checkin_time timestamptz NOT NULL DEFAULT now (),
        PRIMARY KEY (event_id, rushee_id),
        FOREIGN KEY (event_id) REFERENCES events_rush (id) ON DELETE CASCADE,
        FOREIGN KEY (rushee_id) REFERENCES rushees (id) ON DELETE CASCADE
    );

COMMENT ON TABLE "event_timeframes_rush" IS 'Unique listing id enforces One-to-One relationsip';