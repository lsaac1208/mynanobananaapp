-- ================================================================
-- API Configuration Management System - Database Migration
-- Created: 2025-10-01
-- Purpose: Create api_config_groups table with encryption support
-- ================================================================

-- Drop existing table if exists (for development reset)
DROP TABLE IF EXISTS api_config_groups;

-- ================================================================
-- Main Table: API Configuration Groups
-- ================================================================
CREATE TABLE api_config_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 0,
    openai_hk_base_url TEXT NOT NULL,
    openai_hk_api_key_encrypted BLOB NOT NULL,  -- Encrypted binary data
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CHECK (length(name) >= 1 AND length(name) <= 100),
    CHECK (length(openai_hk_base_url) >= 1 AND length(openai_hk_base_url) <= 500)
);

-- ================================================================
-- Indexes for Performance Optimization
-- ================================================================
CREATE INDEX idx_api_config_is_active ON api_config_groups(is_active);
CREATE INDEX idx_api_config_name ON api_config_groups(name);

-- ================================================================
-- Trigger: Enforce Single Active Configuration Rule
-- ================================================================
-- When a configuration is activated, automatically deactivate all others
DROP TRIGGER IF EXISTS enforce_single_active_config;

CREATE TRIGGER enforce_single_active_config
BEFORE UPDATE ON api_config_groups
WHEN NEW.is_active = 1 AND OLD.is_active = 0
BEGIN
    UPDATE api_config_groups
    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
    WHERE is_active = 1 AND id != NEW.id;
END;

-- ================================================================
-- Trigger: Automatic Timestamp Update
-- ================================================================
-- Automatically update updated_at when any field is modified
DROP TRIGGER IF EXISTS update_api_config_timestamp;

CREATE TRIGGER update_api_config_timestamp
AFTER UPDATE ON api_config_groups
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at  -- Only update if not manually set
BEGIN
    UPDATE api_config_groups
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ================================================================
-- Verification Query
-- ================================================================
-- SELECT name FROM sqlite_master WHERE type='table' AND name='api_config_groups';
-- SELECT * FROM api_config_groups;
