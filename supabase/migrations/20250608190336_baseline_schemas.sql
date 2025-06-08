create table "public"."applications" (
    "id" uuid not null,
    "listing_id" uuid not null,
    "date_applied" timestamp with time zone not null default now(),
    "email" text not null,
    "first_name" text not null,
    "last_name" text not null,
    "preferred_name" text,
    "gpa" double precision,
    "grad_month" text not null,
    "grad_year" integer not null,
    "has_gpa" boolean not null,
    "image" text not null,
    "website" text,
    "linkedin" text,
    "resume" text not null,
    "major" text not null,
    "minor" text,
    "phone" text not null,
    "colleges" jsonb,
    "responses" jsonb
);


create table "public"."listings" (
    "id" uuid not null,
    "title" text not null,
    "date_created" timestamp with time zone not null default now(),
    "deadline" timestamp with time zone not null,
    "is_encrypted" boolean not null,
    "is_visible" boolean not null,
    "questions" jsonb
);


CREATE UNIQUE INDEX applications_pkey ON public.applications USING btree (id);

CREATE UNIQUE INDEX listings_pkey ON public.listings USING btree (id);

alter table "public"."applications" add constraint "applications_pkey" PRIMARY KEY using index "applications_pkey";

alter table "public"."listings" add constraint "listings_pkey" PRIMARY KEY using index "listings_pkey";

alter table "public"."applications" add constraint "applications_listing_id_fkey" FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE not valid;

alter table "public"."applications" validate constraint "applications_listing_id_fkey";

grant delete on table "public"."applications" to "anon";

grant insert on table "public"."applications" to "anon";

grant references on table "public"."applications" to "anon";

grant select on table "public"."applications" to "anon";

grant trigger on table "public"."applications" to "anon";

grant truncate on table "public"."applications" to "anon";

grant update on table "public"."applications" to "anon";

grant delete on table "public"."applications" to "authenticated";

grant insert on table "public"."applications" to "authenticated";

grant references on table "public"."applications" to "authenticated";

grant select on table "public"."applications" to "authenticated";

grant trigger on table "public"."applications" to "authenticated";

grant truncate on table "public"."applications" to "authenticated";

grant update on table "public"."applications" to "authenticated";

grant delete on table "public"."applications" to "service_role";

grant insert on table "public"."applications" to "service_role";

grant references on table "public"."applications" to "service_role";

grant select on table "public"."applications" to "service_role";

grant trigger on table "public"."applications" to "service_role";

grant truncate on table "public"."applications" to "service_role";

grant update on table "public"."applications" to "service_role";

grant delete on table "public"."listings" to "anon";

grant insert on table "public"."listings" to "anon";

grant references on table "public"."listings" to "anon";

grant select on table "public"."listings" to "anon";

grant trigger on table "public"."listings" to "anon";

grant truncate on table "public"."listings" to "anon";

grant update on table "public"."listings" to "anon";

grant delete on table "public"."listings" to "authenticated";

grant insert on table "public"."listings" to "authenticated";

grant references on table "public"."listings" to "authenticated";

grant select on table "public"."listings" to "authenticated";

grant trigger on table "public"."listings" to "authenticated";

grant truncate on table "public"."listings" to "authenticated";

grant update on table "public"."listings" to "authenticated";

grant delete on table "public"."listings" to "service_role";

grant insert on table "public"."listings" to "service_role";

grant references on table "public"."listings" to "service_role";

grant select on table "public"."listings" to "service_role";

grant trigger on table "public"."listings" to "service_role";

grant truncate on table "public"."listings" to "service_role";

grant update on table "public"."listings" to "service_role";


