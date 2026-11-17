from __future__ import annotations

import cv2
import numpy as np


def difference_hash(image: np.ndarray, width: int = 9, height: int = 8) -> int:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
    bits = resized[:, 1:] > resized[:, :-1]
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return value


def hash_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def color_histogram(image: np.ndarray, size: tuple[int, int] = (160, 90)) -> np.ndarray:
    small = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    histogram = cv2.calcHist([hsv], [0, 1], None, [24, 16], [0, 180, 0, 256])
    cv2.normalize(histogram, histogram)
    return histogram


def scene_difference(previous: np.ndarray | None, current: np.ndarray) -> float:
    if previous is None:
        return 0.0
    return float(cv2.compareHist(previous, current, cv2.HISTCMP_BHATTACHARYYA))
