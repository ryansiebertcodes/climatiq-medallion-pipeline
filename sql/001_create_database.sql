-- Run as superuser: psql -U postgres
-- Creates the database and grants ownership to the application user.

CREATE DATABASE climatiq_pipeline
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8';
