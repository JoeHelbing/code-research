# Module 4: The Model Swarms Algorithm — Deep Dive

**Estimated time: 60 minutes**

This is the core module of the course. We'll walk through the complete Model Swarms algorithm, step by step, connecting each piece to the paper's formulation and the actual code.

---

## 4.1 Algorithm Overview

Open the paper to **Algorithm 1** (page 4) and **Figure 1**. The algorithm has four phases:

```
INITIALIZATION → [VELOCITY UPDATE → WEIGHT UPDATE → CONVERGENCE CHECK] × K
```

The bracketed portion repeats for up to K iterations (default: 200, but patience-based early stopping usually triggers much sooner).

---

## 4.2 Step 0: Initialization

### Input Requirements

The algorithm takes as input:
- **n initial experts**: LoRA adapters fine-tuned on different domains (default: 10)
- **Utility function f**: A function that takes a model and returns a scalar score
- **Hyperparameters**: inertia, cognitive/social/repel coefficients, step length, patience

### Population Expansion

The n initial experts are expanded to N particles (default: N=20) through pairwise interpolation:

```python
# For each new particle to create:
parent_1, parent_2 = random_choice(existing_experts)  # two different parents
t = random.random() * 2  # t ∈ [0, 2]
child = t * parent_1 + (1 - t) * parent_2
```

**Why expand?** More particles = better coverage of the search space. The paper found that N=20 provides a good balance between diversity and computational cost.

**Why allow t > 1?** This creates **extrapolated** children that lie outside the line segment between the parents. In weight space, this can discover interesting regions that aren't simple averages of existing experts.

### Velocity Initialization

Each particle receives an initial velocity. Three modes are supported:

| Mode | How | Intuition |
|------|-----|-----------|
| `zero` | `v_i = 0` | Particles start stationary, only move after first evaluation |
| `random` | `v_i = x_j - x_i` (random j) | Each particle points toward a random other particle |
| `best` | `v_i = g - x_i` | All particles point toward the global best (after initial evaluation) |

The default is `random`, which provides the most diverse initial exploration.

### Initial Evaluation

Every particle is evaluated on the utility function:

```python
# Pseudocode
for each particle i:
    score_i = f(particle_i)  # Run inference on validation set

# Track bests
personal_best[i] = score_i for all i
global_best = max(all scores)
global_worst = min(all scores)
```

This step is the most expensive part of initialization — it requires N forward passes through the validation set.

---

## 4.3 Step 1: Velocity Update (The Core Equation)

This is the heart of Model Swarms. The velocity update determines how each particle will move:

### The Formula

```
v_i ← (1/C) * [r_v * φ_v * v_i        +     # inertia
                r_p * φ_p * (p_i - x_i)  +     # cognitive
                r_g * φ_g * (g - x_i)    -     # social
                r_w * φ_w * (g_w - x_i)]       # repulsion
```

where:
```
C = r_v * φ_v + r_p * φ_p + r_g * φ_g + r_w * φ_w    (normalization)
```

### Each Component in Detail

**Inertia: `r_v * φ_v * v_i`**
- `φ_v` (phi_v) = inertia coefficient (default: 0.2)
- `r_v` = uniform random in [0, 1]
- Effect: the particle keeps moving in its current direction
- High inertia → more exploration, slower convergence
- Low inertia → more responsive to cognitive/social signals

**Cognitive: `r_p * φ_p * (p_i - x_i)`**
- `φ_p` = cognitive coefficient (default: 0.3)
- `r_p` = uniform random in [0, 1]
- `p_i - x_i` = direction from current position to personal best
- Effect: the particle is pulled back toward the best configuration it has ever found
- This represents "individual memory" — what has worked for this particle in the past

**Social: `r_g * φ_g * (g - x_i)`**
- `φ_g` = social coefficient (default: 0.4)
- `r_g` = uniform random in [0, 1]
- `g - x_i` = direction from current position to global best
- Effect: the particle is attracted to the best configuration found by any particle
- This represents "social learning" — copying what has worked for the group

**Repulsion: `-r_w * φ_w * (g_w - x_i)`**
- `φ_w` = repel coefficient (default: 0.1)
- `r_w` = uniform random in [0, 1]
- `g_w - x_i` = direction from current position to global worst
- The minus sign means: direction AWAY from the global worst
- Equivalently: `+r_w * φ_w * (x_i - g_w)` — move in the direction you already differ from the worst
- Effect: the particle avoids regions of weight space associated with poor performance

### Normalization

The factor `C` normalizes the velocity so it represents a **weighted average direction** rather than a sum:

