SET session_replication_role = replica;

-- Healthcheck table seed data
INSERT INTO public.ping_health (id, last_ping)
VALUES ('00000000-0000-0000-0000-000000000001', now())
ON CONFLICT (id) DO NOTHING;