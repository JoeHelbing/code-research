from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from safetensors.numpy import load_file, save_file

StateDict = dict[str, np.ndarray]


def merge_lora_state_dicts(weights: list[float], adapters: list[StateDict]) -> StateDict:
    """Merge in-memory LoRA adapter state dicts with weighted sum."""
    if not adapters:
        raise ValueError("At least one adapter is required for merging.")
    if len(weights) != len(adapters):
        raise ValueError("weights and adapters must have the same length.")

    keys = set(adapters[0].keys())
    for adapter in adapters[1:]:
        if set(adapter.keys()) != keys:
            raise ValueError("All adapters must share the same tensor keys.")

    merged: StateDict = {}
    for key in keys:
        acc = np.zeros_like(adapters[0][key], dtype=np.float32)
        for weight, adapter in zip(weights, adapters, strict=True):
            acc = acc + np.float32(weight) * adapter[key].astype(np.float32)
        merged[key] = acc
    return merged


def lora_merge_from_paths(
    weights: list[float], adapter_paths: list[str], output_path: str
) -> StateDict:
    """Merge adapters from disk and write merged adapter_model.safetensors."""
    adapters = []
    for path in adapter_paths:
        safetensors_file = os.path.join(path, "adapter_model.safetensors")
        adapters.append(load_file(safetensors_file))

    merged = merge_lora_state_dicts(weights=weights, adapters=adapters)
    os.makedirs(output_path, exist_ok=True)
    save_file(merged, os.path.join(output_path, "adapter_model.safetensors"))
    return merged


def create_dummy_adapter(path: str, seed: int = 42) -> StateDict:
    """Create small deterministic adapter weights for tests or notebook demos."""
    rng = np.random.default_rng(seed)
    state_dict: StateDict = {
        "layer.0.lora_A.weight": rng.standard_normal((16, 32), dtype=np.float32),
        "layer.0.lora_B.weight": rng.standard_normal((32, 16), dtype=np.float32),
        "layer.1.lora_A.weight": rng.standard_normal((16, 32), dtype=np.float32),
        "layer.1.lora_B.weight": rng.standard_normal((32, 16), dtype=np.float32),
    }
    Path(path).mkdir(parents=True, exist_ok=True)
    save_file(state_dict, os.path.join(path, "adapter_model.safetensors"))
    return state_dict
