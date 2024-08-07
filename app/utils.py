# utils.py
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import mediapipe as mp
import os
from django.conf import settings

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

model_path = os.path.join(settings.BASE_DIR, 'app', 'model_alpha_1.h5')
model = load_model(model_path)

def load_labels(csv_file):
    try:
        df = pd.read_csv(csv_file, header=None)
        labels = df.iloc[:, 0].unique().tolist()
        return labels
    except Exception as e:
        print(f"Error loading labels: {e}")
        return []

labels_path = os.path.join(settings.BASE_DIR, 'app', 'data_alpha_1.csv')
labels = load_labels(labels_path)

def normalize(vector_axis):
    vector_axis = np.array(vector_axis)
    axrange = vector_axis.max() - vector_axis.min()
    return (vector_axis - vector_axis.min()) / axrange

def preprocess_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            vector_x, vector_y, vector_z = [], [], []
            for landmark in hand_landmarks.landmark:
                vector_x.append(landmark.x)
                vector_y.append(landmark.y)
                vector_z.append(landmark.z)
            
            normalized_vector_x = normalize(vector_x)
            normalized_vector_y = normalize(vector_y)
            normalized_vector_z = normalize(vector_z)
            
            vector = np.concatenate([normalized_vector_x, normalized_vector_y, normalized_vector_z])
            return vector, result.multi_hand_landmarks
    return None, None

def predict(vector):
    vector = vector.reshape(1, -1)
    predictions = model.predict(vector)
    predicted_probabilities = predictions[0]
    top_indices = np.argsort(predicted_probabilities)[-5:]
    
    valid_indices = [i for i in top_indices[::-1] if i < len(labels)]
    predicted_labels = [labels[i] for i in valid_indices]
    predicted_probabilities = [predicted_probabilities[i] * 100 for i in valid_indices]
    
    return predicted_labels, predicted_probabilities

def display_predictions(image, labels, probabilities):
    for i in range(len(labels)):
        cv2.putText(image, f"{labels[i]}: {probabilities[i]:.2f}%", (50, 100 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

def generate_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        vector, hand_landmarks = preprocess_image(frame)
        if vector is not None:
            predicted_labels, predicted_probabilities = predict(vector)
            display_predictions(frame, predicted_labels, predicted_probabilities)
            for landmarks in hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode image.")
            break
        
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

def generate_webcam_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Failed to capture image.")
            break
        
        vector, hand_landmarks = preprocess_image(frame)
        if vector is not None:
            predicted_labels, predicted_probabilities = predict(vector)
            display_predictions(frame, predicted_labels, predicted_probabilities)
            for landmarks in hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode image.")
            break
        
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()
