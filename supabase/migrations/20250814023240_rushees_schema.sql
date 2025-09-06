create table "public"."rushees" (
    "id" uuid not null,
    "name" text not null,
    "email" text not null
);


CREATE UNIQUE INDEX rushees_pkey ON public.rushees USING btree (id);

alter table "public"."rushees" add constraint "rushees_pkey" PRIMARY KEY using index "rushees_pkey";

grant delete on table "public"."rushees" to "anon";

grant insert on table "public"."rushees" to "anon";

grant references on table "public"."rushees" to "anon";

grant select on table "public"."rushees" to "anon";

grant trigger on table "public"."rushees" to "anon";

grant truncate on table "public"."rushees" to "anon";

grant update on table "public"."rushees" to "anon";

grant delete on table "public"."rushees" to "authenticated";

grant insert on table "public"."rushees" to "authenticated";

grant references on table "public"."rushees" to "authenticated";

grant select on table "public"."rushees" to "authenticated";

grant trigger on table "public"."rushees" to "authenticated";

grant truncate on table "public"."rushees" to "authenticated";

grant update on table "public"."rushees" to "authenticated";

grant delete on table "public"."rushees" to "service_role";

grant insert on table "public"."rushees" to "service_role";

grant references on table "public"."rushees" to "service_role";

grant select on table "public"."rushees" to "service_role";

grant trigger on table "public"."rushees" to "service_role";

grant truncate on table "public"."rushees" to "service_role";

grant update on table "public"."rushees" to "service_role";


