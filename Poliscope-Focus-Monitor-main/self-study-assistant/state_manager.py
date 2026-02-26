ENGAGED = "ENGAGED"
DISTRACTED = "DISTRACTED"
INACTIVE = "INACTIVE"

class StateManager:
    def __init__(self):
        self.calibrated = False
        self.base_yaw = 0
        self.base_pitch = 0
        self.base_eye_y = 0

        self.yaw_tol = 0.03
        self.pitch_tol = 0.04
        self.eye_tol = 0.04

        self.state = INACTIVE
        self.stats = {ENGAGED: 0, DISTRACTED: 0, INACTIVE: 0}

    def calibrate(self, yaw, pitch, eye_y):
        self.base_yaw = yaw
        self.base_pitch = pitch
        self.base_eye_y = eye_y
        self.calibrated = True
        print("✅ CALIBRATION COMPLETE — ENGAGED BASELINE SET")

    def focus_level(self, yaw, pitch, eye_y):
        if not self.calibrated:
            return 0.0

        dy = abs(yaw - self.base_yaw) / self.yaw_tol
        dp = abs(pitch - self.base_pitch) / self.pitch_tol
        de = abs(eye_y - self.base_eye_y) / self.eye_tol

        score = 1 - min(1, (dy + dp + de) / 3)
        return max(0.0, score)

    def update(self, face_present, yaw, pitch, eye_y):
        if not face_present:
            self.state = INACTIVE
        elif not self.calibrated:
            self.state = DISTRACTED
        else:
            focused = (
                abs(yaw - self.base_yaw) < self.yaw_tol and
                abs(pitch - self.base_pitch) < self.pitch_tol and
                abs(eye_y - self.base_eye_y) < self.eye_tol
            )
            self.state = ENGAGED if focused else DISTRACTED

        self.stats[self.state] += 1
        return self.state
