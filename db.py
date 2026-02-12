import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.db_path = os.getenv('DB_PATH', 'proctor.db')
        self._initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # To get dictionary-like results
        return conn

    def _initialize_db(self):
        # Create tables if they don't exist
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Student table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                face_encoding BLOB
            )
        ''')
        
        # Exams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER,
                type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
            )
        ''')
        
        # Sample students
        cursor.execute("INSERT OR IGNORE INTO students (student_id, name, email) VALUES (?, ?, ?)", 
                       ('STU001', 'Test Student', 'test@example.com'))
        cursor.execute("INSERT OR IGNORE INTO students (student_id, name, email) VALUES (?, ?, ?)", 
                       ('STU002', 'Yuvaraj', 'yuvaraj@example.com'))
        cursor.execute("INSERT OR IGNORE INTO students (student_id, name, email) VALUES (?, ?, ?)", 
                       ('STU003', 'Admin Test', 'admin@example.com'))
        
        conn.commit()
        conn.close()

    def execute_query(self, query, params=None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = [dict(row) for row in cursor.fetchall()]
            conn.commit()
            return results
        except sqlite3.Error as e:
            print(f"Query error: {e}")
            return None
        finally:
            conn.close()

    def execute_insert(self, query, params=None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except sqlite3.Error as e:
            print(f"Insert error: {e}")
            return None
        finally:
            conn.close()

db = Database()
