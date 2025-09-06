CREATE TABLE
    event_timeframes_member (
        id uuid PRIMARY KEY,
        name text NOT NULL,
        spreadsheet_id text NOT NULL,
        date_created timestamptz NOT NULL DEFAULT now ()
    );

CREATE TABLE
    events_member (
        id uuid PRIMARY KEY,
        timeframe_id uuid NOT NULL,
        name text NOT NULL,
        code text NOT NULL,
        date_created timestamptz NOT NULL DEFAULT now (),
        spreadsheet_tab text NOT NULL,
        spreadsheet_col text NOT NULL,
        FOREIGN KEY (timeframe_id) REFERENCES event_timeframes_member (id) ON DELETE CASCADE
    );

CREATE TABLE
    tags (id uuid PRIMARY KEY, name text NOT NULL UNIQUE);

CREATE TABLE
    event_tags (
        events_member_id uuid NOT NULL,
        tag_id uuid NOT NULL,
        PRIMARY KEY (events_member_id, tag_id),
        FOREIGN KEY (events_member_id) REFERENCES events_member (id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    );

CREATE TABLE
    events_member_attendees (
        event_id uuid NOT NULL,
        user_id uuid NOT NULL,
        checkin_time timestamptz NOT NULL DEFAULT now (),
        PRIMARY KEY (event_id, user_id),
        FOREIGN KEY (event_id) REFERENCES events_member (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );