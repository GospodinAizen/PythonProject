import numpy as np

from video_learning.vision import hash_distance, histogram_distance, visual_signature


def test_identical_frames_have_same_hash():
    frame = np.zeros((180, 320, 3), dtype=np.uint8)
    _, first, _ = visual_signature(frame)
    _, second, _ = visual_signature(frame.copy())
    assert hash_distance(first, second) == 0


def test_identical_histograms_have_zero_distance():
    frame = np.full((180, 320, 3), 127, dtype=np.uint8)
    hist, _, _ = visual_signature(frame)
    assert histogram_distance(hist, hist.copy()) == 0.0


def test_hash_distance_is_bounded():
    a = np.zeros((180, 320, 3), dtype=np.uint8)
    b = np.full((180, 320, 3), 255, dtype=np.uint8)
    _, ha, _ = visual_signature(a)
    _, hb, _ = visual_signature(b)
    assert 0 <= hash_distance(ha, hb) <= 64
