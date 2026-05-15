-- Create the three schemas that form the backbone of our data warehouse
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
-- Create a read-only user for Metabase (security best practice)
CREATE USER metabase_readonly WITH PASSWORD 'metabase_readonly_pass';
-- Grant connect to the analytics database
GRANT CONNECT ON DATABASE analytics TO metabase_readonly;
-- Grant usage on the marts schema (Metabase should only see business-ready tables)
GRANT USAGE ON SCHEMA marts TO metabase_readonly;
-- Grant read-only access to all current and future tables in marts
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO metabase_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO metabase_readonly;
-- Also grant read access to staging for debugging (optional — lock this down in production)
GRANT USAGE ON SCHEMA staging TO metabase_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA staging TO metabase_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT SELECT ON TABLES TO metabase_readonly;
-- Create the Metabase internal application database
-- (Metabase will create its own tables here on first launch)
CREATE DATABASE metabase;
-- Verify schemas were created
\dn
