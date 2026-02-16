# Module 6: Hands-On Lab — Running Experiments

**Estimated time: 45 minutes**

This module walks you through actually running Model Swarms. You'll set up the environment, run a minimal experiment, and interpret the results.

---

## 6.1 Hardware Requirements

| Resource | Minimum | Recommended | Paper's Setup |
|----------|---------|-------------|---------------|
| GPUs | 1× 24GB (e.g., RTX 3090) | 4-5× 24GB+ | 5× A100 80GB |
| RAM | 32GB | 64GB | 128GB+ |
| Disk | 50GB free | 100GB free | 500GB+ |
| Time per run | ~2-4 hours (1 GPU) | ~30-60 min (5 GPUs) | ~20-30 min |

If you have limited resources, we provide resource-saving configurations below.

---

## 6.2 Environment Setup

```bash
# Step 1: Clone the repository
git clone https://github.com/BunsenFeng/model_swarm.git
cd model_swarm

# Step 2: Create conda environment
conda env create -f swarm.yml
conda activate swarm

# Step 3: Authenticate with Hugging Face
# (Required for Gemma model access — you need to accept the license first)
# Visit https://huggingface.co/google/gemma-7b-it and accept the terms
huggingface-cli login

# Step 4: Download initial expert LoRA adapters
cd initial_experts
python initial_experts.py
cd ..

# Step 5: Verify the download
ls initial_experts/
# Expected output: 10 directories (cot, code, flan, lima, etc.)
# Each contains adapter_config.json and adapter_model.safetensors

# Step 6: Verify GPU access
python -c "import torch; print(f'GPUs: {torch.cuda.device_count()}')"
```

### Troubleshooting

**"Can't access Gemma model"**: Make sure you've accepted the Gemma license on Hugging Face and your token is correctly configured.

**"CUDA out of memory"**: Gemma-7B in float16 requires ~14GB VRAM. If your GPU has less, you'll need to use 8-bit quantization (add `load_in_8bit=True` to the model loading call in `evaluate.py`).

**"safetensors not found"**: The initial experts download may have failed. Check that each directory under `initial_experts/` contains an `adapter_model.safetensors` file.

---

## 6.3 Inspecting the Initial Experts

Before running the search, let's understand what we're starting with:

```python
# inspect_experts.py - Run this to understand your initial experts
import os
import json
import torch
from safetensors.torch import load_file

expert_dir = "initial_experts"
experts = sorted([d for d in os.listdir(expert_dir)
                  if os.path.isdir(os.path.join(expert_dir, d))])

print(f"Found {len(experts)} initial experts:")
for expert in experts:
    safetensors_path = os.path.join(expert_dir, expert, "adapter_model.safetensors")
    if os.path.exists(safetensors_path):
        state_dict = load_file(safetensors_path, device="cpu")
        total_params = sum(v.numel() for v in state_dict.values())
        total_norm = sum(torch.norm(v).item() for v in state_dict.values())
        print(f"  {expert:20s}: {total_params:>10,} params, "
              f"norm={total_norm:.2f}, "
              f"layers={len(state_dict)} tensors")
    else:
        print(f"  {expert:20s}: MISSING safetensors file!")
```

### Examining the Data

```python
# Look at an evaluation dataset
import json

dataset = json.load(open("data/eval/nlgraph.json"))
print(f"Keys: {dataset.keys()}")  # typically: dev, test
print(f"Dev examples: {len(dataset['dev'])}")
print(f"Test examples: {len(dataset['test'])}")

# Examine a single example
example = dataset['dev'][0]
print(f"\nExample question: {example['question'][:200]}...")
print(f"Example answer: {example['answer']}")
```

---

## 6.4 Running Your First Search (Resource-Efficient)

We'll run a minimal search with reduced parameters for faster iteration.

### Create a Minimal Search Script

```bash
#!/bin/bash
# search_minimal.sh - Resource-efficient first run

python search.py \
    -n my_first_search \
    -e exact_match \
    -d nlgraph \
    -g 0 \
    --inertia 0.2 \
    --cognitive_coeff 0.3 \
    --social_coeff 0.4 \
    --repel_coeff 0.1 \
    --step_length 0.8 \
    --starting_test_set_eval 1 \
    --fast_merge 1 \
    --project_name_wb my_first_swarm \
    --weight_randomess 1 \
    --populate_initial_experts 1 \
    --initial_experts_num 10 \
    --starting_velocity_mode random \
    --repel_term 1 \
    --step_length_factor 0.95 \
    --restart_stray_particles 1 \
    --restart_patience 0.67 \
    -p 5 \
    -m 20 \
    --dropK 0.3 \
    --dropN 0.3
```

