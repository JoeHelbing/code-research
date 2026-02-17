from __future__ import annotations

import numpy as np


def min_max_normalize(values: np.ndarray) -> np.ndarray:
    """Scale values into [0, 1] with deterministic zero fallback."""
    arr = np.asarray(values, dtype=float)
    lo, hi = float(np.min(arr)), float(np.max(arr))
    if hi == lo:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)
