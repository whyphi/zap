CREATE TABLE
    users (
        id uuid PRIMARY KEY,
        name text NOT NULL,
        email text NOT NULL, -- TODO: make email unique
        class text,
        college text,
        family text,
        grad_year integer,
        is_eboard boolean NOT NULL,
        is_new_user boolean NOT NULL,
        major text,
        minor text,
        team text
    );

CREATE TABLE
    roles (
        id uuid PRIMARY KEY,
        name text UNIQUE NOT NULL,
        CONSTRAINT allowed_roles CHECK (
            name IN ('admin', 'member', 'eboard', 'recruitment')
        )
    );

CREATE TABLE
    user_roles (
        user_id uuid NOT NULL,
        role_id uuid NOT NULL,
        assigned_at timestamptz NOT NULL DEFAULT now (),
        PRIMARY KEY (user_id, role_id),
        CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
    );