-- Migration: Create ReviewLogs table
-- Version: 2
-- Description: Creates table for storing flashcard review history and FSRS algorithm data
-- Author: AI Assistant
-- Date: 2025-05-13

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ReviewLogs table: Stores history of flashcard reviews with FSRS algorithm data
CREATE TABLE IF NOT EXISTS ReviewLogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_profile_id INTEGER NOT NULL,
    flashcard_id INTEGER NOT NULL,
    review_log_data TEXT NOT NULL, -- JSON of fsrs.ReviewLog.to_dict()
    fsrs_rating INTEGER NOT NULL,   -- 1:Again, 2:Hard, 3:Good, 4:Easy
    reviewed_at TEXT NOT NULL,      -- ISO8601 datetime string
    scheduler_params_at_review TEXT NOT NULL, -- JSON of fsrs.Scheduler.parameters active at review time
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_profile_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (flashcard_id) REFERENCES Flashcards(id) ON DELETE CASCADE
);

-- Create index to optimize queries by user and flashcard
CREATE INDEX IF NOT EXISTS idx_reviewlogs_user_flashcard ON ReviewLogs (user_profile_id, flashcard_id);

-- Set schema version
PRAGMA user_version = 2;
