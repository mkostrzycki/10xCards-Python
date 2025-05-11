-- Migration: Merged Schema
-- Version: 1
-- Description: Merged schema containing all changes from previous migrations
-- Author: AI Assistant
-- Date: 2025-05-11

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Users table: Stores user profiles and authentication data
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT,  -- NULL allowed for potential OAuth/external auth
    encrypted_api_key BLOB,   -- Binary storage for encrypted API key
    default_llm_model TEXT NULL,  -- User's preferred LLM model
    app_theme TEXT NULL,   -- User's preferred UI theme
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Decks table: Stores flashcard decks belonging to users
CREATE TABLE Decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    UNIQUE (user_id, name)  -- Prevent duplicate deck names per user
);

-- Flashcards table: Stores individual flashcards belonging to decks
CREATE TABLE Flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    fsrs_state TEXT,  -- Stores FSRS algorithm state as JSON
    source TEXT NOT NULL CHECK (source IN ('manual', 'ai-generated', 'ai-edited')),
    ai_model_name TEXT,  -- NULL for manual cards
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES Decks(id) ON DELETE CASCADE
);

-- Create indexes for foreign keys to optimize JOIN operations
CREATE INDEX idx_decks_user_id ON Decks(user_id);
CREATE INDEX idx_flashcards_deck_id ON Flashcards(deck_id);

-- Create triggers for Users table
CREATE TRIGGER update_users_timestamp 
AFTER UPDATE ON Users
BEGIN
    UPDATE Users SET updated_at = DATETIME('now')
    WHERE id = NEW.id AND (
        OLD.username != NEW.username OR 
        OLD.encrypted_api_key IS NOT NEW.encrypted_api_key OR
        OLD.default_llm_model != NEW.default_llm_model OR
        OLD.app_theme != NEW.app_theme
    );
END;

-- Decks table updated_at trigger
CREATE TRIGGER update_decks_updated_at
AFTER UPDATE ON Decks
FOR EACH ROW
BEGIN
    UPDATE Decks SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Flashcards table updated_at trigger
CREATE TRIGGER update_flashcards_updated_at
AFTER UPDATE ON Flashcards
FOR EACH ROW
BEGIN
    UPDATE Flashcards SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Set schema version
PRAGMA user_version = 1;
