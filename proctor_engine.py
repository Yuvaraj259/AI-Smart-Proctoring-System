import cv2
import time
import numpy as np
import pickle
from models import ViolationModel, StudentModel, ExamModel

class ProctorEngine:
    def __init__(self, exam_id):
        self.exam_id = exam_id
        # Get student encoding
        exam = ExamModel.get_exam(exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")
            
        student = StudentModel.get_by_id(exam['student_id'])
        
        self.face_recognizer = None
        if student and student.get('face_encoding'):
            try:
                registered_face = pickle.loads(student['face_encoding'])
                # Initialize LBPH Face Recognizer
                self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
                self.face_recognizer.train([registered_face], np.array([1]))
            except Exception as e:
                print(f"Error initializing face recognizer: {e}")

        # Load the Haar Cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            self.face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

        self.last_violation_time = 0
        self.violation_cooldown = 2

    def process_frame(self, frame):
        """Processes a single frame sent from the client and returns the processed frame and violation status."""
        if frame is None:
            return None, None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Use more robust parameters
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        violation_type = None
        color = (0, 255, 0) # Default: Success Green
        
        if len(faces) == 0:
            violation_type = "NO_FACE"
            color = (0, 0, 255) # Red
        elif len(faces) > 1:
            violation_type = "MULTIPLE_FACES"
            color = (0, 0, 255) # Red
        else:
            # Single face detected, check for impersonation
            if self.face_recognizer is not None:
                (x, y, w, h) = faces[0]
                current_face = gray[y:y+h, x:x+w]
                current_face = cv2.resize(current_face, (200, 200))

                label, confidence = self.face_recognizer.predict(current_face)
                # LBPH confidence: lower is better. 85 is a safe threshold.
                if confidence > 85: 
                    violation_type = "IMPERSONATION"
                    color = (0, 0, 255)

        # Draw bounding boxes and status
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        status_text = f"Status: {violation_type if violation_type else 'Secure'}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Log violation to database if cooldown passed
        if violation_type and (time.time() - self.last_violation_time > self.violation_cooldown):
            ViolationModel.log_violation(self.exam_id, violation_type)
            self.last_violation_time = time.time()
            print(f"Logged Violation: {violation_type}")

        return frame, violation_type