```python
self_weight = r_w_rand * inertia
cognitive_weight = r_p_rand * cognitive_coeff
social_weight = r_s_rand * social_coeff
repel_weight = r_b_rand * repel_coeff

weight_sum = self_weight + cognitive_weight + social_weight + repel_weight

# Normalize
self_weight /= weight_sum
cognitive_weight /= weight_sum
social_weight /= weight_sum
repel_weight /= weight_sum
```

This is critical because without normalization, the velocity magnitude would be unpredictable — dependent on the sum of random numbers. With normalization, the velocity always represents a unit-weighted combination of the four directions.

### Random Coefficients: Why?

The random multipliers `r_v, r_p, r_g, r_w ∈ [0, 1]` serve a crucial purpose: **they prevent all particles from moving in identical directions**.

Without randomness, if all particles have the same global best and similar positions, they would all compute nearly identical velocities and collapse to the same point. The random coefficients ensure that each particle weighs the four components differently at each step, maintaining swarm diversity.

The paper includes an ablation study (Table 5) showing that removing randomness (`weight_randomness=0`) reduces performance by 5-15% across tasks.

---

## 4.4 Step 2: Weight Update

After computing the velocity, the particle moves:

```
x_i ← x_i + λ * v_i
```

where `λ` is the step length (default: starts at 0.7-1.0, varies by task).

In code:
```python
lora_merge(
    weights=[1, step_length],
    lora_name_list=[current_position_path, velocity_path],
    output_name=current_position_path
)
```

The particle then gets evaluated:

```python
score = evaluate(new_position, eval_type, dataset, gpu_id, base_model)
```

### Updating Tracking Variables

After evaluation, the algorithm updates:

```python
# Update personal best
if score > personal_best_score[i]:
    personal_best_score[i] = score
    personal_best_position[i] = current_position[i].copy()

# Update global best
if score > global_best_score:
    global_best_score = score
    global_best_position = current_position[i].copy()

# Update global worst
if score < global_worst_score:
    global_worst_score = score
    global_worst_position = current_position[i].copy()
```

---

## 4.5 Step 3: Convergence and Scheduling

### Early Stopping (Patience)

The search terminates when the global best hasn't improved in `patience` iterations:

```python
g_history = utility_scratchpad["g_history"]
if len(g_history) > patience:
    recent = g_history[-patience:]
    if max(recent) == min(recent):  # no improvement in last `patience` steps
        break
```

Default patience: 10 iterations.

### Step Length Decay

Each iteration, the step length shrinks:

```python
step_length = max(step_length * step_length_factor, minimum_step_length)
# Default: step_length_factor = 0.95, minimum_step_length = 0.1
```

After 10 iterations: `λ = 1.0 * 0.95^10 ≈ 0.60`
After 20 iterations: `λ = 1.0 * 0.95^20 ≈ 0.36`
After 30 iterations: `λ = 1.0 * 0.95^30 ≈ 0.21`

This gradual decay transitions the search from exploration (large steps, broad coverage) to exploitation (small steps, local refinement).

### Particle Restart

If a particle's personal best hasn't improved in `restart_patience * patience` iterations:

```python
particle_history = utility_scratchpad[f"particle_{i}_history"]
particle_best = utility_scratchpad[f"particle_{i}_best"]
first_time_best_idx = particle_history.index(particle_best)

if len(particle_history) - first_time_best_idx >= restart_patience * patience:
    # Reset to personal best position with zero velocity
    copy(personal_best → current_position)
    velocity = zero_vector
```

Default: `restart_patience = 0.67`, meaning a particle restarts after `0.67 * 10 ≈ 7` iterations of stagnation.

This mechanism prevents "zombie particles" — particles that have drifted far from any good region and are consuming evaluation budget without contributing to the search.

---

## 4.6 The Complete Algorithm as Pseudocode

Putting it all together:

```
Algorithm: Model Swarms

Input:
  - n initial expert LoRA adapters
  - Utility function f (validation performance)
  - Hyperparameters: φ_v, φ_p, φ_g, φ_w, λ, φ_λ, patience, K

Step 0: Initialize
  Expand n experts to N particles via pairwise interpolation
  Initialize velocities (random mode: v_i = x_random - x_i)
  Evaluate all particles: score_i = f(x_i)
  Set p_i = x_i, g = argmax(scores), g_w = argmin(scores)

For iteration = 1 to K:

  Step 1: For each particle i:
    Sample r_v, r_p, r_g, r_w ~ Uniform(0, 1)
    C = r_v*φ_v + r_p*φ_p + r_g*φ_g + r_w*φ_w

    v_i = (1/C) * [r_v*φ_v*v_i
                    + r_p*φ_p*(p_i - x_i)
                    + r_g*φ_g*(g - x_i)
                    - r_w*φ_w*(g_w - x_i)]

  Step 2: For each particle i:
    x_i = x_i + λ * v_i
    score_i = f(x_i)
    If score_i > best_score(p_i): update p_i
    If score_i > best_score(g): update g
    If score_i < best_score(g_w): update g_w

    If particle i stagnated for restart_patience * patience:
      x_i = p_i; v_i = 0  (restart)

  Step 3: Check convergence
    If g unchanged for `patience` iterations: STOP
    λ = max(λ * φ_λ, λ_min)

Output: global best particle g
```

