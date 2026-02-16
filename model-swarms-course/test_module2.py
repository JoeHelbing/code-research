#!/usr/bin/env python3
"""Test Module 2: PSO Implementation"""
import numpy as np

def rastrigin(x):
    """Rastrigin function: many local minima, global min at origin."""
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))

class ParticleSwarmOptimizer:
    def __init__(self, func, dim, n_particles, bounds,
                 w=0.7, c1=1.5, c2=1.5, max_iter=100):
        self.func = func
        self.dim = dim
        self.n_particles = n_particles
        self.bounds = bounds
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.max_iter = max_iter

        self.positions = np.random.uniform(
            bounds[0], bounds[1], (n_particles, dim)
        )

        velocity_range = (bounds[1] - bounds[0]) * 0.1
        self.velocities = np.random.uniform(
            -velocity_range, velocity_range, (n_particles, dim)
        )

        self.scores = np.array([func(p) for p in self.positions])

        self.personal_best_positions = self.positions.copy()
        self.personal_best_scores = self.scores.copy()

        best_idx = np.argmin(self.scores)
        self.global_best_position = self.positions[best_idx].copy()
        self.global_best_score = self.scores[best_idx]

        self.history = {
            'global_best_scores': [self.global_best_score],
            'positions': [self.positions.copy()],
            'particle_scores': [self.scores.copy()]
        }

    def step(self):
        for i in range(self.n_particles):
            r1 = np.random.random(self.dim)
            r2 = np.random.random(self.dim)

            self.velocities[i] = (
                self.w * self.velocities[i]
                + self.c1 * r1 * (self.personal_best_positions[i]
                                   - self.positions[i])
                + self.c2 * r2 * (self.global_best_position
                                   - self.positions[i])
            )

            self.positions[i] += self.velocities[i]

            self.positions[i] = np.clip(
                self.positions[i], self.bounds[0], self.bounds[1]
            )

            score = self.func(self.positions[i])
            self.scores[i] = score

            if score < self.personal_best_scores[i]:
                self.personal_best_scores[i] = score
                self.personal_best_positions[i] = self.positions[i].copy()

                if score < self.global_best_score:
                    self.global_best_score = score
                    self.global_best_position = self.positions[i].copy()

        self.history['global_best_scores'].append(self.global_best_score)
        self.history['positions'].append(self.positions.copy())
        self.history['particle_scores'].append(self.scores.copy())

    def optimize(self):
        for iteration in range(self.max_iter):
            self.step()
        return self.global_best_position, self.global_best_score


# Run PSO on the 2D Rastrigin function
np.random.seed(42)
pso = ParticleSwarmOptimizer(
    func=rastrigin,
    dim=2,
    n_particles=20,
    bounds=(-5.12, 5.12),
    w=0.7,
    c1=1.5,
    c2=1.5,
    max_iter=50
)
best_pos, best_score = pso.optimize()
print(f"Best position: {best_pos}")
print(f"Best score: {best_score:.6f}")
print(f"Global optimum: [0, 0] with score 0.0")

# Verify it found something reasonable
assert best_score < 5.0, f"PSO failed to converge: score={best_score}"
assert len(pso.history['global_best_scores']) == 51, "History length mismatch"
assert pso.history['global_best_scores'][-1] <= pso.history['global_best_scores'][0], \
    "Global best should not increase (minimizing)"

print("\n--- Module 2 PSO tests PASSED ---")
