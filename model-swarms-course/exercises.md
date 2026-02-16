# Exercises & Coding Challenges

This document collects standalone coding challenges that integrate concepts from multiple modules. Each challenge is designed to deepen your understanding through implementation.

---

## Challenge 1: Build a Complete Mini-Swarm from Scratch

**Difficulty: Medium | Time: 60-90 minutes**

Implement a complete, simplified Model Swarms system that works on 2D weight vectors (not real neural networks). This lets you study the algorithm's dynamics without needing GPUs or large models.

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable, Optional

class MiniModelSwarm:
    """
    A simplified Model Swarms implementation operating on 2D weight vectors.
    The 'utility function' is a synthetic function over 2D space,
    simulating how model performance varies with weight configurations.
    """

    def __init__(
        self,
        utility_func: Callable[[np.ndarray], float],
        initial_positions: List[np.ndarray],
        target_particles: int = 20,
        inertia: float = 0.2,
        cognitive_coeff: float = 0.3,
        social_coeff: float = 0.4,
        repel_coeff: float = 0.1,
        step_length: float = 1.0,
        step_decay: float = 0.95,
        min_step: float = 0.1,
        patience: int = 10,
        restart_patience_ratio: float = 0.67,
        use_randomness: bool = True,
    ):
        # YOUR IMPLEMENTATION:
        # 1. Store hyperparameters
        # 2. Expand initial_positions to target_particles via interpolation
        #    (match the paper's approach: t ~ Uniform(0,2), child = t*p1 + (1-t)*p2)
        # 3. Initialize random velocities (random mode)
        # 4. Evaluate all particles
        # 5. Set up tracking: personal_best, global_best, global_worst, histories
        pass

    def step(self) -> dict:
        """
        Execute one iteration of Model Swarms.

        Returns a dict with:
        - 'global_best_score': current global best
        - 'improved': whether global best improved this iteration
        - 'restarts': number of particles restarted
        """
        # YOUR IMPLEMENTATION:
        # For each particle:
        #   1. Check restart condition
        #   2. Sample random coefficients (if use_randomness)
        #   3. Normalize weights
        #   4. Compute velocity components (inertia, cognitive, social, repulsion)
        #   5. Update velocity
        #   6. Update position: x_i += step_length * v_i
        #   7. Evaluate
        #   8. Update personal_best, global_best, global_worst
        # Decay step_length
        # Return summary dict
        pass

    def search(self, max_iter: int = 50) -> Tuple[np.ndarray, float]:
        """
        Run the full search with patience-based stopping.

        Returns (best_position, best_score).
        """
        # YOUR IMPLEMENTATION
        pass

    def plot_trajectory(self, ax=None):
        """Visualize the search trajectory."""
        # YOUR IMPLEMENTATION:
        # Plot the utility function as a contour map
        # Overlay particle positions at each iteration
        # Highlight global best trajectory
        pass


# --- TEST YOUR IMPLEMENTATION ---

def multi_peak_utility(x: np.ndarray) -> float:
    """
    A synthetic utility function with multiple peaks.
    Simulates a weight-space landscape with several 'good' regions.
    Global maximum at approximately (2.0, 1.5).
    """
    return (
        0.8 * np.exp(-((x[0]-2)**2 + (x[1]-1.5)**2) / 0.5)    # global peak
        + 0.6 * np.exp(-((x[0]+1)**2 + (x[1]-0.5)**2) / 0.8)  # local peak 1
        + 0.5 * np.exp(-((x[0]-0.5)**2 + (x[1]+1)**2) / 0.6)  # local peak 2
        + 0.3 * np.exp(-((x[0]+1.5)**2 + (x[1]+1.5)**2) / 1.0) # local peak 3
        + 0.1 * np.random.randn() * 0.01  # slight noise
    )

# Create 5 'initial experts' at different locations
initial_experts = [
    np.array([-1.0, 0.5]),   # near local peak 1
    np.array([0.5, -1.0]),   # near local peak 2
    np.array([-1.5, -1.5]),  # near local peak 3
    np.array([1.0, 0.0]),    # between peaks
    np.array([0.0, 1.0]),    # between peaks
]

swarm = MiniModelSwarm(
    utility_func=multi_peak_utility,
    initial_positions=initial_experts,
    target_particles=15,
)

best_pos, best_score = swarm.search(max_iter=30)
print(f"Best position: {best_pos}")
print(f"Best score: {best_score:.4f}")
print(f"True optimum: [2.0, 1.5] with score ~0.8")

# Visualize
swarm.plot_trajectory()
```

### Acceptance Criteria
- The search finds the global peak (within 0.3 of [2.0, 1.5])
- The trajectory visualization shows particles converging
- Particle restart triggers at least once during the search
- The convergence curve shows monotonic improvement in global best

---

## Challenge 2: Implement the Merge Operation with Verification

**Difficulty: Easy-Medium | Time: 30 minutes**

Implement `lora_merge` and write comprehensive tests:

```python
import torch
from safetensors.torch import load_file, save_file
import os
import tempfile

