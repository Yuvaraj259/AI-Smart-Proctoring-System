from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_key')

# Global dictionary to keep track of active proctor engines
active_exams = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register_face', methods=['POST'])
def register_face():
    import base64
    import numpy as np
    import cv2
    import pickle

    data = request.json
    student_id = data.get('student_id')
    image_data_full = data.get('image')
    if not image_data_full or ',' not in image_data_full:
        return jsonify({'success': False, 'message': 'Invalid image data received.'})
    
    image_data = image_data_full.split(',')[1]

    try:
        img_bytes = base64.b64decode(image_data)
        if not img_bytes:
            return jsonify({'success': False, 'message': 'Decoded image is empty.'})
            
        nparr = np.frombuffer(img_bytes, np.uint8)
        if nparr.size == 0:
            return jsonify({'success': False, 'message': 'Image buffer is empty.'})
            
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'success': False, 'message': 'OpenCV could not decode the image.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Image processing error: {str(e)}'})

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use Haar Cascade to find the face
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        return jsonify({'success': False, 'message': 'No face detected. Please try again.'})
    if len(faces) > 1:
        return jsonify({'success': False, 'message': 'Multiple faces detected. Please register alone.'})

    (x, y, w, h) = faces[0]
    face_roi = gray[y:y+h, x:x+w]
    face_roi = cv2.resize(face_roi, (200, 200))

    # Check if student exists
    from models import StudentModel
    student = StudentModel.get_by_id(student_id)
    if not student:
        return jsonify({'success': False, 'message': f'Student ID {student_id} not found. Please contact admin.'})

    # We store the raw image bytes for training later in the engine
    # or we can train a small model per user. For MVP, we store the ROI.
    face_blob = pickle.dumps(face_roi)
    StudentModel.update_face_encoding(student_id, face_blob)
    
    return jsonify({'success': True, 'message': 'Face registered successfully!'})

@app.route('/start_exam', methods=['POST'])
def start_exam():
    from models import StudentModel, ExamModel
    student_id = request.form.get('student_id')
    student = StudentModel.get_by_id(student_id)
    
    if not student:
        return "Student not found. Please register first.", 404
        
    if not student['face_encoding']:
        return "Face not registered. Please go to Face Registration first.", 403

    exam_id = ExamModel.start_exam(student_id)
    return redirect(url_for('exam_room', exam_id=exam_id))

@app.route('/exam_room/<int:exam_id>')
def exam_room(exam_id):
    from models import ExamModel
    exam = ExamModel.get_exam(exam_id)
    if not exam:
        return "Exam not found", 404
    return render_template('exam_room.html', exam_id=exam_id)

@app.route('/video_feed/<int:exam_id>')
def video_feed(exam_id):
    from proctor_engine import ProctorEngine
    if exam_id not in active_exams:
        engine = ProctorEngine(exam_id)
        engine.start()
        active_exams[exam_id] = engine
    
    return Response(active_exams[exam_id].generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_exam/<int:exam_id>')
def stop_exam(exam_id):
    from models import ExamModel
    if exam_id in active_exams:
        active_exams[exam_id].stop()
        del active_exams[exam_id]
    
    ExamModel.end_exam(exam_id)
    return redirect(url_for('view_report', exam_id=exam_id))

@app.route('/report/<int:exam_id>')
def view_report(exam_id):
    from models import ExamModel, ViolationModel
    exam = ExamModel.get_exam(exam_id)
    violations = ViolationModel.get_by_exam(exam_id)
    return render_template('report.html', exam=exam, violations=violations)

@app.route('/api/violations/<int:exam_id>')
def get_violations(exam_id):
    from models import ViolationModel
    violations = ViolationModel.get_by_exam(exam_id)
    return jsonify(violations)

@app.route('/api/log_violation/<int:exam_id>', methods=['POST'])
def log_browser_violation(exam_id):
    from models import ViolationModel
    data = request.json
    violation_type = data.get('type')
    if violation_type:
        ViolationModel.log_violation(exam_id, violation_type)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/admin')
def admin_dashboard():
    from models import ExamModel
    stats = ExamModel.get_stats()
    exams = ExamModel.get_all()
    # Add active status to exams
    for exam in exams:
        exam['is_active'] = exam['exam_id'] in active_exams
    return render_template('admin.html', stats=stats, exams=exams)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
