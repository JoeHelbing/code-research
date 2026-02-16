# Module 3: Background — LLM Experts, LoRA & Model Merging

**Estimated time: 45 minutes**

---

## 3.1 The Foundation: What Are LLM Experts?

An "LLM expert" in the context of this paper is a pre-trained language model that has been **fine-tuned** on a specific domain or task. The paper uses 10 initial experts, all based on **Gemma-7B** (Google's 7-billion parameter model), each fine-tuned on a different subset of the Tulu-v2 dataset:

| Expert | Training Domain | What It's Good At |
|--------|----------------|-------------------|
| FLAN | Instruction following | General instruction completion |
| CoT | Chain-of-thought | Step-by-step reasoning |
| LIMA | Curated responses | High-quality, thoughtful answers |
| Open Assistant | Dialogue | Conversational interactions |
| Science | Scientific text | Technical/scientific questions |
| ShareGPT | ChatGPT-like responses | Broad conversational ability |
| Code | Programming | Code generation and explanation |
| Wizardlm | Complex instructions | Multi-step instruction following |
| Ultrachat | Long dialogues | Extended conversational contexts |
| MetaMath | Mathematics | Mathematical problem solving |

Each expert is stored as a **LoRA adapter** — a small set of weight modifications layered on top of the frozen base Gemma-7B model. This is the key design choice that makes Model Swarms computationally feasible.

---

## 3.2 LoRA: Low-Rank Adaptation

LoRA (Low-Rank Adaptation, Hu et al. 2021) is a parameter-efficient fine-tuning method. Instead of updating all model weights during fine-tuning, LoRA:

1. **Freezes** the pre-trained model weights `W`
2. **Adds** a low-rank decomposition `ΔW = BA` where:
   - `B` is a matrix of shape `(d, r)` — the "up projection"
   - `A` is a matrix of shape `(r, k)` — the "down projection"
   - `r << min(d, k)` is the rank (typically 8, 16, or 32)

3. The effective weight becomes `W + ΔW = W + BA`

### Why LoRA Matters for Model Swarms

For a 7B parameter model, the full weight matrices contain ~7 billion parameters. A LoRA adapter with rank 16 applied to attention layers contains only **~18 million parameters** — a 400x reduction.

This matters because:
- **Storage**: Each "particle" in the swarm is ~70MB instead of ~28GB
- **Merging**: Combining two LoRA adapters is a simple weighted sum of small tensors
- **Speed**: Loading, saving, and arithmetic on 18M parameters is fast
- **Linear interpolation works**: The low-rank structure preserves the property that interpolated weights produce coherent models

### LoRA Arithmetic

If you have two LoRA adapters `ΔW₁` and `ΔW₂`, their weighted combination is:

```
ΔW_combined = α₁ * ΔW₁ + α₂ * ΔW₂
```

The resulting model uses `W + ΔW_combined`. This is exactly the operation that Model Swarms performs when updating particle positions — it combines multiple LoRA adapters with different weights to produce new model configurations.

---

## 3.3 Understanding the Merge Operation

The `merge.py` file in the Model Swarms codebase implements the core weight combination operation. Let's study it:

```python
# From merge.py - the "fast merge" path
def lora_merge(weights, lora_name_list, output_name, gpu_id,
               directly_load_safetensors=1):
    """
    Combine multiple LoRA adapters with given weights.

    Args:
        weights: list of scalar weights [w1, w2, ...]
        lora_name_list: list of paths to LoRA adapters
        output_name: where to save the merged result
        gpu_id: which GPU to use
        directly_load_safetensors: use fast path (recommended)
    """
    if directly_load_safetensors:
        # Load only the LoRA weight tensors (not the full model)
        lora_state_dict_list = []
        for lora_name in lora_name_list:
            state_dict = load_file(
                os.path.join(lora_name, "adapter_model.safetensors"),
                device="cpu"
            )
            lora_state_dict_list.append(state_dict)

        # Weighted sum across all adapters
        final_state_dict = {}
        for i, state_dict in enumerate(lora_state_dict_list):
            if i == 0:
                for key in state_dict:
                    final_state_dict[key] = weights[i] * state_dict[key]
            else:
                for key in state_dict:
                    final_state_dict[key] += weights[i] * state_dict[key]

        # Save the merged adapter
        save_file(final_state_dict,
                  os.path.join(output_name, "adapter_model.safetensors"))
        return final_state_dict
```

This is remarkably simple. The entire merge operation is:

```
for each tensor key in the adapter:
    merged[key] = w1 * adapter1[key] + w2 * adapter2[key] + ...
```

No special handling, no gradient computation, no activation analysis. Just weighted sums of tensors.

---

## 3.4 How Model Swarms Uses Merging

Every PSO operation in Model Swarms is expressed as a merge:

### Computing Velocity Components

```python
# personal_best - current_position  (cognitive direction)
lora_merge(
    weights=[1, -1],
    lora_name_list=[personal_best_path, current_path],
    output_name=p_minus_x_path
)

# global_best - current_position  (social direction)
lora_merge(
    weights=[1, -1],
    lora_name_list=[global_best_path, current_path],
    output_name=g_minus_x_path
)

# current_position - global_worst  (repulsion direction)
lora_merge(
    weights=[-1, 1],
    lora_name_list=[global_worst_path, current_path],
    output_name=x_minus_gw_path
)
```

### Combining Velocity Components

```python
# v_new = w_inertia * v_old + w_cognitive * (p-x) + w_social * (g-x)
#         + w_repel * (x-gw)
lora_merge(
    weights=[self_weight, cognitive_weight, social_weight, repel_weight],
    lora_name_list=[velocity_path, p_minus_x_path, g_minus_x_path,
                     x_minus_gw_path],
    output_name=velocity_path  # overwrites old velocity
)
```

### Position Update

```python
# x_new = x_current + step_length * v_new
lora_merge(
    weights=[1, step_length],
    lora_name_list=[current_path, velocity_path],
    output_name=current_path  # overwrites current position
)
```

Every single operation — subtraction, addition, scaling — is implemented as a call to `lora_merge` with appropriate weights. Subtraction is `merge([1, -1], [A, B])`. Addition is `merge([1, 1], [A, B])`. Scaling is `merge([alpha], [A])`.

---

## 3.5 The Model Merging Landscape

Model Swarms exists within a broader ecosystem of model merging techniques. Understanding these baselines is important because the paper compares against all of them.

### Static Methods (Task-Independent)

These methods merge models without looking at any task data:

**Uniform Soup** — Average all model weights equally:
```
merged = (1/N) * Σ model_i
```

**SLERP** (Spherical Linear Interpolation) — Interpolate between two models along the surface of a hypersphere:
```
slerp(t, A, B) = sin((1-t)θ)/sin(θ) * A + sin(tθ)/sin(θ) * B
```
where `θ = arccos(A·B / (|A||B|))`. This preserves the magnitude of weight vectors, unlike linear interpolation which can shrink them.

**DARE-TIES** — Prune weights (set small changes to zero), resolve sign conflicts (when experts disagree on the sign of a weight change), then merge:
```
1. For each expert, randomly drop δ% of weight changes
2. For remaining changes, use majority vote to resolve sign conflicts
3. Average the surviving, sign-aligned changes
```

**Model Stocks** — Treat pre-trained and fine-tuned weights as points, use geometric analysis to find a better merge point:
```
merged = pretrained + Σ α_i * (expert_i - pretrained)
```
with coefficients derived from a geometric center-of-mass calculation.

### Dynamic Methods (Task-Dependent)

These methods use task data to determine how to merge:

**Greedy Soup** — Start with the best expert. Iteratively try adding each remaining expert (with equal weight). Keep additions that improve validation performance. Stop when no addition helps.

**LoraHub** — Learn a coefficient vector `[α₁, α₂, ..., αₙ]` by minimizing loss on task data:
```
merged_adapter = Σ α_i * adapter_i
minimize L(merged_adapter, task_data)  via gradient descent on α
```

**EvolMerge** — Use evolutionary algorithms (crossover, mutation) to search over merge recipes. Each "genome" specifies per-layer merge ratios.

**Pack of LLMs / cBTM** — Use routing mechanisms to select which expert to use for each input, based on input features.

### Where Model Swarms Differs

Model Swarms is **dynamic** (it uses task data via the utility function) but **gradient-free** (unlike LoraHub). It searches **collaboratively** (unlike Greedy Soup's sequential addition). And it explores the space **continuously** (unlike EvolMerge's discrete mutations).

The paper's key empirical finding is that this combination — collaborative, gradient-free, continuous search — outperforms all other approaches by significant margins.

---

## 3.6 Population Expansion via Interpolation

One subtle but important step: the paper starts with 10 initial experts but expands to 20 particles. The expansion uses **pairwise linear interpolation**:

```python
# From search.py - population expansion
for i in range(initial_experts_num - particles_now):
    parent_1 = random.choice(particle_paths)
    parent_2 = random.choice(particle_paths)
    while parent_1 == parent_2:
        parent_2 = random.choice(particle_paths)

    w_1 = random.random() * 2  # weight in [0, 2]
    w_2 = 1 - w_1              # w_1 + w_2 = 1 (but w_1 can be > 1!)

    lora_merge([w_1, w_2], [parent_1, parent_2], child_path)
```

Note the weight range: `w_1` is in `[0, 2]`, meaning `w_2` is in `[-1, 1]`. This means the interpolation can **extrapolate** beyond the convex hull of the two parents, not just interpolate between them. This creates initial particles that are more diverse than simple midpoints.

---

## 3.7 Practical Code: LoRA Merging by Hand

Let's implement a minimal version of LoRA merging to build intuition:

```python
import torch
from safetensors.torch import load_file, save_file

def simple_lora_merge(adapter_paths, weights, output_path):
    """
    Merge multiple LoRA adapters with given weights.

    Args:
        adapter_paths: list of paths to adapter_model.safetensors files
        weights: list of scalar weights (same length as adapter_paths)
        output_path: where to save the merged safetensors file
    """
    assert len(adapter_paths) == len(weights)

    # Load all adapters
    adapters = [load_file(path, device="cpu") for path in adapter_paths]

    # Verify they have the same keys (same architecture)
    keys = list(adapters[0].keys())
    for adapter in adapters[1:]:
        assert list(adapter.keys()) == keys, "Adapter architectures don't match"

    # Weighted sum
    merged = {}
    for key in keys:
        merged[key] = sum(w * adapter[key] for w, adapter in zip(weights, adapters))

    # Save
    save_file(merged, output_path)
    return merged


def inspect_adapter(adapter_path):
    """Print information about a LoRA adapter."""
    state_dict = load_file(adapter_path, device="cpu")

    total_params = 0
    print(f"Adapter: {adapter_path}")
    print(f"Number of tensors: {len(state_dict)}")
    print(f"\nTensor shapes:")
    for key in sorted(state_dict.keys())[:10]:  # first 10
        shape = state_dict[key].shape
        n_params = state_dict[key].numel()
        total_params += n_params
        print(f"  {key}: {list(shape)} ({n_params:,} params)")
    print(f"  ... ({len(state_dict) - 10} more tensors)")

    # Count remaining
    for key in sorted(state_dict.keys())[10:]:
        total_params += state_dict[key].numel()

    print(f"\nTotal parameters: {total_params:,}")
    print(f"Size on disk: ~{total_params * 2 / 1024 / 1024:.1f} MB (float16)")
```

---

## 3.8 Why Linear Weight Interpolation Works

A natural question: why does averaging/interpolating model weights produce good models at all? Shouldn't combining millions of individually-tuned parameters create nonsense?

There are several reasons this works:

### 1. Shared Pre-training Basin
All experts share the same pre-trained base model. Fine-tuning with LoRA makes small perturbations to this base. The experts all live in a relatively small region of weight space — the "fine-tuning basin" around the pre-trained model.

### 2. Linear Mode Connectivity
Research (Frankle et al., 2020; Neyshabur et al., 2020) has shown that neural networks fine-tuned from the same pre-trained checkpoint exhibit **linear mode connectivity** — you can linearly interpolate between their weights without encountering a loss barrier. The loss landscape between them is roughly convex.

### 3. Low-Rank Structure
LoRA adapters have additional structure: they're low-rank matrices. Interpolating between low-rank matrices produces another low-rank matrix. The expressiveness of the combined adapter is bounded by the sum of individual ranks.

### 4. Empirical Support from Model Soups
Wortsman et al. (2022) demonstrated that simply averaging multiple fine-tuned checkpoints of the same model often improves performance over any individual checkpoint. This "model soup" finding provides direct empirical evidence that weight-space interpolation is productive for neural networks.

---

## [Exercise 3.1] Adapter Inspection

If you have access to the Model Swarms codebase with downloaded initial experts:

```python
# Inspect one of the initial LoRA adapters
inspect_adapter("initial_experts/flan/adapter_model.safetensors")

# Questions:
# 1. How many parameters does each adapter have?
# 2. Which layers have LoRA adapters? (attention? feedforward? both?)
# 3. What is the LoRA rank based on the tensor shapes?
# 4. What is the compression ratio vs. the full 7B model?
```

## [Exercise 3.2] Manual Merge

Create a weighted merge of two adapters and analyze the result:

```python
# Merge two adapters with different weights
adapter_a = load_file("initial_experts/code/adapter_model.safetensors")
adapter_b = load_file("initial_experts/metamath/adapter_model.safetensors")

# Try different interpolation ratios
for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]:
    merged = {}
    for key in adapter_a:
        merged[key] = alpha * adapter_a[key] + (1 - alpha) * adapter_b[key]

    # Compute some statistics about the merged adapter
    total_norm = sum(torch.norm(v).item() for v in merged.values())
    print(f"alpha={alpha:.2f}: total norm = {total_norm:.2f}")

# Questions:
# 1. How does the total norm change as alpha varies?
# 2. Is the relationship linear?
# 3. What happens when alpha > 1.0 or alpha < 0.0 (extrapolation)?
```

## [Exercise 3.3] Velocity as a Weight Difference

The "velocity" in Model Swarms is itself a set of LoRA weights. Implement the operation `velocity = personal_best - current_position` and analyze the resulting velocity vector:

```python
personal_best = load_file("path/to/personal_best/adapter_model.safetensors")
current = load_file("path/to/current/adapter_model.safetensors")

velocity = {}
for key in personal_best:
    velocity[key] = personal_best[key] - current[key]

# Analyze the velocity:
# 1. What is the magnitude (L2 norm) of the velocity?
# 2. What is the cosine similarity between the velocity and the
#    current position?
# 3. How does velocity magnitude change across layers?
#    (Plot norm per layer)
```

## [Exercise 3.4] Conceptual Questions

1. If all 10 initial experts were trained on the same data split (same domain), how would this affect Model Swarms' ability to find good solutions? Relate your answer to the PSO concept of "swarm diversity."

2. The population expansion step uses weights `w_1 ∈ [0, 2]` (allowing extrapolation). Why might extrapolation be beneficial compared to staying within the convex hull (`w_1 ∈ [0, 1]`)? What risks does it introduce?

3. The paper uses LoRA rank 16 for all adapters. What would happen if you used rank 4 instead? Rank 64? Think about the trade-off between expressiveness and interpolation quality.

4. LoRA merging treats all layers identically — the same weight `α` is applied to every tensor. Could per-layer or per-module weights improve results? What would the downsides be?

---

**Next: [Module 4 — The Model Swarms Algorithm: Deep Dive →](module_04_algorithm_deep_dive.md)**
