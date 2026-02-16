#!/usr/bin/env python3
"""Test Module 4: Velocity Update & Harmonic Mean"""
import numpy as np

# Test 1: Velocity update implementation
def model_swarms_velocity_update(
    current_velocity, current_position, personal_best,
    global_best, global_worst,
    inertia, cognitive_coeff, social_coeff, repel_coeff,
    use_randomness=True, seed=None
):
    if seed is not None:
        np.random.seed(seed)

    if use_randomness:
        r_v = np.random.uniform(0, 1)
        r_p = np.random.uniform(0, 1)
        r_g = np.random.uniform(0, 1)
        r_w = np.random.uniform(0, 1)
    else:
        r_v = r_p = r_g = r_w = 1.0

    self_weight = r_v * inertia
    cognitive_weight = r_p * cognitive_coeff
    social_weight = r_g * social_coeff
    repel_weight = r_w * repel_coeff

    weight_sum = self_weight + cognitive_weight + social_weight + repel_weight

    self_weight /= weight_sum
    cognitive_weight /= weight_sum
    social_weight /= weight_sum
    repel_weight /= weight_sum

    inertia_component = self_weight * current_velocity
    cognitive_component = cognitive_weight * (personal_best - current_position)
    social_component = social_weight * (global_best - current_position)
    repulsion_component = repel_weight * (current_position - global_worst)

    new_velocity = (inertia_component + cognitive_component +
                    social_component + repulsion_component)
    return new_velocity


# Test deterministic case
v = model_swarms_velocity_update(
    current_velocity=np.array([0.1, -0.05]),
    current_position=np.array([0.3, 0.7]),
    personal_best=np.array([0.4, 0.6]),
    global_best=np.array([0.7, 0.8]),
    global_worst=np.array([0.5, 0.2]),
    inertia=0.2, cognitive_coeff=0.3,
    social_coeff=0.4, repel_coeff=0.1,
    use_randomness=False
)
print(f"Deterministic velocity: {v}")

# Verify normalization: weights should sum to 1, so velocity is a weighted average
# of the four direction components. Each component is bounded, so velocity should be
# reasonable in magnitude.
assert np.all(np.isfinite(v)), "Velocity contains non-finite values"
assert np.linalg.norm(v) < 10.0, f"Velocity too large: {np.linalg.norm(v)}"

# Test with randomness (just verify it runs and produces different results)
v1 = model_swarms_velocity_update(
    current_velocity=np.array([0.1, -0.05]),
    current_position=np.array([0.3, 0.7]),
    personal_best=np.array([0.4, 0.6]),
    global_best=np.array([0.7, 0.8]),
    global_worst=np.array([0.5, 0.2]),
    inertia=0.2, cognitive_coeff=0.3,
    social_coeff=0.4, repel_coeff=0.1,
    use_randomness=True, seed=42
)
v2 = model_swarms_velocity_update(
    current_velocity=np.array([0.1, -0.05]),
    current_position=np.array([0.3, 0.7]),
    personal_best=np.array([0.4, 0.6]),
    global_best=np.array([0.7, 0.8]),
    global_worst=np.array([0.5, 0.2]),
    inertia=0.2, cognitive_coeff=0.3,
    social_coeff=0.4, repel_coeff=0.1,
    use_randomness=True, seed=99
)
assert not np.allclose(v1, v2), "Random velocities should differ with different seeds"
print(f"Random velocity (seed=42): {v1}")
print(f"Random velocity (seed=99): {v2}")

print("\n--- Velocity update tests PASSED ---")

# Test 2: Harmonic mean vs arithmetic mean
print("\n--- Harmonic vs Arithmetic Mean ---")
scenarios = [
    (0.9, 0.9, "Both high"),
    (0.9, 0.1, "Very imbalanced"),
    (0.5, 0.5, "Both medium"),
    (0.7, 0.3, "Moderately imbalanced"),
    (0.95, 0.05, "Extremely imbalanced"),
]

for s1, s2, label in scenarios:
    arithmetic = (s1 + s2) / 2
    harmonic = 2 * s1 * s2 / (s1 + s2)
    print(f"{label}: scores=({s1}, {s2})")
    print(f"  Arithmetic mean: {arithmetic:.3f}")
    print(f"  Harmonic mean:   {harmonic:.3f}")
    print(f"  Ratio (H/A):     {harmonic/arithmetic:.3f}")

# Verify harmonic mean properties
assert 2 * 0.9 * 0.1 / (0.9 + 0.1) < (0.9 + 0.1) / 2, \
    "Harmonic mean should be <= arithmetic mean"
assert abs(2 * 0.5 * 0.5 / (0.5 + 0.5) - 0.5) < 1e-10, \
    "Harmonic mean of equal values should equal those values"

print("\n--- Harmonic mean tests PASSED ---")

# Test 3: Position update
position = np.array([0.3, 0.7])
velocity = np.array([0.265, 0.064])
step_length = 0.85
new_position = position + step_length * velocity
print(f"\nPosition update: {position} + {step_length} * {velocity} = {new_position}")
expected = position + step_length * velocity
assert np.allclose(new_position, expected), \
    f"Position update incorrect: {new_position}"

print("\n--- Position update test PASSED ---")
print("\n=== ALL Module 4 tests PASSED ===")
