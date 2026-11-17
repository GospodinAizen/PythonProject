import cv2
import numpy as np


def visual_signature(frame: np.ndarray, width: int = 160, height: int = 90):
    """Return normalized HSV histogram, 64-bit difference hash, and hex hash."""
    small = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [24, 16], [0, 180, 0, 256])
    cv2.normalize(hist, hist, alpha=1.0, norm_type=cv2.NORM_L1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hash_img = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
    bits = hash_img[:, 1:] > hash_img[:, :-1]
    value = 0
    for bit in bits.flat:
        value = (value << 1) | int(bit)
    return hist, value, f"{value:016x}"


def histogram_distance(previous: np.ndarray | None, current: np.ndarray) -> float:
    if previous is None:
        return 0.0
    return float(cv2.compareHist(previous, current, cv2.HISTCMP_BHATTACHARYYA))


def hash_distance(left: int | None, right: int) -> int:
    return 64 if left is None else (left ^ right).bit_count()
