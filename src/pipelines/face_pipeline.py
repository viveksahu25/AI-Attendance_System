
import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st
from pkg_resources import resource_filename

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()

    # Ensure image is a NumPy RGB image
    image_np = np.ascontiguousarray(image_np, dtype=np.uint8)

    faces = detector(image_np, 1)
    encodings = []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(
            image_np, shape
        )
        encodings.append(np.array(face_descriptor))

    return encodings


@st.cache_data
def get_training_data():
    student_db = get_all_students()

    X = []
    y = []

    if not student_db:
        return [], []

    for student in student_db:
        embedding = student.get("face_embedding")
        student_id = student.get("student_id")

        if embedding and student_id is not None:
            X.append(np.array(embedding, dtype=float))
            y.append(student_id)

    return X, y


@st.cache_resource
def get_trained_model():
    X, y = get_training_data()

    if not X:
        return None

    # SVC needs at least two different classes
    if len(set(y)) < 2:
        return {
            "clf": None,
            "X": X,
            "y": y
        }

    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    clf.fit(X, y)

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


def train_classifier():
    get_training_data.clear()
    get_trained_model.clear()

    model_data = get_trained_model()
    return bool(model_data and model_data["X"])


def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    X = model_data["X"]
    y = model_data["y"]
    clf = model_data["clf"]

    all_students = sorted(set(y))

    for encoding in encodings:
        if clf is not None:
            predicted_id = clf.predict([encoding])[0]
        else:
            predicted_id = all_students[0]

        # Compare only against embeddings for the predicted student
        student_embeddings = [
            np.asarray(X[i], dtype=float)
            for i in range(len(y))
            if y[i] == predicted_id
        ]

        if not student_embeddings:
            continue

        best_match_score = min(
            np.linalg.norm(student_embedding - encoding)
            for student_embedding in student_embeddings
        )

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)