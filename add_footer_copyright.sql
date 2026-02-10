-- Add footer_copyright column to site_settings table
-- Run this SQL script directly on your database if Alembic migration fails

ALTER TABLE site_settings 
ADD COLUMN footer_copyright TEXT DEFAULT 'Powered By IT Centre Glorious Church Copyright @ 2023';
