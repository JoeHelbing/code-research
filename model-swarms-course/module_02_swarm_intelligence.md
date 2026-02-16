# Module 2: Background — Swarm Intelligence & Particle Swarm Optimization

**Estimated time: 45 minutes**

---

## 2.1 Swarm Intelligence: The Big Idea

Swarm intelligence is a field of AI inspired by the collective behavior of decentralized, self-organized systems — bird flocks, ant colonies, fish schools, bee hives. The key observation is that **simple agents following simple rules can collectively solve complex problems** that no individual agent could solve alone.

A flock of starlings performing a murmuration doesn't have a leader. Each bird follows three rules:
1. **Separation**: Don't crash into nearby birds
2. **Alignment**: Match the velocity of nearby birds
3. **Cohesion**: Move toward the center of nearby birds

From these three simple rules, the entire flock produces complex, adaptive, beautiful patterns. No centralized control required.

Particle Swarm Optimization (PSO), introduced by Kennedy and Eberhart in 1995, takes this principle and applies it to function optimization.

---

## 2.2 Particle Swarm Optimization: The Classic Algorithm

### Setup

You want to find the minimum (or maximum) of a function `f(x)` where `x` is a vector in some high-dimensional space. You don't have access to gradients — just the ability to evaluate `f` at any point.

### The Algorithm

1. **Initialize** N particles at random positions in the search space. Each particle also gets a random velocity.

2. **Evaluate** `f(x_i)` for each particle. Record:
   - `p_i` — the best position this particle has personally visited (personal best)
   - `g` — the best position any particle has visited (global best)

3. **Update velocities** using the PSO equation:

```
v_i ← w * v_i + c1 * r1 * (p_i - x_i) + c2 * r2 * (g - x_i)
```

Where:
- `w` = inertia weight (how much the particle keeps its current direction)
- `c1` = cognitive coefficient (attraction to personal best)
- `c2` = social coefficient (attraction to global best)
- `r1, r2` = random numbers in [0, 1] (stochastic exploration)

4. **Update positions**:

```
x_i ← x_i + v_i
```

5. **Evaluate** all particles again. Update personal bests and global best.

6. **Repeat** steps 3-5 until convergence.

### Intuition for Each Term

| Term | Name | What It Does |
|------|------|-------------|
| `w * v_i` | Inertia | Keeps the particle moving in its current direction. Prevents instant convergence. Encourages exploration. |
| `c1 * r1 * (p_i - x_i)` | Cognitive | Pulls the particle back toward the best place it personally found. "I remember this was good." |
| `c2 * r2 * (g - x_i)` | Social | Pulls the particle toward the best place anyone found. "The group found something better over there." |

The random factors `r1` and `r2` prevent all particles from taking identical paths, maintaining diversity in the swarm.

---

## 2.3 Implementing Classic PSO from Scratch

Let's implement PSO to build intuition. We'll optimize the **Rastrigin function**, a classic test function with many local minima:

```
f(x) = 10n + Σ[x_i² - 10*cos(2π*x_i)]
```

where `n` is the dimensionality. The global minimum is at `x = (0, 0, ..., 0)` with `f(x) = 0`.

