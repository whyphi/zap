create table "public"."event_timeframes_rush" (
    "id" uuid not null,
    "listing_id" uuid not null,
    "name" text not null,
    "default_rush_timeframe" boolean not null default false,
    "date_created" timestamp with time zone not null default now()
);


create table "public"."events_rush" (
    "id" uuid not null,
    "timeframe_id" uuid not null,
    "name" text not null,
    "code" text not null,
    "location" text not null,
    "date" timestamp with time zone not null,
    "deadline" timestamp with time zone not null,
    "event_cover_image" text not null,
    "event_cover_image_name" text not null,
    "event_cover_image_version" text not null,
    "date_created" timestamp with time zone not null default now(),
    "last_modified" timestamp with time zone not null default now()
);


create table "public"."events_rush_attendees" (
    "event_id" uuid not null,
    "rushee_id" uuid not null,
    "checkin_time" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX event_timeframes_rush_listing_id_key ON public.event_timeframes_rush USING btree (listing_id);

CREATE UNIQUE INDEX event_timeframes_rush_pkey ON public.event_timeframes_rush USING btree (id);

CREATE UNIQUE INDEX events_rush_attendees_pkey ON public.events_rush_attendees USING btree (event_id, rushee_id);

CREATE UNIQUE INDEX events_rush_pkey ON public.events_rush USING btree (id);

alter table "public"."event_timeframes_rush" add constraint "event_timeframes_rush_pkey" PRIMARY KEY using index "event_timeframes_rush_pkey";

alter table "public"."events_rush" add constraint "events_rush_pkey" PRIMARY KEY using index "events_rush_pkey";

alter table "public"."events_rush_attendees" add constraint "events_rush_attendees_pkey" PRIMARY KEY using index "events_rush_attendees_pkey";

alter table "public"."event_timeframes_rush" add constraint "event_timeframes_rush_listing_id_fkey" FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE not valid;

alter table "public"."event_timeframes_rush" validate constraint "event_timeframes_rush_listing_id_fkey";

alter table "public"."event_timeframes_rush" add constraint "event_timeframes_rush_listing_id_key" UNIQUE using index "event_timeframes_rush_listing_id_key";

alter table "public"."events_rush" add constraint "events_rush_timeframe_id_fkey" FOREIGN KEY (timeframe_id) REFERENCES event_timeframes_rush(id) ON DELETE CASCADE not valid;

alter table "public"."events_rush" validate constraint "events_rush_timeframe_id_fkey";

alter table "public"."events_rush_attendees" add constraint "events_rush_attendees_event_id_fkey" FOREIGN KEY (event_id) REFERENCES events_rush(id) ON DELETE CASCADE not valid;

alter table "public"."events_rush_attendees" validate constraint "events_rush_attendees_event_id_fkey";

alter table "public"."events_rush_attendees" add constraint "events_rush_attendees_rushee_id_fkey" FOREIGN KEY (rushee_id) REFERENCES rushees(id) ON DELETE CASCADE not valid;

alter table "public"."events_rush_attendees" validate constraint "events_rush_attendees_rushee_id_fkey";

grant delete on table "public"."event_timeframes_rush" to "anon";

grant insert on table "public"."event_timeframes_rush" to "anon";

grant references on table "public"."event_timeframes_rush" to "anon";

grant select on table "public"."event_timeframes_rush" to "anon";

grant trigger on table "public"."event_timeframes_rush" to "anon";

grant truncate on table "public"."event_timeframes_rush" to "anon";

grant update on table "public"."event_timeframes_rush" to "anon";

grant delete on table "public"."event_timeframes_rush" to "authenticated";

grant insert on table "public"."event_timeframes_rush" to "authenticated";

grant references on table "public"."event_timeframes_rush" to "authenticated";

grant select on table "public"."event_timeframes_rush" to "authenticated";

grant trigger on table "public"."event_timeframes_rush" to "authenticated";

grant truncate on table "public"."event_timeframes_rush" to "authenticated";

grant update on table "public"."event_timeframes_rush" to "authenticated";

grant delete on table "public"."event_timeframes_rush" to "service_role";

grant insert on table "public"."event_timeframes_rush" to "service_role";

grant references on table "public"."event_timeframes_rush" to "service_role";

grant select on table "public"."event_timeframes_rush" to "service_role";

grant trigger on table "public"."event_timeframes_rush" to "service_role";

grant truncate on table "public"."event_timeframes_rush" to "service_role";

grant update on table "public"."event_timeframes_rush" to "service_role";

grant delete on table "public"."events_rush" to "anon";

grant insert on table "public"."events_rush" to "anon";

grant references on table "public"."events_rush" to "anon";

grant select on table "public"."events_rush" to "anon";

grant trigger on table "public"."events_rush" to "anon";

grant truncate on table "public"."events_rush" to "anon";

grant update on table "public"."events_rush" to "anon";

grant delete on table "public"."events_rush" to "authenticated";

grant insert on table "public"."events_rush" to "authenticated";

grant references on table "public"."events_rush" to "authenticated";

grant select on table "public"."events_rush" to "authenticated";

grant trigger on table "public"."events_rush" to "authenticated";

grant truncate on table "public"."events_rush" to "authenticated";

grant update on table "public"."events_rush" to "authenticated";

grant delete on table "public"."events_rush" to "service_role";

grant insert on table "public"."events_rush" to "service_role";

grant references on table "public"."events_rush" to "service_role";

grant select on table "public"."events_rush" to "service_role";

grant trigger on table "public"."events_rush" to "service_role";

grant truncate on table "public"."events_rush" to "service_role";

grant update on table "public"."events_rush" to "service_role";

grant delete on table "public"."events_rush_attendees" to "anon";

grant insert on table "public"."events_rush_attendees" to "anon";

grant references on table "public"."events_rush_attendees" to "anon";

grant select on table "public"."events_rush_attendees" to "anon";

grant trigger on table "public"."events_rush_attendees" to "anon";

grant truncate on table "public"."events_rush_attendees" to "anon";

grant update on table "public"."events_rush_attendees" to "anon";

grant delete on table "public"."events_rush_attendees" to "authenticated";

grant insert on table "public"."events_rush_attendees" to "authenticated";

grant references on table "public"."events_rush_attendees" to "authenticated";

grant select on table "public"."events_rush_attendees" to "authenticated";

grant trigger on table "public"."events_rush_attendees" to "authenticated";

grant truncate on table "public"."events_rush_attendees" to "authenticated";

grant update on table "public"."events_rush_attendees" to "authenticated";

grant delete on table "public"."events_rush_attendees" to "service_role";

grant insert on table "public"."events_rush_attendees" to "service_role";

grant references on table "public"."events_rush_attendees" to "service_role";

grant select on table "public"."events_rush_attendees" to "service_role";

grant trigger on table "public"."events_rush_attendees" to "service_role";

grant truncate on table "public"."events_rush_attendees" to "service_role";

grant update on table "public"."events_rush_attendees" to "service_role";


