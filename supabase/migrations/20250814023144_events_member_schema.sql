create table "public"."event_tags" (
    "events_member_id" uuid not null,
    "tag_id" uuid not null
);


create table "public"."event_timeframes_member" (
    "id" uuid not null,
    "name" text not null,
    "spreadsheet_id" text not null,
    "date_created" timestamp with time zone not null default now()
);


create table "public"."events_member" (
    "id" uuid not null,
    "timeframe_id" uuid not null,
    "name" text not null,
    "code" text not null,
    "date_created" timestamp with time zone not null default now(),
    "spreadsheet_tab" text not null,
    "spreadsheet_col" text not null
);


create table "public"."events_member_attendees" (
    "event_id" uuid not null,
    "user_id" uuid not null,
    "checkin_time" timestamp with time zone not null default now()
);


create table "public"."tags" (
    "id" uuid not null,
    "name" text not null
);


CREATE UNIQUE INDEX event_tags_pkey ON public.event_tags USING btree (events_member_id, tag_id);

CREATE UNIQUE INDEX event_timeframes_member_pkey ON public.event_timeframes_member USING btree (id);

CREATE UNIQUE INDEX events_member_attendees_pkey ON public.events_member_attendees USING btree (event_id, user_id);

CREATE UNIQUE INDEX events_member_pkey ON public.events_member USING btree (id);

CREATE UNIQUE INDEX tags_name_key ON public.tags USING btree (name);

CREATE UNIQUE INDEX tags_pkey ON public.tags USING btree (id);

alter table "public"."event_tags" add constraint "event_tags_pkey" PRIMARY KEY using index "event_tags_pkey";

alter table "public"."event_timeframes_member" add constraint "event_timeframes_member_pkey" PRIMARY KEY using index "event_timeframes_member_pkey";

alter table "public"."events_member" add constraint "events_member_pkey" PRIMARY KEY using index "events_member_pkey";

alter table "public"."events_member_attendees" add constraint "events_member_attendees_pkey" PRIMARY KEY using index "events_member_attendees_pkey";

alter table "public"."tags" add constraint "tags_pkey" PRIMARY KEY using index "tags_pkey";

alter table "public"."event_tags" add constraint "event_tags_events_member_id_fkey" FOREIGN KEY (events_member_id) REFERENCES events_member(id) ON DELETE CASCADE not valid;

alter table "public"."event_tags" validate constraint "event_tags_events_member_id_fkey";

alter table "public"."event_tags" add constraint "event_tags_tag_id_fkey" FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE not valid;

alter table "public"."event_tags" validate constraint "event_tags_tag_id_fkey";

alter table "public"."events_member" add constraint "events_member_timeframe_id_fkey" FOREIGN KEY (timeframe_id) REFERENCES event_timeframes_member(id) ON DELETE CASCADE not valid;

alter table "public"."events_member" validate constraint "events_member_timeframe_id_fkey";

alter table "public"."events_member_attendees" add constraint "events_member_attendees_event_id_fkey" FOREIGN KEY (event_id) REFERENCES events_member(id) ON DELETE CASCADE not valid;

alter table "public"."events_member_attendees" validate constraint "events_member_attendees_event_id_fkey";

alter table "public"."events_member_attendees" add constraint "events_member_attendees_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE not valid;

alter table "public"."events_member_attendees" validate constraint "events_member_attendees_user_id_fkey";

alter table "public"."tags" add constraint "tags_name_key" UNIQUE using index "tags_name_key";

grant delete on table "public"."event_tags" to "anon";

grant insert on table "public"."event_tags" to "anon";

grant references on table "public"."event_tags" to "anon";

grant select on table "public"."event_tags" to "anon";

grant trigger on table "public"."event_tags" to "anon";

grant truncate on table "public"."event_tags" to "anon";

grant update on table "public"."event_tags" to "anon";

grant delete on table "public"."event_tags" to "authenticated";

grant insert on table "public"."event_tags" to "authenticated";

grant references on table "public"."event_tags" to "authenticated";

grant select on table "public"."event_tags" to "authenticated";

grant trigger on table "public"."event_tags" to "authenticated";

grant truncate on table "public"."event_tags" to "authenticated";

grant update on table "public"."event_tags" to "authenticated";

grant delete on table "public"."event_tags" to "service_role";

grant insert on table "public"."event_tags" to "service_role";

grant references on table "public"."event_tags" to "service_role";

grant select on table "public"."event_tags" to "service_role";

grant trigger on table "public"."event_tags" to "service_role";

grant truncate on table "public"."event_tags" to "service_role";

grant update on table "public"."event_tags" to "service_role";

grant delete on table "public"."event_timeframes_member" to "anon";

grant insert on table "public"."event_timeframes_member" to "anon";

