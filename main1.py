import cv2
import mediapipe as mp
import os
import pygame
import time
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk   # for embedding OpenCV frames in Tkinter


# Sound System

pygame.mixer.init()

hello_sound = r"C:\Users\ASUS\Desktop\speakshand\hello.wav"
th_sound = r"C:\Users\ASUS\Desktop\speakshand\thankyou.wav"
help_me=r"C:\Users\ASUS\Desktop\speakshand\help me.wav"
i_want_to_say=r"C:\Users\ASUS\Desktop\speakshand\i want to say.wav"
like_it=r"C:\Users\ASUS\Desktop\speakshand\i like it.wav"
call_me=r"C:\Users\ASUS\Desktop\speakshand\call me.wav"
well_done=r"C:\Users\ASUS\Desktop\speakshand\well done.wav"
wait_s=r"C:\Users\ASUS\Desktop\speakshand\wait.wav"
# Suppress mediapipe logs
os.environ["GLOG_minloglevel"] = "2"

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

FINGER_TIPS = [4, 8, 12, 16, 20]


# cooldown
last_played = {"hello": 0, "thank": 0, "help me" :0, "i want to say" :0,  "i like it" :0, "call me":0,  "well done":0, "wait s":0}
cooldown = 2  # seconds

def play_sound(file_path, key):
    global last_played
    now = time.time()
    if now - last_played.get(key, 0) > cooldown:
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            last_played[key] = now
        except Exception as e:
            print(f"⚠️ Error playing sound: {e}")


# Gesture Detection 

def fingers_up(hand_landmarks):
    fingers = []
    if hand_landmarks.landmark[FINGER_TIPS[0]].x < hand_landmarks.landmark[FINGER_TIPS[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip in FINGER_TIPS[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def classify_gesture(fingers):
    if fingers == [0,1,1,1,1]:
        play_sound(hello_sound, "hello")
        return "Hello🖐"
    if fingers == [0,1,1,0,0]:
        play_sound(th_sound, "thank")
        return "Thank You ✌️"
    if fingers == [0,0,0,0,0]:
        play_sound(help_me, "help me")
        return "help ✊"
    if fingers == [0,1,0,0,0]:
        play_sound(i_want_to_say, "i want to say")
        return "Point ☝️"
    if fingers == [1,0,0,0,0]:
        play_sound(like_it , "i like it")
        return "i like it 👍"
    if fingers == [0,0,0,0,1]:
        play_sound(call_me, "call me")
        return "Call me 🤙"
    if fingers == [1,1,0,0,1]:
        play_sound(well_done, "well done")
        return "well done🤘"
    if fingers == [0,1,1,1,0]:
        return "Three ✋"
    if fingers == [1,1,1,1,1]:
        play_sound(wait_s, "wait s")
        return "wait✋"
    return "Unknown"

# Camera Loop (runs inside Tkinter)

running = False
cap = None
hands = None

def update_frame():
    global cap, running, hands
    if running and cap is not None:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            gesture_text = "No Hands Detected"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    fingers = fingers_up(hand_landmarks)
                    gesture_text = classify_gesture(fingers)

            # update message row
            message_label.config(text=f"Message: {gesture_text}")

            # convert frame to Tkinter format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

    if running:
        root.after(10, update_frame)  # schedule next frame


# GUI Controls

def start_camera():
    global cap, running, hands
    if not running:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            messagebox.showerror("Error", "❌ Could not open webcam.")
            return
        hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        running = True
        update_frame()

def stop_camera():
    global running, cap, hands
    running = False
    if cap:
        cap.release()
        cap = None
    if hands:
        hands.close()
        hands = None
    video_label.config(image="")  # clear frame
     
# Tkinter GUI

root = tk.Tk()
root.title("Hand Gesture Detection")
root.geometry("700x600")

title_label = tk.Label(root, text="🤖 HandSpeak", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

video_label = tk.Label(root)
video_label.pack()

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="▶ Start Camera", font=("Arial", 12), command=start_camera)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(btn_frame, text="⏹ Stop Camera", font=("Arial", 12), command=stop_camera)
stop_btn.grid(row=0, column=1, padx=10)

exit_btn = tk.Button(btn_frame, text="❌ Exit", font=("Arial", 12), command=root.quit)
exit_btn.grid(row=0, column=2, padx=10)

# Message Row
message_label = tk.Label(root, text="Message: ---", font=("Arial", 14), fg="blue")
message_label.pack(pady=20)

root.mainloop()

pygame.mixer.quit()