```python
import numpy as np
import matplotlib.pyplot as plt

def rastrigin(x):
    """Rastrigin function: many local minima, global min at origin."""
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))

class ParticleSwarmOptimizer:
    def __init__(self, func, dim, n_particles, bounds,
                 w=0.7, c1=1.5, c2=1.5, max_iter=100):
        """
        Classic PSO implementation.

        Args:
            func: objective function to minimize
            dim: dimensionality of the search space
            n_particles: number of particles in the swarm
            bounds: (min, max) tuple for each dimension
            w: inertia weight
            c1: cognitive coefficient
            c2: social coefficient
            max_iter: maximum iterations
        """
        self.func = func
        self.dim = dim
        self.n_particles = n_particles
        self.bounds = bounds
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.max_iter = max_iter

        # Initialize positions uniformly in the search space
        self.positions = np.random.uniform(
            bounds[0], bounds[1], (n_particles, dim)
        )

        # Initialize velocities to small random values
        velocity_range = (bounds[1] - bounds[0]) * 0.1
        self.velocities = np.random.uniform(
            -velocity_range, velocity_range, (n_particles, dim)
        )

        # Evaluate initial positions
        self.scores = np.array([func(p) for p in self.positions])

        # Personal bests
        self.personal_best_positions = self.positions.copy()
        self.personal_best_scores = self.scores.copy()

        # Global best
        best_idx = np.argmin(self.scores)
        self.global_best_position = self.positions[best_idx].copy()
        self.global_best_score = self.scores[best_idx]

        # History for visualization
        self.history = {
            'global_best_scores': [self.global_best_score],
            'positions': [self.positions.copy()],
            'particle_scores': [self.scores.copy()]
        }

    def step(self):
        """Execute one PSO iteration."""
        for i in range(self.n_particles):
            r1 = np.random.random(self.dim)
            r2 = np.random.random(self.dim)

            # Velocity update: the core PSO equation
            self.velocities[i] = (
                self.w * self.velocities[i]                          # inertia
                + self.c1 * r1 * (self.personal_best_positions[i]    # cognitive
                                   - self.positions[i])
                + self.c2 * r2 * (self.global_best_position          # social
                                   - self.positions[i])
            )

            # Position update
            self.positions[i] += self.velocities[i]

            # Clamp to bounds
            self.positions[i] = np.clip(
                self.positions[i], self.bounds[0], self.bounds[1]
            )

            # Evaluate
            score = self.func(self.positions[i])
            self.scores[i] = score

            # Update personal best
            if score < self.personal_best_scores[i]:
                self.personal_best_scores[i] = score
                self.personal_best_positions[i] = self.positions[i].copy()

                # Update global best
                if score < self.global_best_score:
                    self.global_best_score = score
                    self.global_best_position = self.positions[i].copy()

        self.history['global_best_scores'].append(self.global_best_score)
        self.history['positions'].append(self.positions.copy())
        self.history['particle_scores'].append(self.scores.copy())

    def optimize(self):
        """Run the full optimization."""
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
```

### Visualizing the Swarm

```python
def plot_pso_trajectory(pso, func):
    """Visualize particle trajectories on the function landscape."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Create function landscape
    x = np.linspace(-5.12, 5.12, 200)
    y = np.linspace(-5.12, 5.12, 200)
    X, Y = np.meshgrid(x, y)
    Z = np.array([[func(np.array([xi, yi])) for xi, yi in zip(xrow, yrow)]
                   for xrow, yrow in zip(X, Y)])

    # Plot at three time points
    for ax, t, title in zip(axes, [0, 10, 49],
                             ['Iteration 0', 'Iteration 10', 'Iteration 49']):
        ax.contourf(X, Y, Z, levels=30, cmap='viridis', alpha=0.6)
        positions = pso.history['positions'][t]
        ax.scatter(positions[:, 0], positions[:, 1],
                  c='red', s=30, zorder=5, edgecolors='white', linewidth=0.5)
        ax.scatter(0, 0, c='yellow', s=100, marker='*', zorder=6,
                  label='Global optimum')
        ax.set_title(title)
        ax.set_xlim(-5.12, 5.12)
        ax.set_ylim(-5.12, 5.12)

    plt.tight_layout()
    plt.savefig('pso_trajectory.png', dpi=150)
    plt.show()

# plot_pso_trajectory(pso, rastrigin)
```

---

## 2.4 Why PSO Works (and When It Doesn't)

### Strengths
- **No gradients required**: Only needs function evaluations. Works on black-box functions.
- **Handles multimodal landscapes**: The swarm maintains diversity, exploring multiple basins.
- **Simple to implement**: The core algorithm is ~30 lines of code.
- **Parallelizable**: Each particle evaluation is independent.

