import numpy as np

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def eye_box(landmarks, idxs, w, h, pad=0.6):
    pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in idxs]
    xs, ys = zip(*pts)

    x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
    bw, bh = x2 - x1, y2 - y1

    return (
        max(int(x1 - bw * pad), 0),
        max(int(y1 - bh * pad), 0),
        min(int(x2 + bw * pad), w),
        min(int(y2 + bh * pad), h),
    )

def eye_vertical_position(landmarks):
    return np.mean([landmarks[i].y for i in LEFT_EYE + RIGHT_EYE])
