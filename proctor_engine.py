import cv2
import threading
import time
import numpy as np
import pickle
from models import ViolationModel, StudentModel, ExamModel

class ProctorEngine:
    def __init__(self, exam_id):
        self.exam_id = exam_id
        # Get student encoding
        exam = ExamModel.get_exam(exam_id)
        student = StudentModel.get_by_id(exam['student_id'])
        
        self.face_recognizer = None
        if student['face_encoding']:
            try:
                registered_face = pickle.loads(student['face_encoding'])
                # Initialize LBPH Face Recognizer
                self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
                # Train with the single registered face (as a list)
                self.face_recognizer.train([registered_face], np.array([1]))
            except Exception as e:
                print(f"Error initializing face recognizer: {e}")

        # Load the pre-trained Haar Cascade classifier for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = None
        self.is_running = False
        self.last_violation_time = 0
        self.violation_cooldown = 2
        self.last_recognition_time = 0
        self.recognition_interval = 5

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.is_running = True

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def generate_frames(self):
        while self.is_running:
            success, frame = self.cap.read()
            if not success:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            violation_type = None
            if len(faces) == 0:
                violation_type = "NO_FACE"
                color = (0, 0, 255)
            elif len(faces) > 1:
                violation_type = "MULTIPLE_FACES"
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)

            # Draw bounding boxes
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            status_text = f"Status: {violation_type if violation_type else 'Normal'}"
            
            # Anti-Impersonation Check
            if len(faces) == 1 and self.face_recognizer is not None:
                if time.time() - self.last_recognition_time > self.recognition_interval:
                    self.last_recognition_time = time.time()
                    
                    (x, y, w, h) = faces[0]
                    current_face = gray[y:y+h, x:x+w]
                    current_face = cv2.resize(current_face, (200, 200))

                    label, confidence = self.face_recognizer.predict(current_face)
                    # Lower confidence means better match for LBPH
                    # Generally < 70 is a good match depending on environment
                    if confidence > 85: 
                        violation_type = "IMPERSONATION"
                        color = (0, 0, 255)
                        status_text = "Status: IMPERSONATION DETECTED"
                        print(f"Impersonation Alert! Confidence: {confidence}")

            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Log violation to database with cooldown
            if violation_type and (time.time() - self.last_violation_time > self.violation_cooldown):
                ViolationModel.log_violation(self.exam_id, violation_type)
                self.last_violation_time = time.time()
                print(f"Logged Violation: {violation_type}")

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        self.stop()
