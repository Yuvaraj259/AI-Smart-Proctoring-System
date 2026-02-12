-- Database Schema for AI Proctoring System

CREATE DATABASE IF NOT EXISTS proctor_db;
USE proctor_db;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    face_encoding BLOB NULL
);

-- Exams table
CREATE TABLE IF NOT EXISTS exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50),
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Violations table
CREATE TABLE IF NOT EXISTS violations (
    violation_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT,
    type ENUM('NO_FACE', 'MULTIPLE_FACES', 'IMPERSONATION', 'TAB_SWITCH') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE
);

-- Insert a sample student for testing
INSERT IGNORE INTO students (student_id, name, email) VALUES ('STU001', 'Test Student', 'test@example.com');
