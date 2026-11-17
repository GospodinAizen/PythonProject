import numpy as np
import pytest

from sololeveling_video.config import PipelineConfig
from sololeveling_video.vision import difference_hash, hash_distance


def test_difference_hash_is_stable():
    image = np.zeros((90, 160, 3), dtype=np.uint8)
    assert difference_hash(image) == difference_hash(image.copy())


def test_hash_distance():
    assert hash_distance(1234, 1234) == 0
    assert hash_distance(0b0001, 0b0011) == 1


def test_default_config_is_valid():
    PipelineConfig().validate()


def test_analysis_rate_must_cover_sampling_rate():
    with pytest.raises(ValueError, match="analysis_fps"):
        PipelineConfig(sample_fps=3, analysis_fps=2).validate()
