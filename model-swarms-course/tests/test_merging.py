from pathlib import Path

import numpy as np
from safetensors.numpy import load_file

from model_swarms_course.merging import (
    create_dummy_adapter,
    lora_merge_from_paths,
    merge_lora_state_dicts,
)


def test_merge_lora_state_dicts_weighted_sum() -> None:
    a = {"x": np.array([1.0, 2.0], dtype=np.float32)}
    b = {"x": np.array([3.0, 4.0], dtype=np.float32)}

    merged = merge_lora_state_dicts(weights=[0.25, 0.75], adapters=[a, b])
    np.testing.assert_allclose(merged["x"], np.array([2.5, 3.5], dtype=np.float32))


def test_lora_merge_from_paths_writes_safetensor(tmp_path: Path) -> None:
    p1 = tmp_path / "a1"
    p2 = tmp_path / "a2"
    out = tmp_path / "out"
    create_dummy_adapter(str(p1), seed=11)
    create_dummy_adapter(str(p2), seed=13)

    merged = lora_merge_from_paths([0.5, 0.5], [str(p1), str(p2)], str(out))

    saved = load_file(str(out / "adapter_model.safetensors"))
    assert set(saved.keys()) == set(merged.keys())
