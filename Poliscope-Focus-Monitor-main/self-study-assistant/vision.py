import cv2
import mediapipe as mp

class VisionTracker:
    def __init__(self):
        self.mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)

        if not result.multi_face_landmarks:
            return None, None, None

        lm = result.multi_face_landmarks[0].landmark

        # Head pose landmarks
        left = lm[234]
        right = lm[454]
        top = lm[10]
        bottom = lm[152]

        yaw = right.x - left.x
        pitch = top.y - bottom.y

        return lm, yaw, pitch
