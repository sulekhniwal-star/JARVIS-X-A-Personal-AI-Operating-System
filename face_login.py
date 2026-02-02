from typing import Optional, Any
import cv2  # type: ignore
import os
import numpy as np

class FaceLogin:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(  # type: ignore
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )
        self.ref_path = "reference_face.jpg"

    def _capture_face(self, message: str = "Look at the camera") -> Optional[Any]:
        cap = cv2.VideoCapture(0)
        face_img = None

        print(message)

        for _ in range(100):
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))
                break

        cap.release()
        return face_img

    def authenticate(self) -> bool:
        if not os.path.exists(self.ref_path):
            print("No reference face found. Capturing now...")
            face = self._capture_face("Capturing reference face...")
            if face is None:
                print("Failed to capture reference face.")
                return False
            cv2.imwrite(self.ref_path, face)
            print("Reference face saved.")
            return True

        ref_face = cv2.imread(self.ref_path, cv2.IMREAD_GRAYSCALE)
        live_face = self._capture_face("Authenticating...")

        if live_face is None:
            print("No face detected.")
            return False

        diff = np.mean((ref_face.astype("float") - live_face.astype("float")) ** 2)  # type: ignore

        print("Face difference score:", diff)  # type: ignore

        return bool(diff < 2000)  # type: ignore
