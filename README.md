# AI-Based Smart Examination Monitoring System (Online Proctoring)

This is a production-ready MVP of an AI-driven proctoring system that monitors students during online exams using computer vision to detect suspicious activities.

## 🚀 Features
- **Real-Time Monitoring**: Face detection using OpenCV to ensure only the student is present.
- **Anti-Impersonation (Phase 2)**: Face recognition to verify the student's identity against a registered profile.
- **Tab Switching Detection (Phase 3)**: Monitors if a student leaves the exam tab or window.
- **Admin Dashboard (Phase 3)**: A central hub for monitoring all active exams and statistics.
- **Violation Logging**: Automatically logs "NO_FACE", "MULTIPLE_FACES", "IMPERSONATION", or "TAB_SWITCH" directly to MySQL.
- **Premium UI**: Modern Glassmorphic design with real-time violation alerts.
- **Reporting**: Generates a detailed violation report after the exam concludes.

## 🛠 Tech Stack
- **Backend**: Flask, OpenCV
- **Database**: MySQL
- **Frontend**: HTML5, Vanilla CSS, Jinja2, JavaScript

## 📦 Installation & Setup

### 1. Requirements
Ensure you have Python 3.10+ and MySQL installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
1. Login to your MySQL server.
2. Run the commands in `schema.sql` to create the database and tables.
   ```bash
   mysql -u root -p < schema.sql
   ```
3. Update the `.env` file with your database credentials.

### 4. Run the Application
```bash
python app.py
```
Wait for the server to start (typically at `http://127.0.0.1:5000`).

⚙️ How it Works
1. Go to **Face Registration** and register your face with your Student ID (e.g. `STU001`).
2. Go back to the home page, enter your Student ID, and click **Start Examination**.
3. The system activates the webcam and begins monitoring.
4. The proctoring engine periodically (every 5s) verifies your identity.
5. Any violations (missing face, extra faces, or impersonation) are logged in real-time.
7. **Admin Access**: Navigate to `/admin` to see the instructor's dashboard.

## 🗺 Future Roadmap (Phase 2)
- **Face Recognition**: Compare the live face with a registered student photo.
- **Head Movement Detection**: Log if the student looks away from the screen too often.
- **Tab Switching**: Prevent students from switching tabs during the exam.
- **Audio Detection**: Monitor for voices or suspicious background noise.
- **Dashboard**: Admin panel for live monitoring of all active exams.