### Weaknesses
- **No convergence guarantee**: PSO is a heuristic. It may get stuck in local optima.
- **Hyperparameter sensitive**: Performance depends on `w`, `c1`, `c2` choices.
- **Dimensionality challenge**: Effectiveness decreases in very high-dimensional spaces.
- **Evaluation cost**: Each iteration requires N function evaluations.

### Why This Matters for Model Swarms

The weight space of a neural network is:
- **Extremely high-dimensional** (millions/billions of parameters)
- **Non-convex** with many local optima
- **Expensive to evaluate** (requires running inference on a validation set)
- **Not differentiable** with respect to task metrics (accuracy isn't smooth)

PSO's gradient-free nature is essential here — you can't backpropagate through "accuracy on 200 validation examples" the way you can through a loss function. But the dimensionality and evaluation cost are real challenges that the paper addresses through:
- **LoRA adapters** (reducing effective dimensionality from billions to millions)
- **Fast merging** (operating on safetensor files directly)
- **Dropout-K/N** (skipping evaluations stochastically)

---

## 2.5 Model Swarms' Modifications to Classic PSO

The paper doesn't use vanilla PSO. It introduces several modifications:

### 1. Repulsion from Global Worst

Classic PSO has no concept of "bad" positions — only attraction to good ones. Model Swarms adds a **repulsion term** that pushes particles away from the worst-performing configuration:

```
v_i ← (1/C)[w*r_v*v_i + c1*r_p*(p_i - x_i) + c2*r_s*(g - x_i) - c3*r_b*(g_w - x_i)]
```

The `- c3*r_b*(g_w - x_i)` term creates a "force field" around the worst solution. This is important because in weight space, bad regions can be catastrophic — a model that produces toxic output or gibberish is far worse than one that's merely mediocre.

### 2. Normalization

Instead of simply summing the weighted terms, Model Swarms normalizes them:

```
C = r_v*w + r_p*c1 + r_s*c2 + r_b*c3
```

This ensures the velocity direction is a weighted average of the four component directions, not a sum that could grow unboundedly.

### 3. Particle Restart

If a particle hasn't improved its personal best in `restart_patience * patience` iterations, it "restarts" — teleporting back to its personal best position with zero velocity. This prevents particles from drifting endlessly in unproductive directions.

### 4. Step Length Scheduling

The step length `λ` (how far a particle moves in the velocity direction) decays geometrically:

```
λ ← λ * φ_λ    (where φ_λ = 0.95 typically)
```

This creates an exploration-to-exploitation transition: early iterations take big steps to explore broadly, later iterations take small steps to refine solutions.

---

## 2.6 PSO Hyperparameter Sensitivity

Let's explore how PSO parameters affect optimization behavior:

```python
def run_pso_experiment(w, c1, c2, n_particles=20, dim=2,
                       max_iter=50, n_trials=5):
    """Run multiple PSO trials and return convergence curves."""
    all_curves = []
    for seed in range(n_trials):
        np.random.seed(seed)
        pso = ParticleSwarmOptimizer(
            func=rastrigin, dim=dim, n_particles=n_particles,
            bounds=(-5.12, 5.12), w=w, c1=c1, c2=c2, max_iter=max_iter
        )
        pso.optimize()
        all_curves.append(pso.history['global_best_scores'])
    return np.array(all_curves)

# Experiment 1: Effect of inertia weight
configs = [
    (0.1, 1.5, 1.5, 'Low inertia (w=0.1)'),
    (0.5, 1.5, 1.5, 'Medium inertia (w=0.5)'),
    (0.9, 1.5, 1.5, 'High inertia (w=0.9)'),
]

fig, ax = plt.subplots(figsize=(10, 6))
for w, c1, c2, label in configs:
    curves = run_pso_experiment(w, c1, c2)
    mean_curve = curves.mean(axis=0)
    std_curve = curves.std(axis=0)
    ax.plot(mean_curve, label=label)
    ax.fill_between(range(len(mean_curve)),
                    mean_curve - std_curve, mean_curve + std_curve, alpha=0.2)
ax.set_xlabel('Iteration')
ax.set_ylabel('Best Score (lower is better)')
ax.set_title('Effect of Inertia Weight on PSO Convergence')
ax.legend()
ax.set_yscale('log')
plt.tight_layout()
# plt.savefig('pso_inertia_experiment.png', dpi=150)
```

---

## 2.7 From Classic PSO to Model Swarms: The Conceptual Bridge

Here's the mapping between classic PSO and Model Swarms:

| Classic PSO Concept | Model Swarms Equivalent |
|--------------------|-----------------------|
| Particle position `x_i` | LoRA adapter weights of expert `i` |
| Search space | Space of all possible LoRA weight configurations |
| Objective function `f(x)` | Utility function (accuracy, harmonic mean, reward score, etc.) |
| Particle velocity `v_i` | Direction of weight change (also a set of LoRA weights) |
| Position update `x + λv` | Weighted combination of current weights and velocity weights |
| Personal best `p_i` | Best-performing weight configuration this expert has visited |
| Global best `g` | Best-performing weight configuration any expert has visited |
| Random coefficients `r1, r2` | Uniform random numbers maintaining exploration diversity |

The conceptual leap is treating **LoRA adapter weights** as positions in a continuous space where:
- Weighted combinations of positions (linear interpolation) produce valid models
- The utility function (task performance) defines the fitness landscape
- Particles can "move" by adding velocity vectors to their weight vectors

This works because neural network weight spaces have a useful property: **linear interpolation between good models often produces good models** (this is the insight behind model soups, SLERP, and related techniques). Model Swarms exploits this linearity while adding the collaborative search dynamics of PSO.

---

## [Exercise 2.1] Implement PSO with Repulsion

Extend the `ParticleSwarmOptimizer` class to include a repulsion term from the global worst, matching the Model Swarms formulation:

```python
class ModelSwarmsPSO(ParticleSwarmOptimizer):
    def __init__(self, *args, c3=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self.c3 = c3
        # Track global worst
        worst_idx = np.argmax(self.scores)
        self.global_worst_position = self.positions[worst_idx].copy()
        self.global_worst_score = self.scores[worst_idx]

    def step(self):
        # YOUR IMPLEMENTATION HERE
        # Modify the velocity update to include:
        # 1. Normalization (divide by sum of random-weighted coefficients)
        # 2. Repulsion from global worst: -c3 * r3 * (g_worst - x_i)
        # 3. Update global worst tracking
        pass
```

Test your implementation on the Rastrigin function and compare convergence with and without repulsion.

## [Exercise 2.2] Explore Dimensionality

Run the classic PSO optimizer on the Rastrigin function in 2, 5, 10, 20, and 50 dimensions. Plot:
1. Final best score vs. dimensionality
2. Number of iterations to reach "good enough" (score < 1.0) vs. dimensionality

What happens to PSO's effectiveness as dimensionality increases? How does this inform the design choice to use LoRA (low-rank) adapters in Model Swarms rather than full model weights?

## [Exercise 2.3] Particle Restart Mechanism

Implement the particle restart mechanism described in Section 2.5.3:
- Track how many iterations each particle has gone without improving its personal best
- If a particle exceeds `restart_patience * patience` iterations without improvement, reset its position to its personal best and zero its velocity

Run experiments comparing PSO with and without restart on a modified Rastrigin function that has one deep global minimum and several shallow local minima.

## [Exercise 2.4] Step Length Decay

Implement geometric step length decay (`λ ← λ * 0.95` each iteration) in your PSO implementation. Compare convergence behavior with:
- Fixed step length (λ = 1.0)
- Decaying step length (λ starts at 1.0, decays by 0.95 per iteration)
- Aggressive decay (λ decays by 0.8 per iteration)

Which regime finds the global optimum most reliably? Which converges fastest but to a worse solution?

---

**Next: [Module 3 — Background: LLM Experts, LoRA & Model Merging →](module_03_lora_and_merging.md)**