Key differences from the paper's settings:
- `--initial_experts_num 10` (instead of 20): fewer particles, less computation
- `-g 0`: single GPU
- `-p 5` (patience of 5 instead of 10): earlier stopping
- `-m 20` (max 20 iterations instead of 200): hard cap
- `--dropK 0.3 --dropN 0.3`: skip 30% of evaluations

### Run It

```bash
# Make sure you're in the model_swarm directory
bash search_minimal.sh
```

### What to Expect

The output will show:
1. "initializing search..." — Population expansion + initial evaluation
2. "iteration 1!" — First search iteration
3. For each iteration: particle updates, evaluations, new bests
4. Eventually: "patience reached!" or max iterations hit
5. "ending search and starting test set evaluation..."
6. Final metrics

### Monitor Progress

In a separate terminal:

```bash
# Watch the log file
tail -f search/my_first_search_*/log.txt

# Check the utility scratchpad
cat search/my_first_search_*/utility_scratchpad.json | python -m json.tool | head -50
```

---

## 6.5 Interpreting the Results

After the search completes, examine the output:

```python
import json
import os

# Find the search directory
search_dirs = [d for d in os.listdir("search") if d.startswith("my_first_search")]
search_dir = os.path.join("search", sorted(search_dirs)[-1])  # most recent

# Load the utility scratchpad
with open(os.path.join(search_dir, "utility_scratchpad.json")) as f:
    scratchpad = json.load(f)

# Global best history
g_history = scratchpad["g_history"]
print(f"Global best history ({len(g_history)} entries):")
for i, g in enumerate(g_history):
    marker = " ← improved!" if i > 0 and g > g_history[i-1] else ""
    print(f"  Iteration {i}: {g:.4f}{marker}")

print(f"\nStarting global best: {g_history[0]:.4f}")
print(f"Ending global best:   {g_history[-1]:.4f}")
print(f"Improvement: {g_history[-1] - g_history[0]:.4f} "
      f"({(g_history[-1] - g_history[0]) / g_history[0] * 100:.1f}%)")

# Per-particle analysis
print(f"\nPer-particle starting → ending best:")
for i in range(10):
    key = f"particle_{i}_history"
    if key in scratchpad:
        history = scratchpad[key]
        best = scratchpad[f"particle_{i}_best"]
        print(f"  Particle {i}: {history[0]:.4f} → {best:.4f} "
              f"(Δ={best - history[0]:.4f})")
```

### Plotting Convergence

```python
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Global best over iterations
ax1.plot(g_history, 'b-', linewidth=2, label='Global best')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Utility (accuracy)')
ax1.set_title('Global Best Convergence')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: All particles' current scores over iterations
for i in range(10):
    key = f"particle_{i}_history"
    if key in scratchpad:
        ax2.plot(scratchpad[key], alpha=0.5, label=f'Particle {i}')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Utility (accuracy)')
ax2.set_title('All Particle Trajectories')
ax2.legend(fontsize=7, ncol=2)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('convergence_plot.png', dpi=150)
plt.show()
```

---

## 6.6 Comparing with Baselines

To appreciate what the search achieves, compare against simple baselines:

### Baseline 1: Best Single Expert

```python
# The starting global best IS the best single expert score
best_single = g_history[0]
print(f"Best single expert: {best_single:.4f}")
```

### Baseline 2: Uniform Soup

```python
# Merge all experts with equal weights
from merge import lora_merge
from evaluate import evaluate

expert_paths = sorted([
    os.path.join("initial_experts", d)
    for d in os.listdir("initial_experts")
    if os.path.isdir(os.path.join("initial_experts", d))
])

weights = [1.0 / len(expert_paths)] * len(expert_paths)
os.makedirs("search/uniform_soup", exist_ok=True)
lora_merge(weights, expert_paths, "search/uniform_soup", 0, 1)

uniform_score = evaluate("search/uniform_soup", "exact_match",
                         "nlgraph", 0, "google/gemma-7b-it", False)
print(f"Uniform soup: {uniform_score:.4f}")
print(f"Model Swarms: {g_history[-1]:.4f}")
print(f"Gain over uniform soup: {g_history[-1] - uniform_score:.4f}")
```

---