---

## 4.7 Computational Cost Analysis

Each iteration requires:
- **N merge operations** for velocity components: 4 merges per particle × N particles = 4N merges
- **N merge operations** for velocity combination: 1 merge per particle × N particles = N merges
- **N merge operations** for position update: 1 merge per particle × N particles = N merges
- **N evaluations**: forward passes on the validation set (the expensive part)

Total per iteration: **6N merges + N evaluations**

With N=20 and 200 validation examples:
- 120 merge operations (fast — just tensor arithmetic on ~18M parameters)
- 20 model evaluations (requires loading model + running inference on 200 examples)

The paper reports that a typical search completes in 15-30 iterations, so total evaluations: 300-600 model evaluations, plus the N initial evaluations.

### Dropout-K/N Acceleration

The paper introduces a simple acceleration: skip evaluations stochastically.

- **Dropout-K**: With probability `dropK`, skip the entire iteration's evaluation (reuse previous scores)
- **Dropout-N**: For each particle, with probability `dropN`, skip its evaluation (reuse previous score)

```python
if random.random() < dropK:
    global_skip_flag = True  # skip all evaluations this iteration

for each particle i:
    if random.random() < dropN:
        local_skip_flag = True  # skip this particle's evaluation
```

With `dropK=0.5` and `dropN=0.5`, the expected number of evaluations per iteration drops from 20 to ~5, a 4x speedup with modest performance degradation.

---

## 4.8 Utility Functions: Defining "Good"

The utility function is the objective that PSO optimizes. The paper uses four different utility functions for four adaptation objectives:

### Single Task: Validation Accuracy

```python
def utility_single_task(model, validation_data):
    predictions = model.predict(validation_data)
    return accuracy_score(validation_data.labels, predictions)
```

### Multi-Task: Harmonic Mean

```python
def utility_multitask(model, validation_data_1, validation_data_2):
    score_1 = accuracy(model, validation_data_1)
    score_2 = accuracy(model, validation_data_2)
    return 2 * score_1 * score_2 / (score_1 + score_2)  # harmonic mean
```

Why harmonic mean instead of arithmetic mean? The harmonic mean penalizes imbalanced performance. A model that scores 90% on task 1 and 10% on task 2 gets a harmonic mean of 18%, not 50%. This encourages the search to find Pareto-optimal solutions that are good at both tasks.

### Reward Model: Average RM Score

```python
def utility_reward_model(model, prompts, rm_type):
    responses = model.generate(prompts)
    scores = reward_model.score(prompts, responses, rm_type)
    return mean(scores)
```

### Human Interest: LLM-as-Judge

```python
def utility_human_interest(model, prompts):
    responses = model.generate(prompts)
    scores = [gemini_eval(prompt, response) for prompt, response in zip(prompts, responses)]
    return mean(scores)  # average 1-10 rating
```

The beauty of Model Swarms is that **changing the utility function is all you need to do** to adapt the algorithm to completely different objectives. The search mechanics remain identical.

---

## 4.9 Worked Example: One Iteration

Let's trace through one complete iteration with concrete (simplified) numbers.

**Setup**: 3 particles (for simplicity), 2D weight space, maximizing a function.

```
Iteration 5:
  Particle 0: position=[0.3, 0.7], velocity=[0.1, -0.05], personal_best=[0.4, 0.6], score=0.72
  Particle 1: position=[0.5, 0.2], velocity=[-0.1, 0.1], personal_best=[0.5, 0.3], score=0.68
  Particle 2: position=[0.8, 0.9], velocity=[0.05, 0.02], personal_best=[0.7, 0.8], score=0.81

  Global best: [0.7, 0.8] (score=0.81, from Particle 2)
  Global worst: [0.5, 0.2] (score=0.55, from iteration 3)

Hyperparameters: φ_v=0.2, φ_p=0.3, φ_g=0.4, φ_w=0.1, λ=0.85
```

**Velocity update for Particle 0:**

