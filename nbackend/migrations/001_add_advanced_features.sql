/*
  # Add Advanced Summary Features

  1. New Columns
    - `user_role` (varchar): Student/Researcher/Professional role
    - `extractive_summary` (text): Extractive component of hybrid summary
    - `abstractive_summary` (text): Abstractive component
    - `keywords` (jsonb): Array of extracted keywords
    - `sections` (jsonb): Document sections (abstract, methodology, etc.)
    - `is_private` (boolean): Privacy flag for memory system
    - `memory_type` (varchar): short_term or long_term

  2. Changes
    - Add columns to existing summaries table
    - Set default values for backward compatibility
*/

-- Add new columns to summaries table
ALTER TABLE summaries
ADD COLUMN IF NOT EXISTS user_role VARCHAR(50) DEFAULT 'general',
ADD COLUMN IF NOT EXISTS extractive_summary TEXT,
ADD COLUMN IF NOT EXISTS abstractive_summary TEXT,
ADD COLUMN IF NOT EXISTS keywords JSONB,
ADD COLUMN IF NOT EXISTS sections JSONB,
ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS memory_type VARCHAR(20) DEFAULT 'short_term';

-- Create index on memory_type for faster queries
CREATE INDEX IF NOT EXISTS idx_summaries_memory_type ON summaries(memory_type);

-- Create index on is_private for privacy filtering
CREATE INDEX IF NOT EXISTS idx_summaries_is_private ON summaries(is_private);

-- Create index on user_role for role-based queries
CREATE INDEX IF NOT EXISTS idx_summaries_user_role ON summaries(user_role);

-- Update existing records to have long_term memory by default
UPDATE summaries SET memory_type = 'long_term' WHERE memory_type = 'short_term';
