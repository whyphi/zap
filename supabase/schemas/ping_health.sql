-- A tiny table used only for health checks and activity pings
CREATE TABLE
    IF NOT EXISTS ping_health (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
        last_ping timestamptz NOT NULL DEFAULT now ()
    );