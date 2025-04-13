-- Migration: Initial Schema Setup
-- Description: Creates the initial database schema for 10xCards MVP including Users, Decks, and Flashcards tables
-- with their relationships, indexes, and triggers for updated_at columns.
-- Author: AI Assistant
-- Date: 2025-04-13

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Users table: Stores user profiles and authentication data
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT,  -- NULL allowed for potential OAuth/external auth
    hashed_api_key TEXT,   -- NULL allowed if user hasn't set up AI integration
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

-- Create triggers to automatically update updated_at timestamps

-- Users table updated_at trigger
CREATE TRIGGER update_users_updated_at
AFTER UPDATE ON Users
FOR EACH ROW
BEGIN
    UPDATE Users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
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

-- Set initial schema version
PRAGMA user_version = 1;
