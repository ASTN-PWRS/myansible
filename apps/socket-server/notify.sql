CREATE OR REPLACE FUNCTION notify_users_update()
RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('users_updated', row_to_json(NEW)::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_update_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION notify_users_update();
