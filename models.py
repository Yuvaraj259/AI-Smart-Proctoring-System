from db import db
from datetime import datetime

class StudentModel:
    @staticmethod
    def get_by_id(student_id):
        query = "SELECT * FROM students WHERE student_id = ?"
        results = db.execute_query(query, (student_id,))
        return results[0] if results else None

    @staticmethod
    def create(student_id, name, email):
        query = "INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)"
        return db.execute_insert(query, (student_id, name, email))

    @staticmethod
    def update_face_encoding(student_id, encoding_blob):
        query = "UPDATE students SET face_encoding = ? WHERE student_id = ?"
        return db.execute_query(query, (encoding_blob, student_id))

class ExamModel:
    @staticmethod
    def start_exam(student_id):
        query = "INSERT INTO exams (student_id, start_time) VALUES (?, ?)"
        return db.execute_insert(query, (student_id, datetime.now()))

    @staticmethod
    def end_exam(exam_id):
        query = "UPDATE exams SET end_time = ? WHERE exam_id = ?"
        return db.execute_query(query, (datetime.now(), exam_id))

    @staticmethod
    def get_exam(exam_id):
        query = "SELECT * FROM exams WHERE exam_id = ?"
        results = db.execute_query(query, (exam_id,))
        return results[0] if results else None

    @staticmethod
    def get_all():
        query = "SELECT e.*, s.name as student_name FROM exams e JOIN students s ON e.student_id = s.student_id ORDER BY start_time DESC"
        return db.execute_query(query)

    @staticmethod
    def get_stats():
        query_exams = "SELECT COUNT(*) as total FROM exams"
        query_students = "SELECT COUNT(*) as total FROM students"
        exams = db.execute_query(query_exams)
        students = db.execute_query(query_students)
        return {
            'total_exams': exams[0]['total'] if exams else 0,
            'total_students': students[0]['total'] if students else 0
        }

class ViolationModel:
    @staticmethod
    def log_violation(exam_id, violation_type):
        query = "INSERT INTO violations (exam_id, type, timestamp) VALUES (?, ?, ?)"
        return db.execute_insert(query, (exam_id, violation_type, datetime.now()))

    @staticmethod
    def get_by_exam(exam_id):
        query = "SELECT * FROM violations WHERE exam_id = ? ORDER BY timestamp DESC"
        return db.execute_query(query, (exam_id,))
