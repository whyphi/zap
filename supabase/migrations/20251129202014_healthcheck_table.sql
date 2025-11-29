drop function if exists "public"."healthcheck"();

create table "public"."ping_health" (
    "id" uuid not null default gen_random_uuid(),
    "last_ping" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX ping_health_pkey ON public.ping_health USING btree (id);

alter table "public"."ping_health" add constraint "ping_health_pkey" PRIMARY KEY using index "ping_health_pkey";

grant delete on table "public"."ping_health" to "anon";

grant insert on table "public"."ping_health" to "anon";

grant references on table "public"."ping_health" to "anon";

grant select on table "public"."ping_health" to "anon";

grant trigger on table "public"."ping_health" to "anon";

grant truncate on table "public"."ping_health" to "anon";

grant update on table "public"."ping_health" to "anon";

grant delete on table "public"."ping_health" to "authenticated";

grant insert on table "public"."ping_health" to "authenticated";

grant references on table "public"."ping_health" to "authenticated";

grant select on table "public"."ping_health" to "authenticated";

grant trigger on table "public"."ping_health" to "authenticated";

grant truncate on table "public"."ping_health" to "authenticated";

grant update on table "public"."ping_health" to "authenticated";

grant delete on table "public"."ping_health" to "service_role";

grant insert on table "public"."ping_health" to "service_role";

grant references on table "public"."ping_health" to "service_role";

grant select on table "public"."ping_health" to "service_role";

grant trigger on table "public"."ping_health" to "service_role";

grant truncate on table "public"."ping_health" to "service_role";

grant update on table "public"."ping_health" to "service_role";


