-- ============================================================
-- Skill Gap Analyzer v4 — Full Database Schema
-- Run this in your MySQL database
-- ============================================================

CREATE DATABASE IF NOT EXISTS skill_gap_analyzer;
USE skill_gap_analyzer;

-- ─────────────────────────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  UNIQUE NOT NULL,
    username      VARCHAR(80)   UNIQUE NOT NULL,
    password      VARCHAR(255)  NOT NULL,
    role          ENUM('student','professional','job_seeker') DEFAULT 'student',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────
-- JOB ROLES  (replaces the hardcoded JOB_SKILLS dict)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_roles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    role_key        VARCHAR(120) UNIQUE NOT NULL,   -- lowercase slug, e.g. "data scientist"
    display_name    VARCHAR(150) NOT NULL,           -- e.g. "Data Scientist"
    is_ai_generated TINYINT(1) DEFAULT 0,           -- 1 = created by AI, 0 = seeded
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────
-- JOB ROLE SKILLS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_role_skills (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    job_role_id  INT NOT NULL,
    skill_name   VARCHAR(100) NOT NULL,
    skill_type   ENUM('technical','soft') NOT NULL,
    skill_order  INT DEFAULT 0,
    FOREIGN KEY (job_role_id) REFERENCES job_roles(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────
-- USER PROGRESS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_progress (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,
    job_role         VARCHAR(120) NOT NULL,
    completed_skills TEXT NOT NULL,
    last_updated     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_job (user_id, job_role)
);

-- ─────────────────────────────────────────────────────────────
-- SEED: 24 built-in job roles
-- Run seed_jobs.py after creating these tables to populate them
-- ─────────────────────────────────────────────────────────────
