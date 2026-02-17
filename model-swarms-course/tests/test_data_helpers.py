import numpy as np

from model_swarms_course.data import min_max_normalize


def test_min_max_normalize_standard_case() -> None:
    x = np.array([2.0, 4.0, 6.0])
    y = min_max_normalize(x)
    np.testing.assert_allclose(y, np.array([0.0, 0.5, 1.0]))


def test_min_max_normalize_constant_values() -> None:
    x = np.array([3.0, 3.0, 3.0])
    y = min_max_normalize(x)
    np.testing.assert_allclose(y, np.array([0.0, 0.0, 0.0]))