```
r_v=0.73, r_p=0.41, r_g=0.89, r_w=0.55

Weighted components:
  inertia_w  = 0.73 * 0.2 = 0.146
  cognitive_w = 0.41 * 0.3 = 0.123
  social_w   = 0.89 * 0.4 = 0.356
  repel_w    = 0.55 * 0.1 = 0.055
  C = 0.146 + 0.123 + 0.356 + 0.055 = 0.680

Normalized weights: [0.215, 0.181, 0.524, 0.081]

Direction components:
  inertia   = [0.1, -0.05]                           (current velocity)
  cognitive = [0.4-0.3, 0.6-0.7] = [0.1, -0.1]      (toward personal best)
  social    = [0.7-0.3, 0.8-0.7] = [0.4, 0.1]       (toward global best)
  repulsion = -([0.5-0.3, 0.2-0.7]) = [0.2, 0.5]    (away from global worst)

New velocity = 0.215*[0.1,-0.05] + 0.181*[0.1,-0.1] + 0.524*[0.4,0.1] + 0.081*[0.2,0.5]
             = [0.0215,-0.0107] + [0.0181,-0.0181] + [0.2096,0.0524] + [0.0162,0.0405]
             ≈ [0.265, 0.064]
```

**Position update for Particle 0:**

```
new_position = [0.3, 0.7] + 0.85 * [0.265, 0.064]
             = [0.3 + 0.225, 0.7 + 0.054]
             ≈ [0.525, 0.754]
```

**Evaluate**: `score = f([0.525, 0.754]) = 0.78`

Since 0.78 > 0.72 (previous personal best), update personal best to [0.525, 0.754].
Since 0.78 < 0.81 (global best), global best unchanged.

---

## [Exercise 4.1] Trace the Algorithm

Using the same setup from Section 4.9, complete the velocity and position updates for Particles 1 and 2. Use these random numbers:

- Particle 1: r_v=0.22, r_p=0.67, r_g=0.35, r_w=0.91
- Particle 2: r_v=0.58, r_p=0.14, r_g=0.82, r_w=0.44

Questions:
1. Which particle moves the most (largest position change)?
2. Which particle is most influenced by the social term?
3. After this iteration, has the global best changed? Has the global worst changed?

## [Exercise 4.2] Implement the Velocity Update

Write a function that performs the Model Swarms velocity update:

```python
import numpy as np

def model_swarms_velocity_update(
    current_velocity,     # v_i
    current_position,     # x_i
    personal_best,        # p_i
    global_best,          # g
    global_worst,         # g_w
    inertia,              # φ_v
    cognitive_coeff,      # φ_p
    social_coeff,         # φ_g
    repel_coeff,          # φ_w
    use_randomness=True
):
    """
    Compute the updated velocity for one particle.

    Returns: new_velocity (same shape as current_velocity)
    """
    # YOUR IMPLEMENTATION HERE
    pass


# Test with the worked example values
v = model_swarms_velocity_update(
    current_velocity=np.array([0.1, -0.05]),
    current_position=np.array([0.3, 0.7]),
    personal_best=np.array([0.4, 0.6]),
    global_best=np.array([0.7, 0.8]),
    global_worst=np.array([0.5, 0.2]),
    inertia=0.2, cognitive_coeff=0.3,
    social_coeff=0.4, repel_coeff=0.1
)
print(f"New velocity: {v}")
# Should be approximately [0.265, 0.064] (varies with random seed)
```

## [Exercise 4.3] Utility Function Design

Design utility functions for the following scenarios:

1. **Code quality**: You have 10 code-specialized LLMs and want to find one that generates correct, clean code. You have 200 programming problems with test cases. What metric(s) would you use?

2. **Multilingual translation**: You want a model that translates well between English, Spanish, and French. You have 100 translation pairs for each direction. How would you combine per-direction BLEU scores into a single utility?

3. **Conflicting objectives**: You want a model that is both creative (novel, surprising responses) and factual (accurate, verifiable claims). These objectives often conflict. How would you structure the utility function?

## [Exercise 4.4] Sensitivity Analysis

Without running any code, predict the effect of:

1. Setting `inertia=0.0` (no momentum). What happens to exploration?
2. Setting `social_coeff=0.0` (no social term). What happens to collaboration?
3. Setting `repel_coeff=0.0` (no repulsion). What might the swarm converge to?
4. Setting `patience=1` (stop after one iteration without improvement). What's the risk?
5. Setting `step_length_factor=1.0` (no decay). What's the effect on late-stage behavior?

## [Exercise 4.5] Harmonic Mean vs. Arithmetic Mean

The multi-task utility uses the harmonic mean. Explore why:

```python
import numpy as np

# Compare harmonic and arithmetic means for different score distributions
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
    print()

# Question: In which scenario is the difference between harmonic and
# arithmetic mean the largest? Why does this property matter for
# multi-task optimization?
```

---

**Next: [Module 5 — Code Architecture & Implementation Walkthrough →](module_05_code_walkthrough.md)**