def lora_merge(weights, adapter_paths, output_path):
    """
    Merge multiple LoRA adapters with given weights.

    Args:
        weights: list of scalar weights
        adapter_paths: list of paths to directories containing
                       adapter_model.safetensors
        output_path: directory to save merged adapter
    """
    # YOUR IMPLEMENTATION
    pass


# --- TESTS ---

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


# Run all tests
if __name__ == "__main__":
    test_identity_merge()
    test_zero_weight()
    test_subtraction()
    test_linearity()
    test_velocity_computation()
    print("\nAll tests passed!")
```

---

## Challenge 3: Hyperparameter Sensitivity Visualization

**Difficulty: Medium | Time: 45 minutes**

Using your MiniModelSwarm from Challenge 1, create a comprehensive hyperparameter sensitivity analysis:

```python
import itertools

def run_sensitivity_analysis():
    """
    Run the mini swarm with different hyperparameter settings
    and visualize how each parameter affects convergence.
    """

    # Parameters to vary
    param_grid = {
        'inertia': [0.05, 0.1, 0.2, 0.4, 0.6],
        'cognitive_coeff': [0.1, 0.2, 0.3, 0.5],
        'social_coeff': [0.1, 0.2, 0.4, 0.6],
        'repel_coeff': [0.0, 0.05, 0.1, 0.2],
    }

    # YOUR IMPLEMENTATION:
    # 1. For each parameter, vary it while holding others at defaults
    # 2. Run 5 trials per configuration (different random seeds)
    # 3. Record: final score, iterations to converge, diversity at convergence
    # 4. Create a 2×2 subplot figure showing the effect of each parameter
    # 5. Include error bars (std across trials)
    pass


def plot_exploration_exploitation(swarm_results):
    """
    Visualize the exploration-exploitation trade-off.

    Plot:
    - X-axis: average pairwise distance between particles (diversity metric)
    - Y-axis: global best score
    - Color: iteration number
    - One curve per hyperparameter configuration
    """
    # YOUR IMPLEMENTATION
    pass


