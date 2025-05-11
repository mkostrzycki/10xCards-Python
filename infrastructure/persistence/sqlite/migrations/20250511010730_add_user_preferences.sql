-- Add user preferences columns to Users table
-- Version: 3
-- This migration adds two columns to store user preferences:
-- 1. default_llm_model - The preferred LLM model for AI operations
-- 2. app_theme - The preferred UI theme for the application

ALTER TABLE Users ADD COLUMN default_llm_model TEXT NULL;
ALTER TABLE Users ADD COLUMN app_theme TEXT NULL;

-- Update trigger to include new columns
DROP TRIGGER IF EXISTS update_users_timestamp;
CREATE TRIGGER update_users_timestamp 
AFTER UPDATE ON Users
BEGIN
    UPDATE Users SET updated_at = DATETIME('now')
    WHERE id = NEW.id AND (
        OLD.username != NEW.username OR 
        OLD.encrypted_api_key != NEW.encrypted_api_key OR
        OLD.default_llm_model != NEW.default_llm_model OR
        OLD.app_theme != NEW.app_theme
    );
END;

-- Update schema version
PRAGMA user_version = 3;
