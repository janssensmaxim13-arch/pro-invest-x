-- ============================================================================
-- ProInvestiX Enterprise - Database Initialization
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'proinvestix') THEN
        CREATE ROLE proinvestix WITH LOGIN PASSWORD 'proinvestix_secret';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE proinvestix TO proinvestix;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO proinvestix;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO proinvestix;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO proinvestix;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'ProInvestiX database initialized successfully at %', NOW();
END
$$;
