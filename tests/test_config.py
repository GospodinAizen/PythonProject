import pytest

from video_learning.config import PipelineConfig


def test_defaults_are_valid():
    PipelineConfig().validate()


@pytest.mark.parametrize("kwargs", [
    {"sample_fps": 0}, {"scene_threshold": 0}, {"scene_threshold": 1.1},
    {"jpeg_quality": 0}, {"duplicate_hash_distance": 65},
])
def test_invalid_values_fail(kwargs):
    with pytest.raises(ValueError):
        PipelineConfig(**kwargs).validate()
