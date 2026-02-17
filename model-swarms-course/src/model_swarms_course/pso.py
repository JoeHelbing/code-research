from __future__ import annotations

import numpy as np


def rastrigin(x: np.ndarray) -> float:
    """Rastrigin function with global minimum at the origin."""
    n = len(x)
    return float(10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))


def model_swarms_velocity_update(
    current_velocity: np.ndarray,
    current_position: np.ndarray,
    personal_best: np.ndarray,
    global_best: np.ndarray,
    global_worst: np.ndarray,
    inertia: float = 0.2,
    cognitive_coeff: float = 0.3,
    social_coeff: float = 0.4,
    repel_coeff: float = 0.1,
    use_randomness: bool = True,
) -> np.ndarray:
    """Compute one Model Swarms velocity update (Algorithm 1 style)."""
    if use_randomness:
        r_v, r_p, r_g, r_w = np.random.random(4)
    else:
        r_v = r_p = r_g = r_w = 1.0

    w_inertia = r_v * inertia
    w_cognitive = r_p * cognitive_coeff
    w_social = r_g * social_coeff
    w_repel = r_w * repel_coeff
    coeff_sum = w_inertia + w_cognitive + w_social + w_repel
    if coeff_sum == 0:
        return np.zeros_like(current_velocity)

    return (
        w_inertia * current_velocity
        + w_cognitive * (personal_best - current_position)
        + w_social * (global_best - current_position)
        - w_repel * (global_worst - current_position)
    ) / coeff_sum


def expand_population(
    expert_positions: list[np.ndarray], target_count: int, seed: int = 42
) -> list[np.ndarray]:
    """Expand experts via interpolation/extrapolation with t ~ U(0, 2)."""
    if len(expert_positions) < 2:
        raise ValueError("Need at least two experts to expand population.")

    rng = np.random.default_rng(seed)
    children = [np.array(x, copy=True) for x in expert_positions]
    n_existing = len(expert_positions)

    while len(children) < target_count:
        idx1, idx2 = rng.choice(n_existing, size=2, replace=False)
        t = float(rng.random() * 2.0)
        parent1, parent2 = expert_positions[idx1], expert_positions[idx2]
        child = t * parent1 + (1 - t) * parent2
        children.append(np.array(child, copy=True))

    return children
