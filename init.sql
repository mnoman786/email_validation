-- PostgreSQL initialization script
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Optimize for text search on email columns
-- These will be created after Django migrations run