def analyze_step_length_schedules():
    """
    Compare different step length scheduling strategies:
    1. Fixed (no decay)
    2. Linear decay
    3. Geometric decay (paper's approach)
    4. Cosine annealing
    5. Warm restart (reset step length periodically)
    """

    schedules = {
        'fixed': lambda t, T: 1.0,
        'linear': lambda t, T: 1.0 - t/T,
        'geometric': lambda t, T: 0.95**t,
        'cosine': lambda t, T: 0.5 * (1 + np.cos(np.pi * t / T)),
        'warm_restart': lambda t, T: 0.95**(t % (T//3)),
    }

    # YOUR IMPLEMENTATION:
    # Run the mini swarm with each schedule
    # Compare convergence speed and final quality
    pass
```

---

## Challenge 4: Correctness Emergence Detector

**Difficulty: Medium-Hard | Time: 45 minutes**

Build a tool that analyzes correctness emergence from search results:

```python
import json
import os
from collections import Counter

class CorrectnessEmergenceAnalyzer:
    """
    Analyzes correctness emergence in Model Swarms search results.

    Reads prediction files from the search directory and computes
    C-surge and C-emerge metrics.
    """

    def __init__(self, search_dir: str):
        """
        Args:
            search_dir: path to search/<experiment_name>/ directory
        """
        self.search_dir = search_dir
        # YOUR IMPLEMENTATION:
        # Load utility_scratchpad.json
        # Identify all particle directories
        # Load initial predictions (from "now" at start)
        # Load final predictions (from "personal_best" at end)
        pass

    def compute_c_surge(self) -> float:
        """
        C-surge: fraction of questions where the final best model is
        correct AND at least one initial model was incorrect.
        """
        # YOUR IMPLEMENTATION
        pass

    def compute_c_emerge(self) -> float:
        """
        C-emerge: fraction of questions where the final best model is
        correct AND ALL initial models were incorrect.
        """
        # YOUR IMPLEMENTATION
        pass

    def diamond_in_rough_analysis(self) -> dict:
        """
        Analyze the 'diamond in the rough' phenomenon.

        Returns:
        - best_particle_idx: which particle ended as global best
        - initial_rank: where that particle ranked initially (1 = best)
        - bottom_half: whether it started in the bottom 50%
        """
        # YOUR IMPLEMENTATION
        pass

    def per_question_analysis(self) -> list:
        """
        For each question, return:
        - How many initial models got it right
        - Whether the final model got it right
        - Whether this represents emergence (0 initial → 1 final)
        """
        # YOUR IMPLEMENTATION
        pass

    def plot_emergence_heatmap(self):
        """
        Create a heatmap:
        - Rows: questions (sorted by initial difficulty)
        - Columns: initial models + final best model
        - Color: correct (green) / incorrect (red)

        This visually shows which questions 'emerged' — going from
        all-red in initial models to green in the final model.
        """
        # YOUR IMPLEMENTATION
        pass
```

---

## Challenge 5: Build a Utility Function Benchmark

**Difficulty: Hard | Time: 60 minutes**

Create a synthetic benchmark for studying how different utility function properties affect Model Swarms performance:

```python
class UtilityFunctionBenchmark:
    """
    A framework for studying how utility function properties
    (smoothness, noise, multimodality, dimensionality)
    affect Model Swarms convergence.
    """

    @staticmethod
    def smooth_unimodal(x: np.ndarray) -> float:
        """Best case: smooth, single peak."""
        return -np.sum(x**2)  # simple quadratic

    @staticmethod
    def smooth_multimodal(x: np.ndarray) -> float:
        """Multiple peaks, smooth transitions."""
        return max(
            np.exp(-np.sum((x - 1)**2)),
            0.8 * np.exp(-np.sum((x + 1)**2)),
            0.6 * np.exp(-np.sum(x**2) / 2)
        )

    @staticmethod
    def noisy(x: np.ndarray, noise_level: float = 0.1) -> float:
        """Smooth function + random noise (simulates small validation sets)."""
        clean = -np.sum(x**2)
        return clean + np.random.randn() * noise_level

    @staticmethod
    def deceptive(x: np.ndarray) -> float:
        """Global optimum surrounded by bad local optima."""
        # Main peak at origin
        main = np.exp(-np.sum(x**2) / 0.3)
        # Ring of local peaks
        ring = 0.5 * np.exp(-((np.sqrt(np.sum(x**2)) - 2)**2) / 0.5)
        return main + ring

    @staticmethod
    def discontinuous(x: np.ndarray) -> float:
        """Step function (simulates accuracy on small datasets)."""
        score = np.sum(x)
        thresholds = [-2, -1, 0, 1, 2]
        for i, t in enumerate(thresholds):
            if score < t:
                return i / len(thresholds)
        return 1.0

    def run_benchmark(self, swarm_class, n_trials: int = 10) -> dict:
        """
        Run Model Swarms on each utility function and report:
        - Convergence speed (iterations to 90% of optimum)
        - Final quality (% of true optimum found)
        - Variance across trials

        YOUR IMPLEMENTATION
        """
        pass
```

---

## Challenge 6: Visualization Dashboard

**Difficulty: Medium | Time: 45 minutes**

Build a visualization that animates the swarm search process:

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def create_swarm_animation(swarm, utility_func, bounds=(-3, 3),
                           filename='swarm_animation.gif'):
    """
    Create an animated GIF showing:
    - Background: utility function contour plot
    - Particles: colored dots moving over time
    - Global best: highlighted star
    - Velocity vectors: arrows showing direction of movement
    - Score panel: convergence curve updating in real-time
    """
    # YOUR IMPLEMENTATION
    # Hint: Use FuncAnimation with the swarm's position history

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left panel: particle positions on utility landscape
    x = np.linspace(bounds[0], bounds[1], 100)
    y = np.linspace(bounds[0], bounds[1], 100)
    X, Y = np.meshgrid(x, y)
    Z = np.array([[utility_func(np.array([xi, yi]))
                   for xi, yi in zip(xrow, yrow)]
                  for xrow, yrow in zip(X, Y)])

    def animate(frame):
        ax1.clear()
        ax2.clear()

        # Draw contour
        ax1.contourf(X, Y, Z, levels=30, cmap='viridis', alpha=0.6)

        # Draw particles at this frame
        # YOUR CODE: plot positions, velocities, personal bests, global best

        # Draw convergence curve up to this frame
        # YOUR CODE: plot global_best_history[:frame+1]

        ax1.set_title(f'Iteration {frame}')
        ax2.set_title('Convergence')

    anim = FuncAnimation(fig, animate,
                         frames=len(swarm.history['positions']),
                         interval=200)
    anim.save(filename, writer='pillow')
    plt.close()
    print(f"Animation saved to {filename}")
```

---

## Grading Rubric (Self-Assessment)

For each challenge, evaluate yourself on:

| Criterion | Points |
|-----------|--------|
| **Correctness**: Does the code run and produce correct results? | 40% |
| **Completeness**: Are all specified features implemented? | 20% |
| **Understanding**: Do your comments/analysis show you understand WHY, not just HOW? | 25% |
| **Code quality**: Is the code clean, well-structured, and Pythonic? | 15% |

### Minimum Passing (70%):
- Challenges 1-2 fully working
- Challenge 3 at least partially working
- Written analysis for Exercise 7.5 (critical review)

### Distinction (90%+):
- All 6 challenges working
- Visualization challenge produces animated output
- Research proposal (Exercise 8.5) demonstrates genuine novelty
- Hyperparameter analysis reveals a non-obvious insight