grant references on table "public"."event_timeframes_member" to "anon";

grant select on table "public"."event_timeframes_member" to "anon";

grant trigger on table "public"."event_timeframes_member" to "anon";

grant truncate on table "public"."event_timeframes_member" to "anon";

grant update on table "public"."event_timeframes_member" to "anon";

grant delete on table "public"."event_timeframes_member" to "authenticated";

grant insert on table "public"."event_timeframes_member" to "authenticated";

grant references on table "public"."event_timeframes_member" to "authenticated";

grant select on table "public"."event_timeframes_member" to "authenticated";

grant trigger on table "public"."event_timeframes_member" to "authenticated";

grant truncate on table "public"."event_timeframes_member" to "authenticated";

grant update on table "public"."event_timeframes_member" to "authenticated";

grant delete on table "public"."event_timeframes_member" to "service_role";

grant insert on table "public"."event_timeframes_member" to "service_role";

grant references on table "public"."event_timeframes_member" to "service_role";

grant select on table "public"."event_timeframes_member" to "service_role";

grant trigger on table "public"."event_timeframes_member" to "service_role";

grant truncate on table "public"."event_timeframes_member" to "service_role";

grant update on table "public"."event_timeframes_member" to "service_role";

grant delete on table "public"."events_member" to "anon";

grant insert on table "public"."events_member" to "anon";

grant references on table "public"."events_member" to "anon";

grant select on table "public"."events_member" to "anon";

grant trigger on table "public"."events_member" to "anon";

grant truncate on table "public"."events_member" to "anon";

grant update on table "public"."events_member" to "anon";

grant delete on table "public"."events_member" to "authenticated";

grant insert on table "public"."events_member" to "authenticated";

grant references on table "public"."events_member" to "authenticated";

grant select on table "public"."events_member" to "authenticated";

grant trigger on table "public"."events_member" to "authenticated";

grant truncate on table "public"."events_member" to "authenticated";

grant update on table "public"."events_member" to "authenticated";

grant delete on table "public"."events_member" to "service_role";

grant insert on table "public"."events_member" to "service_role";

grant references on table "public"."events_member" to "service_role";

grant select on table "public"."events_member" to "service_role";

grant trigger on table "public"."events_member" to "service_role";

grant truncate on table "public"."events_member" to "service_role";

grant update on table "public"."events_member" to "service_role";

grant delete on table "public"."events_member_attendees" to "anon";

grant insert on table "public"."events_member_attendees" to "anon";

grant references on table "public"."events_member_attendees" to "anon";

grant select on table "public"."events_member_attendees" to "anon";

grant trigger on table "public"."events_member_attendees" to "anon";

grant truncate on table "public"."events_member_attendees" to "anon";

grant update on table "public"."events_member_attendees" to "anon";

grant delete on table "public"."events_member_attendees" to "authenticated";

grant insert on table "public"."events_member_attendees" to "authenticated";

grant references on table "public"."events_member_attendees" to "authenticated";

grant select on table "public"."events_member_attendees" to "authenticated";

grant trigger on table "public"."events_member_attendees" to "authenticated";

grant truncate on table "public"."events_member_attendees" to "authenticated";

grant update on table "public"."events_member_attendees" to "authenticated";

grant delete on table "public"."events_member_attendees" to "service_role";

grant insert on table "public"."events_member_attendees" to "service_role";

grant references on table "public"."events_member_attendees" to "service_role";

grant select on table "public"."events_member_attendees" to "service_role";

grant trigger on table "public"."events_member_attendees" to "service_role";

grant truncate on table "public"."events_member_attendees" to "service_role";

grant update on table "public"."events_member_attendees" to "service_role";

grant delete on table "public"."tags" to "anon";

grant insert on table "public"."tags" to "anon";

grant references on table "public"."tags" to "anon";

grant select on table "public"."tags" to "anon";

grant trigger on table "public"."tags" to "anon";

grant truncate on table "public"."tags" to "anon";

grant update on table "public"."tags" to "anon";

grant delete on table "public"."tags" to "authenticated";

grant insert on table "public"."tags" to "authenticated";

grant references on table "public"."tags" to "authenticated";

grant select on table "public"."tags" to "authenticated";

grant trigger on table "public"."tags" to "authenticated";

grant truncate on table "public"."tags" to "authenticated";

grant update on table "public"."tags" to "authenticated";

grant delete on table "public"."tags" to "service_role";

grant insert on table "public"."tags" to "service_role";

grant references on table "public"."tags" to "service_role";

grant select on table "public"."tags" to "service_role";

grant trigger on table "public"."tags" to "service_role";

grant truncate on table "public"."tags" to "service_role";

grant update on table "public"."tags" to "service_role";


