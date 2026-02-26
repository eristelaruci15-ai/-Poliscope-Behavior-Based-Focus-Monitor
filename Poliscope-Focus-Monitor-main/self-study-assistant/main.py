import cv2
import time
import sys
import numpy as np
from PIL import Image

from vision import VisionTracker
from state_manager import StateManager, ENGAGED, DISTRACTED, INACTIVE
from voice import VoicePlayer
from gaze import eye_box, eye_vertical_position

# ================== UI CONFIG ==================
WINDOW_W = 1280
WINDOW_H = 800
TOP_BAR_H = 90
PADDING = 20

BG_COLOR = (28, 28, 28)
PANEL_BG = (18, 18, 18)

STATE_COLORS = {
    ENGAGED: (90, 180, 90),
    DISTRACTED: (220, 160, 80),
    INACTIVE: (200, 80, 80)
}

STATE_EXPLANATION = {
    ENGAGED: "Eyes aligned with screen",
    DISTRACTED: "Gaze or head turned away",
    INACTIVE: "User not detected"
}

# Robot behavior tuning
ANIM_SPEED = 1.5
LOOP_PAUSE = {
    ENGAGED: 0.5,
    DISTRACTED: 1.2,
    INACTIVE: 2.0
}

ROBOT_OPACITY = {
    ENGAGED: 1.0,
    DISTRACTED: 0.85,
    INACTIVE: 0.6
}

ROBOT_SCALE = 0.9  # keep robot size calm

# ================== HELPERS ==================
def load_gif(path):
    img = Image.open(path)
    frames, durations = [], []
    try:
        while True:
            frames.append(np.array(img.convert("RGB")))
            durations.append(img.info.get("duration", 100) / 1000)
            img.seek(len(frames))
    except EOFError:
        pass
    return frames, durations


def apply_opacity(img, opacity):
    bg = np.zeros_like(img)
    return cv2.addWeighted(img, opacity, bg, 1 - opacity, 0)


# ================== MAIN ==================
def main():
    session_start_time = None
    show_overlays = False

    animations = {
        ENGAGED: load_gif("animations/engaged.gif"),
        DISTRACTED: load_gif("animations/distracted.gif"),
        INACTIVE: load_gif("animations/inactive.gif"),
    }

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        sys.exit("Webcam error")

    vision = VisionTracker()
    state_mgr = StateManager()
    voice = VoicePlayer("audio")

    frame_idx = 0
    last_anim_time = time.time()
    last_state = None

    cv2.namedWindow("Poliscope", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Poliscope", WINDOW_W, WINDOW_H)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break 

            if session_start_time is None:
                session_start_time = time.time()

            frame = cv2.flip(frame, 1)
            cam_h, cam_w, _ = frame.shape

            canvas = np.full((WINDOW_H, WINDOW_W, 3), BG_COLOR, np.uint8)

            content_h = WINDOW_H - TOP_BAR_H - PADDING * 2
            panel_w = (WINDOW_W - PADDING * 3) // 2
            y0 = TOP_BAR_H + PADDING

            # ================== USER PANEL ==================
            user_panel = cv2.resize(frame, (panel_w, content_h))
            canvas[y0:y0+content_h, PADDING:PADDING+panel_w] = user_panel

            landmarks, yaw, pitch = vision.process(frame)
            face_present = landmarks is not None
            eye_y = eye_vertical_position(landmarks) if face_present else None

            if face_present and show_overlays:
                xs = [int(l.x * panel_w) for l in landmarks]
                ys = [int(l.y * content_h) for l in landmarks]
                cv2.rectangle(
                    canvas,
                    (PADDING + min(xs), y0 + min(ys)),
                    (PADDING + max(xs), y0 + max(ys)),
                    (180, 180, 80),
                    1
                )

            # ================== STATE ==================
            state = state_mgr.update(face_present, yaw, pitch, eye_y)

            if state != last_state:
                voice.play(state)
                frame_idx = 0
                last_anim_time = time.time()
                last_state = state

            frames, durations = animations[state]

            if time.time() - last_anim_time >= durations[frame_idx] * ANIM_SPEED:
                frame_idx += 1
                if frame_idx >= len(frames):
                    frame_idx = 0
                    time.sleep(LOOP_PAUSE[state])
                last_anim_time = time.time()

            # ================== ROBOT PANEL (FULL CONTAINER) ==================
            robot_panel_x1 = PADDING * 2 + panel_w
            robot_panel_x2 = robot_panel_x1 + panel_w

            cv2.rectangle(
                canvas,
                (robot_panel_x1, y0),
                (robot_panel_x2, y0 + content_h),
                PANEL_BG,
                -1
            )

            # Divider
            cv2.line(
                canvas,
                (robot_panel_x1 - 10, y0),
                (robot_panel_x1 - 10, y0 + content_h),
                (40, 40, 40),
                1
            )

            rw = int(panel_w * ROBOT_SCALE)
            rh = int(content_h * ROBOT_SCALE)

            robot_img = cv2.resize(frames[frame_idx], (rw, rh))
            robot_img = apply_opacity(robot_img, ROBOT_OPACITY[state])

            rx = robot_panel_x1 + (panel_w - rw) // 2
            ry = y0 + (content_h - rh) // 2
            canvas[ry:ry+rh, rx:rx+rw] = robot_img

            # ================== TOP BAR ==================
            cv2.rectangle(canvas, (0, 0), (WINDOW_W, TOP_BAR_H), STATE_COLORS[state], -1)

            elapsed = int(time.time() - session_start_time)
            mm, ss = divmod(elapsed, 60)

            # Left
            cv2.putText(canvas, "Poliscope", (20, 34),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.15, (255, 255, 255), 2)
            cv2.putText(canvas, "Behavior-Based Focus Monitor", (20, 62),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (235, 235, 235), 1)

            # Center
            cv2.circle(canvas, (WINDOW_W // 2 - 120, 45), 7, (255, 255, 255), -1)
            cv2.putText(canvas, state, (WINDOW_W // 2 - 95, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            cv2.putText(canvas, STATE_EXPLANATION[state],
                        (WINDOW_W // 2 - 120, 78),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1)

            # Right
            cv2.putText(canvas, f"Session {mm:02}:{ss:02}",
                        (WINDOW_W - 240, 34),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            status = "CALIBRATED" if state_mgr.calibrated else "NOT CALIBRATED"
            cv2.putText(canvas, status,
                        (WINDOW_W - 240, 62),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 1)

            cv2.imshow("Poliscope", canvas)

            key = cv2.waitKey(1)
            if key == ord("c") and face_present:
                state_mgr.calibrate(yaw, pitch, eye_y)
            if key == ord("d"):
                show_overlays = not show_overlays
            if key in (27, ord("q")):
                break

    finally:
        cap.release()

        # ================== SESSION SUMMARY ==================
        summary = np.full((WINDOW_H, WINDOW_W, 3), BG_COLOR, np.uint8)
        total = sum(state_mgr.stats.values()) or 1

        cv2.putText(summary, "Session Summary",
                    (WINDOW_W // 2 - 180, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2)

        y = 220
        for s in (ENGAGED, DISTRACTED, INACTIVE):
            pct = state_mgr.stats[s] / total * 100
            cv2.putText(summary,
                        f"{s}: {pct:.1f}%",
                        (WINDOW_W // 2 - 120, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        STATE_COLORS[s], 2)
            y += 60

        cv2.putText(summary, "Press any key to exit",
                    (WINDOW_W // 2 - 160, y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

        cv2.imshow("Poliscope", summary)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