## 6.7 Experimenting with Hyperparameters

Now that you have a baseline run, try varying hyperparameters:

### Experiment 1: Inertia

```bash
# Low inertia (more responsive to cognitive/social signals)
python search.py -n low_inertia -e exact_match -d nlgraph -g 0 \
    --inertia 0.05 --cognitive_coeff 0.3 --social_coeff 0.4 \
    --repel_coeff 0.1 --step_length 0.8 --fast_merge 1 \
    --populate_initial_experts 1 --initial_experts_num 10 \
    -p 5 -m 20

# High inertia (more momentum, slower convergence)
python search.py -n high_inertia -e exact_match -d nlgraph -g 0 \
    --inertia 0.5 --cognitive_coeff 0.3 --social_coeff 0.4 \
    --repel_coeff 0.1 --step_length 0.8 --fast_merge 1 \
    --populate_initial_experts 1 --initial_experts_num 10 \
    -p 5 -m 20
```

### Experiment 2: With vs. Without Repulsion

```bash
# With repulsion (default)
python search.py -n with_repel -e exact_match -d nlgraph -g 0 \
    --repel_term 1 --repel_coeff 0.1 ...

# Without repulsion
python search.py -n no_repel -e exact_match -d nlgraph -g 0 \
    --repel_term 0 ...
```

### Experiment 3: Number of Particles

```bash
# 5 particles (minimal)
python search.py -n particles_5 --initial_experts_num 5 ...

# 10 particles (moderate)
python search.py -n particles_10 --initial_experts_num 10 ...

# 20 particles (paper default)
python search.py -n particles_20 --initial_experts_num 20 ...
```

---

## 6.8 Running a Multi-Task Experiment

To try the multi-task objective (if you have the resources):

```bash
python search.py \
    -n legal_multitask \
    -e multitask \
    -d legal \
    -g 0 \
    --inertia 0.2 \
    --cognitive_coeff 0.3 \
    --social_coeff 0.4 \
    --repel_coeff 0.1 \
    --step_length 0.8 \
    --fast_merge 1 \
    --populate_initial_experts 1 \
    --initial_experts_num 10 \
    -p 5 -m 15
```

The multi-task setting runs TWO evaluation datasets per particle per iteration (hearsay + citation prediction for legal domain), so it takes roughly twice as long per iteration.

---

## 6.9 Using the Resulting Model

After the search, the best model is in `search/<name>/global_best/`. To use it:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

base_model = "google/gemma-7b-it"
adapter_path = "search/my_first_search_*/global_best"

model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16)
model.load_adapter(adapter_path)
model.to("cuda:0")

tokenizer = AutoTokenizer.from_pretrained(base_model)

# Generate a response
prompt = "What is the shortest path between node A and node D in a graph where..."
inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
outputs = model.generate(**inputs, max_new_tokens=100, do_sample=False)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## [Exercise 6.1] Run and Analyze

Run the minimal search script from Section 6.4. Then:

1. Plot the global best convergence curve
2. Identify which particle became the global best
3. Was that particle originally one of the top-performing experts, or a "diamond in the rough"?
4. How many iterations ran before patience triggered?

## [Exercise 6.2] Baseline Comparison

Implement and evaluate these additional baselines:

1. **Random soup**: Average 3 randomly selected experts
2. **Top-2 average**: Average the top 2 experts by initial validation score
3. **Top-3 average**: Average the top 3 experts by initial validation score

Compare all baselines against Model Swarms' final result.

## [Exercise 6.3] Hyperparameter Impact

Run at least 3 different hyperparameter configurations (vary one parameter at a time). Create a table summarizing:

| Configuration | Final Global Best | Iterations to Converge | Best Particle Origin |
|--------------|------------------|----------------------|---------------------|
| Default | ... | ... | ... |
| Low inertia | ... | ... | ... |
| No repulsion | ... | ... | ... |

Which hyperparameter had the largest impact on performance?

## [Exercise 6.4] Custom Utility Function

If you're feeling adventurous, modify `evaluate.py` to add a new evaluation type. Suggestions:
- **Perplexity on a domain corpus**: Evaluate how well the model predicts text in a specific domain
- **Combined safety + accuracy**: Geometric mean of accuracy on a QA task and safety (1 - toxicity) on a generation task
- **Length-penalized generation**: Score based on answer quality with a penalty for overly long outputs

---

**Next: [Module 7 — Results, Analysis & Ablation Studies →](module_07_results_analysis.md)**
