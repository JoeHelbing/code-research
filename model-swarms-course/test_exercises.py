#!/usr/bin/env python3
"""Test exercises: merge operation tests from Challenge 2"""
import torch
from safetensors.torch import load_file, save_file
import os
import tempfile


def lora_merge(weights, adapter_paths, output_path):
    """
    Merge multiple LoRA adapters with given weights.
    """
    assert len(adapter_paths) == len(weights)

    adapters = []
    for path in adapter_paths:
        sf_path = os.path.join(path, "adapter_model.safetensors")
        adapters.append(load_file(sf_path, device="cpu"))

    keys = list(adapters[0].keys())
    for adapter in adapters[1:]:
        assert list(adapter.keys()) == keys, "Adapter architectures don't match"

    merged = {}
    for key in keys:
        merged[key] = sum(w * adapter[key] for w, adapter in zip(weights, adapters))

    os.makedirs(output_path, exist_ok=True)
    save_file(merged, os.path.join(output_path, "adapter_model.safetensors"))
    return merged


def create_dummy_adapter(path, seed=42):
    """Create a dummy adapter for testing."""
    torch.manual_seed(seed)
    state_dict = {
        "layer.0.lora_A.weight": torch.randn(16, 768),
        "layer.0.lora_B.weight": torch.randn(768, 16),
        "layer.1.lora_A.weight": torch.randn(16, 768),
        "layer.1.lora_B.weight": torch.randn(768, 16),
    }
    os.makedirs(path, exist_ok=True)
    save_file(state_dict, os.path.join(path, "adapter_model.safetensors"))
    return state_dict


def test_identity_merge():
    """Merging a model with itself at weight 0.5 each should return the same model."""
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter_path = os.path.join(tmpdir, "adapter")
        output_path = os.path.join(tmpdir, "output")
        original = create_dummy_adapter(adapter_path)

        lora_merge([0.5, 0.5], [adapter_path, adapter_path], output_path)

        merged = load_file(os.path.join(output_path, "adapter_model.safetensors"))
        for key in original:
            assert torch.allclose(original[key], merged[key], atol=1e-6), \
                f"Identity merge failed for {key}"
    print("PASS: test_identity_merge")


def test_zero_weight():
    """Merging with weight 0 should return zeros."""
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter_path = os.path.join(tmpdir, "adapter")
        output_path = os.path.join(tmpdir, "output")
        create_dummy_adapter(adapter_path)

        lora_merge([0], [adapter_path], output_path)

        merged = load_file(os.path.join(output_path, "adapter_model.safetensors"))
        for key in merged:
            assert torch.allclose(merged[key], torch.zeros_like(merged[key])), \
                f"Zero weight merge failed for {key}"
    print("PASS: test_zero_weight")


def test_subtraction():
    """Merging [1, -1] with same model should give zeros."""
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter_path = os.path.join(tmpdir, "adapter")
        output_path = os.path.join(tmpdir, "output")
        create_dummy_adapter(adapter_path)

        lora_merge([1, -1], [adapter_path, adapter_path], output_path)

        merged = load_file(os.path.join(output_path, "adapter_model.safetensors"))
        for key in merged:
            assert torch.allclose(merged[key], torch.zeros_like(merged[key]),
                                  atol=1e-6), \
                f"Subtraction merge failed for {key}"
    print("PASS: test_subtraction")


def test_linearity():
    """merge([a], [A]) + merge([b], [A]) should equal merge([a+b], [A])."""
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter_path = os.path.join(tmpdir, "adapter")
        out1 = os.path.join(tmpdir, "out1")
        out2 = os.path.join(tmpdir, "out2")
        out3 = os.path.join(tmpdir, "out3")
        create_dummy_adapter(adapter_path)

        lora_merge([0.3], [adapter_path], out1)
        lora_merge([0.7], [adapter_path], out2)
        lora_merge([1.0], [adapter_path], out3)

        merged1 = load_file(os.path.join(out1, "adapter_model.safetensors"))
        merged2 = load_file(os.path.join(out2, "adapter_model.safetensors"))
        merged3 = load_file(os.path.join(out3, "adapter_model.safetensors"))

        for key in merged1:
            combined = merged1[key] + merged2[key]
            assert torch.allclose(combined, merged3[key], atol=1e-5), \
                f"Linearity test failed for {key}"
    print("PASS: test_linearity")


def test_velocity_computation():
    """Test that velocity = personal_best - current works correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pb_path = os.path.join(tmpdir, "personal_best")
        curr_path = os.path.join(tmpdir, "current")
        vel_path = os.path.join(tmpdir, "velocity")

        create_dummy_adapter(pb_path, seed=42)
        create_dummy_adapter(curr_path, seed=123)

        lora_merge([1, -1], [pb_path, curr_path], vel_path)

        pb = load_file(os.path.join(pb_path, "adapter_model.safetensors"))
        curr = load_file(os.path.join(curr_path, "adapter_model.safetensors"))
        vel = load_file(os.path.join(vel_path, "adapter_model.safetensors"))

        for key in pb:
            expected = pb[key] - curr[key]
            assert torch.allclose(expected, vel[key], atol=1e-6), \
                f"Velocity computation failed for {key}"
    print("PASS: test_velocity_computation")


def test_multi_adapter_merge():
    """Test merging 4 adapters (like the velocity combination step)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = []
        for i in range(4):
            path = os.path.join(tmpdir, f"adapter_{i}")
            create_dummy_adapter(path, seed=i * 10)
            paths.append(path)

        output_path = os.path.join(tmpdir, "output")
        weights = [0.2, 0.3, 0.4, 0.1]
        lora_merge(weights, paths, output_path)

        # Verify manually
        adapters = [load_file(os.path.join(p, "adapter_model.safetensors"))
                    for p in paths]
        merged = load_file(os.path.join(output_path, "adapter_model.safetensors"))

        for key in adapters[0]:
            expected = sum(w * a[key] for w, a in zip(weights, adapters))
            assert torch.allclose(expected, merged[key], atol=1e-5), \
                f"Multi-adapter merge failed for {key}"
    print("PASS: test_multi_adapter_merge")


def test_position_update():
    """Test x_new = x + step_length * v (the position update step)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pos_path = os.path.join(tmpdir, "position")
        vel_path = os.path.join(tmpdir, "velocity")
        out_path = os.path.join(tmpdir, "output")

        create_dummy_adapter(pos_path, seed=42)
        create_dummy_adapter(vel_path, seed=99)

        step_length = 0.85
        lora_merge([1, step_length], [pos_path, vel_path], out_path)

        pos = load_file(os.path.join(pos_path, "adapter_model.safetensors"))
        vel = load_file(os.path.join(vel_path, "adapter_model.safetensors"))
        result = load_file(os.path.join(out_path, "adapter_model.safetensors"))

        for key in pos:
            expected = pos[key] + step_length * vel[key]
            assert torch.allclose(expected, result[key], atol=1e-5), \
                f"Position update failed for {key}"
    print("PASS: test_position_update")


if __name__ == "__main__":
    test_identity_merge()
    test_zero_weight()
    test_subtraction()
    test_linearity()
    test_velocity_computation()
    test_multi_adapter_merge()
    test_position_update()
    print("\n=== ALL merge tests PASSED ===")
