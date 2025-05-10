-- Add user preferences columns to Users table
-- Version: 3
-- This migration adds two columns to store user preferences:
-- 1. default_llm_model - The preferred LLM model for AI operations
-- 2. app_theme - The preferred UI theme for the application

ALTER TABLE Users ADD COLUMN default_llm_model TEXT NULL;
ALTER TABLE Users ADD COLUMN app_theme TEXT NULL;

-- Update schema version
PRAGMA user_version = 2;
