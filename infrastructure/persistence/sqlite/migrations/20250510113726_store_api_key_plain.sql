-- Migration: Store API key as encrypted instead of hashed
-- Version: 2

-- Rename column from hashed_api_key to encrypted_api_key
ALTER TABLE Users RENAME COLUMN hashed_api_key TO encrypted_api_key;

-- Add trigger to update updated_at timestamp
DROP TRIGGER IF EXISTS update_users_timestamp;
CREATE TRIGGER update_users_timestamp 
AFTER UPDATE ON Users
BEGIN
    UPDATE Users SET updated_at = DATETIME('now')
    WHERE id = NEW.id AND (
        OLD.username != NEW.username OR 
        OLD.encrypted_api_key != NEW.encrypted_api_key
    );
END;

-- Update schema version
PRAGMA user_version = 2;
