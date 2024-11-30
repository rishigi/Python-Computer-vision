import tkinter as tk
from tkinter import Label, Button, Frame
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
import os
import threading
from playsound import playsound

# Initialize MediaPipe pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


class ExerciseCorrectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Pose Correction AI Trainer")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#282C34")

        # Initial variables
        self.exercise = None
        self.rep_count = 0
        self.rep_started = False
        self.paused = False

        # Create a start page
        self.start_frame = Frame(root, bg="#61AFEF")
        self.start_frame.pack(fill="both", expand=True)

        Label(self.start_frame, text="Welcome to the Exercise Pose Correction AI Trainer!",
              font=("Helvetica", 20), bg="#61AFEF", fg="white").pack(pady=20)
        Button(self.start_frame, text="Start", font=("Helvetica", 14), bg="#98C379", fg="white",
               command=self.show_main_page).pack(pady=10)
        Button(self.start_frame, text="Quit", font=("Helvetica", 14), bg="#E06C75", fg="white",
               command=self.quit_app).pack(pady=10)

        # Main application page
        self.main_frame = Frame(root, bg="#282C34")

        self.video_label = Label(self.main_frame, bg="#282C34")
        self.video_label.pack()

        self.feedback_label = Label(self.main_frame, text="Select an exercise to start!",
                                    font=("Helvetica", 14), bg="#282C34", fg="#61AFEF")
        self.feedback_label.pack(pady=2)

        self.rep_count_label = Label(self.main_frame, text="Reps: 0", font=("Helvetica", 14),
                                     bg="#282C34", fg="#98C379")
        self.rep_count_label.pack(pady=2)

        self.control_frame = Frame(self.main_frame, bg="#282C34")
        self.control_frame.pack(pady=2)

        # Arrange exercise buttons in grid
        button_texts = [
            "squats", "pushups", "lunges", "planks", "crunches",
            "Leg Raises", "Bicycle Crunches", "Incline Press",
            "Bicep Curls",
        ]
        button_commands = [
            self.set_exercise_squats, self.set_exercise_pushups, self.set_exercise_lunges,
            self.set_exercise_planks, self.set_exercise_crunches,
            self.set_exercise_leg_raises, self.set_exercise_bicycle_crunches, self.set_exercise_incline_press, self.set_exercise_bicep_curls,
        ]

        for i, (text, command) in enumerate(zip(button_texts, button_commands)):
            row, column = divmod(i, 10)
            Button(self.control_frame, text=text, width=13, height=1, font=("Helvetica", 12),
                   bg="#61AFEF", fg="white", command=command).grid(row=row, column=column, )

        self.pause_button = Button(self.control_frame, text="Pause", width=10, height=1, font=("Helvetica", 12),
                                   bg="#E5C07B", fg="white", command=self.toggle_pause)
        self.pause_button.grid(row=len(button_texts) // 10 + 1, column=0, columnspan=5)

        Button(self.control_frame, text="Quit", width=10, height=1, font=("Helvetica", 12), bg="#E06C75", fg="white",
               command=self.quit_app).grid(row=len(button_texts) // 10 + 1, column=5, columnspan=2)

        # Start video capture
        self.cap = cv2.VideoCapture(0)

        # Close app on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_main_page(self):
        self.start_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.update_video_feed()

    def play_audio_feedback(self, filename):
        # Define the path to the audio files directory
        audio_file_path = os.path.join("audio_feedback", f"{filename}.mp3")

        def play_sound():
            try:
                if os.path.exists(audio_file_path):
                    playsound(audio_file_path)
                else:
                    print(f"Audio file {filename} not found at {audio_file_path}")
            except Exception as e:
                print(f"Error playing audio: {e}")

            # Ensure the audio is played in a separate thread

        if not hasattr(self, '_audio_thread') or not self._audio_thread.is_alive():
            self._audio_thread = threading.Thread(target=play_sound, daemon=True)
            self._audio_thread.start()
        else:
            print("Audio is already playing.")

    def set_exercise_squats(self):
        self.exercise = "squats"
        self.reset()
        self.play_audio_feedback("1")

    def set_exercise_pushups(self):
        self.exercise = "pushups"
        self.reset()
        self.play_audio_feedback("2")

    def set_exercise_lunges(self):
        self.exercise = "lunges"
        self.reset()
        self.play_audio_feedback("3")

    def set_exercise_planks(self):
        self.exercise = "planks"
        self.reset()
        self.play_audio_feedback("4")

    def set_exercise_crunches(self):
        self.exercise = "crunches"
        self.reset()
        self.play_audio_feedback("5")

    def set_exercise_leg_raises(self):
        self.exercise = "leg_raises"
        self.reset()
        self.play_audio_feedback("6")

    def set_exercise_bicycle_crunches(self):
        self.exercise = "bicycle_crunches"
        self.reset()
        self.play_audio_feedback("7")

    def set_exercise_incline_press(self):
        self.exercise = "incline_press"
        self.reset()
        self.play_audio_feedback("8")

    def set_exercise_bicep_curls(self):
        self.exercise = "bicep_curls"
        self.reset()
        self.play_audio_feedback("9")

    def reset(self):
        self.rep_count = 0
        self.rep_started = False
        self.feedback_label.config(text="Perform the exercise!")
        self.rep_count_label.config(text="Reps: 0")

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")

    def update_video_feed(self):
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame_rgb)

                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                    # Apply exercise-specific logic
                    if self.exercise == "squats":
                        self.correct_and_count_squat(results.pose_landmarks)
                    elif self.exercise == "pushups":
                        self.correct_and_count_pushup(results.pose_landmarks)
                    elif self.exercise == "lunges":
                        self.correct_and_count_lunge(results.pose_landmarks)
                    elif self.exercise == "planks":
                        self.correct_and_count_plank(results.pose_landmarks)
                    elif self.exercise == "crunches":
                        self.correct_and_count_crunch(results.pose_landmarks)
                    elif self.exercise == "leg_raises":
                        self.correct_and_count_leg_raises(results.pose_landmarks)
                    elif self.exercise == "bicycle_crunches":
                        self.correct_and_count_bicycle_crunches(results.pose_landmarks)
                    elif self.exercise == "incline_press":
                        self.correct_and_count_incline_press(results.pose_landmarks)
                    elif self.exercise == "bicep_curls":
                        self.correct_and_count_bicep_curls(results.pose_landmarks)

                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_video_feed)

    def calculate_angle(self, point1, point2, point3):
        a = np.array([point1.x, point1.y])
        b = np.array([point2.x, point2.y])
        c = np.array([point3.x, point3.y])

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360.0 - angle

        return angle

    def correct_and_count_squat(self, landmarks):
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

        angle = self.calculate_angle(hip, knee, ankle)
        if angle < 90 and not self.rep_started:
            self.rep_started = True
        if angle >= 160 and self.rep_started:
            self.rep_count += 1
            self.rep_started = False
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")

        self.feedback_label.config(text="Good Squat!" if angle < 90 else "Bend your knees more!")

    def correct_and_count_pushup(self, landmarks):
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

        angle = self.calculate_angle(shoulder, hip, ankle)
        if angle < 90 and not self.rep_started:
            self.rep_started = True
        if angle >= 160 and self.rep_started:
            self.rep_count += 1
            self.rep_started = False
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")

        self.feedback_label.config(text="Good Pushup!" if 160 < angle > 180 else "Keep your body straight!")

    def correct_and_count_lunge(self, landmarks):
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

        angle = self.calculate_angle(hip, knee, ankle)
        if angle < 90 and not self.rep_started:
            self.rep_started = True
        if angle >= 160 and self.rep_started:
            self.rep_count += 1
            self.rep_started = False
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")

        self.feedback_label.config(text="Good Lunge!" if angle < 90 else "Lower your body more!")

    def correct_and_count_plank(self, landmarks):
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

        angle = self.calculate_angle(shoulder, hip, ankle)
        if angle < 90 and not self.rep_started:
            self.rep_started = True
        if angle >= 160 and self.rep_started:
            self.rep_count += 1
            self.rep_started = False
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")

        self.feedback_label.config(text="Good Plank!" if 160 < angle > 180 else "Keep your body straight!")

    def correct_and_count_crunch(self, landmarks):
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]

        angle = self.calculate_angle(shoulder, hip, knee)
        if angle < 45 and not self.rep_started:
            self.rep_started = True
        if angle >= 160 and self.rep_started:
            self.rep_count += 1
            self.rep_started = False
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")

        self.feedback_label.config(text="Good Crunch!" if angle < 45 else "Curl up more!")

    def calculate_angle(self, point1, point2, point3):
        a = np.array([point1.x, point1.y])
        b = np.array([point2.x, point2.y])
        c = np.array([point3.x, point3.y])

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def correct_and_count_leg_raises(self, landmarks):
        # Example: Measure the angle between the hip, knee, and ankle
        left_leg_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
                                              landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE],
                                              landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])

        right_leg_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
                                               landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE],
                                               landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])

        if left_leg_angle > 160 and right_leg_angle > 160:
            if self.rep_started:
                self.rep_count += 1
                self.rep_count_label.config(text=f"Reps: {self.rep_count}")
                self.rep_started = False
        elif left_leg_angle < 80 and right_leg_angle < 80:
            self.rep_started = True

    def correct_and_count_bicycle_crunches(self, landmarks):
        # Left side
        left_elbow_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                                landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
                                                landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE])

        # Right side
        right_elbow_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                                 landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
                                                 landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE])

        # Monitor elbow to opposite knee
        if left_elbow_angle < 30 or right_elbow_angle < 30:  # Threshold for close crunch
            if not self.rep_started:
                self.rep_started = True

        if self.rep_started and (left_elbow_angle > 100 and right_elbow_angle > 100):  # Threshold for return to start
            self.rep_count += 1
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")
            self.rep_started = False

        # Provide feedback
        if left_elbow_angle < 30 or right_elbow_angle < 30:
            self.feedback_label.config(text="Great! You're crunching correctly.")
        else:
            self.feedback_label.config(text="Try to bring your elbow closer to the opposite knee.")

    def correct_and_count_incline_press(self, landmarks):
        # Add correction logic for Incline Press
        left_elbow_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                                landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
                                                landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST])
        left_shoulder_hip_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
                                                       landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                                       landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW])

        # Right side
        right_elbow_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                                 landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
                                                 landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST])
        right_shoulder_hip_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
                                                        landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                                        landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW])

        # Monitor the arms' movements
        if left_elbow_angle < 60 and right_elbow_angle < 60:  # Threshold for arms pressed up
            if not self.rep_started:
                self.rep_started = True

        if self.rep_started and left_elbow_angle > 90 and right_elbow_angle > 90:  # Threshold for arms back at start position
            self.rep_count += 1
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")
            self.rep_started = False

        # Provide feedback
        if left_elbow_angle < 60 and right_elbow_angle < 60:
            self.feedback_label.config(text="Good! Press your arms up and slightly forward.")
        elif left_elbow_angle > 90 and right_elbow_angle > 90:
            self.feedback_label.config(text="Great! Lower your arms back to the start position.")
        else:
            self.feedback_label.config(text="Keep your elbows at a 90-degree angle when lowering your arms.")

        # Check shoulder stability
        if left_shoulder_hip_angle < 70 or right_shoulder_hip_angle < 70:
            self.feedback_label.config(
                text="Ensure your back stays in contact with the bench. Avoid excessive arching.")

    def correct_and_count_bicep_curls(self, landmarks):
        # Left side
        left_elbow_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                                landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
                                                landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST])
        left_shoulder_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
                                                   landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                                   landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW])

        # Right side
        right_elbow_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                                 landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
                                                 landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST])
        right_shoulder_angle = self.calculate_angle(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
                                                    landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                                    landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW])

        # Monitor the arms' movements
        if left_elbow_angle < 45 and right_elbow_angle < 45:  # Threshold for arms fully curled up
            if not self.rep_started:
                self.rep_started = True

        if self.rep_started and left_elbow_angle > 160 and right_elbow_angle > 160:  # Threshold for arms fully extended
            self.rep_count += 1
            self.rep_count_label.config(text=f"Reps: {self.rep_count}")
            self.rep_started = False

        # Provide feedback
        if left_elbow_angle < 45 and right_elbow_angle < 45:
            self.feedback_label.config(text="Good! Fully curl your arms up.")
        elif left_elbow_angle > 160 and right_elbow_angle > 160:
            self.feedback_label.config(text="Great! Lower your arms fully to the starting position.")
        else:
            self.feedback_label.config(text="Keep your elbows close to your body. Avoid moving your shoulders.")

        # Check for shoulder movement
        if left_shoulder_angle > 80 or right_shoulder_angle > 80:
            self.feedback_label.config(text="Keep your shoulders stable. Do not lift them during the curl.")

    def quit_app(self):
        self.cap.release()
        self.root.destroy()

    def on_close(self):
        self.quit_app()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseCorrectionApp(root)
    root.mainloop()