# Module 5: Code Architecture & Implementation Walkthrough

**Estimated time: 45 minutes**

In this module, we read and analyze the actual Model Swarms source code. Keep the [repository](https://github.com/BunsenFeng/model_swarm) open alongside this guide.

---

## 5.1 Repository Structure

```
model_swarm/
├── search.py              # Main algorithm: PSO search loop
├── evaluate.py            # Utility functions: model evaluation
├── merge.py               # Core operation: weighted LoRA merging
├── overall_metrics.py     # Post-search analysis and metrics
├── reward_modeling.py     # Reward model scoring (Objective 3)
├── search_nlgraph.sh      # Example: single-task search (NLGraph)
├── search_legal.sh         # Example: multi-task domain (Legal)
├── search_concise.sh       # Example: reward model (concise)
├── search_phd_application.sh  # Example: human interest
├── data/eval/             # Evaluation datasets (JSON format)
├── initial_experts/       # LoRA adapters + download script
├── search/                # Output directory (created at runtime)
├── swarm.yml              # Conda environment specification
└── LICENSE                # Apache 2.0
```

The codebase is compact — the entire algorithm fits in four Python files totaling ~1200 lines. This is deliberate and reflects the simplicity of the approach.

---

## 5.2 File-by-File Walkthrough

### `merge.py` — The Atomic Operation

This is the smallest and most important file. Every operation in Model Swarms — velocity computation, position update, population expansion — is expressed as a call to `lora_merge()`.

```python
def lora_merge(weights, lora_name_list, output_name, gpu_id,
               directly_load_safetensors=0):
```

**Two code paths:**

| Path | When | How | Speed |
|------|------|-----|-------|
| Slow merge | `directly_load_safetensors=0` | Loads full PEFT models via `AutoModelForCausalLM` | Slow (loads 7B model) |
| Fast merge | `directly_load_safetensors=1` | Loads only safetensor files | Fast (loads ~70MB) |

The fast merge path is always used in practice:

```python
# Fast path: load raw tensors, compute weighted sum, save
lora_state_dict_list = []
for lora_name in lora_name_list:
    state_dict = load_file(
        os.path.join(lora_name, "adapter_model.safetensors"),
        device="cpu"
    )
    lora_state_dict_list.append(state_dict)

final_state_dict = {}
for i in range(len(lora_state_dict_list)):
    for key in lora_state_dict_list[i].keys():
        if i == 0:
            final_state_dict[key] = weights[i] * lora_state_dict_list[i][key]
        else:
            final_state_dict[key] += weights[i] * lora_state_dict_list[i][key]

save_file(final_state_dict, os.path.join(output_name, "adapter_model.safetensors"))
```

**Key observation**: merging is done on CPU (`device="cpu"`). This is intentional — merge operations don't need GPU acceleration since they're just element-wise multiply-add on relatively small tensors. GPUs are reserved for model evaluation (inference).

---

### `evaluate.py` — The Utility Functions

This file implements evaluation for all four objectives. The main entry point:

```python
def evaluate(model_path, eval_type, dataset, gpu_id,
             base_model="google/gemma-7b-it", save_dev_flag=False,
             only_one_or_two=None, skip_flag=False):
```

**Model loading pattern:**

```python
try:
    # Try loading as base model + LoRA adapter
    model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16)
    model.load_adapter(model_path)
    model.to(f"cuda:{gpu_id}")
    tokenizer = AutoTokenizer.from_pretrained(base_model)
except:
    # Fallback: load as a standalone model
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)
    model.to(f"cuda:{gpu_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
```

The `try/except` pattern handles both LoRA adapters (primary use case) and standalone models (fallback). In practice, all particles are LoRA adapters, so the first path is always used.

**Evaluation types:**

| `eval_type` | Method | Output |
|-------------|--------|--------|
| `multiple_choice` | Parse model output for letter answer (A/B/C/D) | Accuracy score |
| `exact_match` | Check if gold answer appears in model output | Fraction correct |
| `external_api` | Generate text, score with Perspective API (toxicity) | 1 - toxicity score |
| `AbstainQA` | Two-pass: answer + self-check, compute effective reliability | Reliability metric |
| `multitask` | Run two evaluations, return harmonic mean | Harmonic mean |
| `rm_*` | Generate responses, score with reward model | Average RM score |
| `human` | Generate responses, score with Gemini-as-judge | Average 1-10 rating |

**The `multiple_choice` answer parser:**

```python
def multiple_choice_answer_parsing(instance_dict, output_text):
    # Try to find answer letter in first 5 characters
    for key in instance_dict["choices"].keys():
        if key in output_text[:5]:
            return key
    # Try last 5 characters
    for key in instance_dict["choices"].keys():
        if key in output_text[-5:]:
            return key
    # Try matching full option text
    for key in instance_dict["choices"].keys():
        if instance_dict["choices"][key].lower() in output_text.lower():
            return key
    return "Z"  # no match found
```

This is a cascading parser — it tries multiple strategies in decreasing order of reliability. The fallback "Z" ensures a non-matching answer rather than a random one.

**Batch generation:**

```python
def batch_generate(model, tokenizer, prompts, gpu_id,
                   batch_size=10, max_new_tokens=10):
    num_batches = math.ceil(len(prompts) / batch_size)
    outputs = []
    for i in tqdm(range(num_batches)):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(prompts))
        batch_prompts = prompts[start_idx:end_idx]

        input_ids = tokenizer(batch_prompts, return_tensors="pt",
                             padding=True).input_ids.to(f"cuda:{gpu_id}")
        output = model.generate(input_ids, max_new_tokens=max_new_tokens,
                               do_sample=False)

        for j in range(len(output)):
            outputs.append(tokenizer.decode(
                output[j][len(input_ids[j]):], skip_special_tokens=True
            ).strip())

        del input_ids, output
        torch.cuda.empty_cache()

    return outputs
```

Note `do_sample=False` — all generation is deterministic (greedy decoding). This ensures that the utility function is deterministic for the same model, which is important for PSO convergence (you don't want random noise in your fitness function).

---

### `search.py` — The Main Algorithm

This is the largest file (~400 lines). It orchestrates the entire search process.

**Argument parsing (lines 1-100):**

The script accepts ~30 command-line arguments. Key ones:

```python
argParser.add_argument("-n", "--name")              # experiment name
argParser.add_argument("-e", "--eval_type")          # evaluation type
argParser.add_argument("-d", "--dataset")             # dataset name
argParser.add_argument("-g", "--gpus")                # GPU IDs (e.g., "0,1,2,3")
argParser.add_argument("--inertia", default=0.4)
argParser.add_argument("--cognitive_coeff", default=0.3)
argParser.add_argument("--social_coeff", default=0.3)
argParser.add_argument("--repel_coeff", default=0.3)
argParser.add_argument("--step_length", default=1)
argParser.add_argument("-p", "--patience", default=10)
argParser.add_argument("-m", "--max_iteration", default=200)
argParser.add_argument("--populate_initial_experts", default=0)
argParser.add_argument("--initial_experts_num", default=None)
```

**Initialization (lines 100-200):**

```python
# Load particle paths
particle_paths = sorted([
    os.path.join(initial_expert_directory, p)
    for p in os.listdir(initial_expert_directory)
    if os.path.isdir(os.path.join(initial_expert_directory, p))
])

# Population expansion (if enabled)
if populate_initial_experts and initial_experts_num > len(particle_paths):
    for i in range(initial_experts_num - particles_now):
        parent_1 = random.choice(particle_paths)
        parent_2 = random.choice(particle_paths)
        w_1 = random.random() * 2
        w_2 = 1 - w_1
        lora_merge([w_1, w_2], [parent_1, parent_2], child_path, ...)
```

**The `initialize_search_records` function:**

This creates the directory structure:
```
search/<experiment_name>/
├── particle_0/
│   ├── now/           # current position (LoRA weights)
│   ├── personal_best/ # best position visited
│   └── velocity/      # current velocity (LoRA weights)
├── particle_1/
│   ├── now/
│   ├── personal_best/
│   └── velocity/
├── ...
├── global_best/       # best position across all particles
├── global_worst/      # worst position across all particles
└── utility_scratchpad.json  # all scores and history
```

Each `now/`, `personal_best/`, `velocity/`, etc. directory contains an `adapter_model.safetensors` file — a set of LoRA weights.

**The main search loop (lines 200-350):**

```python
iter_count = 0
while iter_count < max_iteration:
    iter_count += 1

    # Check patience (early stopping)
    g_history = utility_scratchpad["g_history"]
    if len(g_history) > patience:
        recent = g_history[-patience:]
        if max(recent) == min(recent):
            break

    # Determine restart flags for each particle
    for i in range(len(particle_paths)):
        if restart_stray_particles:
            # Check if particle has stagnated
            ...
            restart_flag = (stagnation_time >= restart_patience * patience)

    # Update all particles (parallelized across CPUs)
    update_args = [(i, gpu_id, ..., restart_flag) for i in range(N)]
    pool = Pool(processes=num_cpu_when_merging)
    pool.starmap(particle_update, update_args)

    # Evaluate all particles (parallelized across GPUs)
    eval_args = [(particle_path, eval_type, dataset, gpu_id, ...) for i in range(N)]
    pool = Pool(processes=len(gpus))
    results = pool.starmap(evaluate, eval_args)

    # Update tracking variables
    for i in range(N):
        if results[i] > personal_best[i]:
            update personal_best[i]
        if results[i] > global_best:
            update global_best
        if results[i] < global_worst:
            update global_worst

    # Decay step length
    step_length = max(step_length * step_length_factor, minimum_step_length)
```

**The `particle_update` function:**

This implements the velocity update for a single particle. It's the direct code implementation of the formula from Module 4:

```python
def particle_update(i, gpu_id, search_pass_name, weight_randomness,
                    inertia, cognitive_coeff, social_coeff, repel_coeff,
                    fast_merge, step_length, repel_term, restart_flag):

    # Handle restart
    if restart_flag:
        copy(personal_best → current_position)
        velocity = zero_vector

    # Sample random weights
    r_w, r_p, r_s, r_b = [random.uniform(0, 1)] * 4  # if randomness enabled

    # Compute normalized weights
    self_weight = r_w * inertia
    cognitive_weight = r_p * cognitive_coeff
    social_weight = r_s * social_coeff
    repel_weight = r_b * repel_coeff
    total = self_weight + cognitive_weight + social_weight + repel_weight
    # normalize...

    # Compute direction vectors as LoRA weight differences
    merge([1, -1], [personal_best, current])  → p_minus_x
    merge([1, -1], [global_best, current])    → g_minus_x
    merge([-1, 1], [global_worst, current])   → x_minus_gw

    # Combine into new velocity
    merge([self_w, cognitive_w, social_w, repel_w],
          [velocity, p_minus_x, g_minus_x, x_minus_gw]) → velocity

    # Position update
    merge([1, step_length], [current, velocity]) → current
```

**Parallelization strategy:**

| Operation | Parallelized How | Why |
|-----------|-----------------|-----|
| Merge operations | `Pool(processes=num_cpu_when_merging)` | Merging is CPU-bound (tensor arithmetic) |
| Evaluations | `Pool(processes=len(gpus))` | Evaluation is GPU-bound (model inference) |

The `assign_gpu` function distributes particles across GPUs:

```python
def assign_gpu(num_gpus, process_idx, total_processes):
    process_per_gpu = math.ceil(total_processes / num_gpus)
    gpu_idx = math.floor(process_idx / process_per_gpu)
    return gpu_idx
```

With 20 particles and 5 GPUs: particles 0-3 on GPU 0, 4-7 on GPU 1, etc.

---

### `overall_metrics.py` — Post-Search Analysis

After the search completes, this file computes final metrics:

```python
def overall_metrics(name, eval_type, top_k=10):
```

It computes:
- **Starting vs. ending best validation utility**: How much did the search improve?
- **Best single test accuracy**: Performance of the single best particle on held-out test data
- **Top-k ensemble accuracy**: Majority-vote ensemble of the k best particles on test data
- **Global best improvement count**: How many times did the global best improve?
- **Global best last change**: At which iteration did the last improvement occur?

The **ensemble metric** is interesting — it uses a utility-weighted majority vote:

```python
def ensemble_based_on_utility(preds, utility_list, top_k):
    # Select top-k particles by utility score
    # For each problem, take majority vote among top-k
    # Break ties by sum of utility scores
    ...
```

This provides a second evaluation dimension: not just "how good is the best model?" but "how good is the best committee of models?"

---

### Shell Scripts — Experiment Configuration

The shell scripts are hyperparameter sweep launchers. They:

1. Define search ranges for each hyperparameter
2. Randomly sample one value from each range
3. Launch `search.py` with those values
4. Loop forever (user kills the script when done)

```bash
# From search_nlgraph.sh
inertia_list=(0.1 0.2 0.3)
cognitive_coeff_list=(0.1 0.2 0.3 0.4 0.5)
social_coeff_list=(0.2 0.3 0.4 0.5 0.6)
repel_coeff_list=(0.01 0.05 0.1)
step_length_list=(0.5 0.6 0.7 0.8 0.9 1.0)

while true; do
    inertia=${inertia_list[$RANDOM % ${#inertia_list[@]}]}
    # ... sample other hyperparameters ...

    python search.py \
        -n nlgraph_{$inertia}_{$cognitive_coeff}_... \
        -e exact_match \
        -d nlgraph \
        -g 0,1,2,3,4 \
        --inertia $inertia \
        --populate_initial_experts 1 \
        --initial_experts_num 20 \
        ...
done
```

This random search strategy is effective because:
- Each run is independent and logged to W&B
- Bad hyperparameter combinations terminate quickly (patience kicks in)
- Good combinations can be identified post-hoc from W&B logs

---

## 5.3 Data Flow Diagram

```
┌─────────────────────────────────────────────────┐
│                    search.py                     │
│                                                  │
│  initial_experts/ ──────────────────────────┐    │
│       │                                     │    │
│       ▼                                     │    │
│  [Population Expansion] ←── merge.py        │    │
│       │                                     │    │
│       ▼                                     │    │
│  [Initial Evaluation] ←── evaluate.py       │    │
│       │                                     │    │
│       ▼                                     │    │
│  ┌─────────────────────┐                    │    │
│  │ Search Loop (×K)    │                    │    │
│  │                     │                    │    │
│  │ 1. Velocity Update  │ ←── merge.py (×6N)│    │
│  │ 2. Position Update  │ ←── merge.py (×N) │    │
│  │ 3. Evaluation       │ ←── evaluate.py   │    │
│  │ 4. Update trackers  │                    │    │
│  │ 5. Check patience   │                    │    │
│  │ 6. Decay step length│                    │    │
│  └─────────────────────┘                    │    │
│       │                                     │    │
│       ▼                                     │    │
│  [Final Evaluation] ←── evaluate.py         │    │
│       │              ←── overall_metrics.py  │    │
│       ▼                                     │    │
│  search/<name>/                              │    │
│  ├── global_best/                            │    │
│  ├── utility_scratchpad.json                 │    │
│  └── log.txt                                 │    │
└─────────────────────────────────────────────────┘
```

---

## 5.4 Key Design Decisions and Trade-offs

### Decision 1: File-System State Management

All state (particle positions, velocities, personal bests) is stored as files on disk, not in memory. This means:
- **Pro**: Each particle's state survives crashes; easy to inspect/debug
- **Pro**: Memory-efficient for large models
- **Con**: I/O overhead from constant read/write of safetensor files
- **Con**: Directory management complexity (lots of `shutil.copytree` calls)

### Decision 2: Multiprocessing for Parallelism

The code uses Python's `multiprocessing.Pool` rather than threading, distributed computing, or GPU-parallel evaluation. This means:
- **Pro**: Simple implementation; works on a single machine
- **Pro**: Each evaluation gets its own GPU (via `assign_gpu`)
- **Con**: Limited to one machine's GPUs
- **Con**: Process spawn overhead for each iteration

### Decision 3: Greedy Tracking (No History Reuse)

When a particle improves, its personal best is updated immediately. The code doesn't maintain a history of all positions visited — only the best. This means:
- **Pro**: Simple bookkeeping
- **Con**: Cannot retroactively analyze trajectories (except via the utility_scratchpad history)

### Decision 4: Random Hyperparameter Search

The shell scripts use random search rather than grid search or Bayesian optimization for hyperparameter tuning. Given the relatively low-dimensional hyperparameter space (5 parameters) and independent runs, random search is a reasonable choice.

---

## [Exercise 5.1] Code Reading

Open `search.py` and answer these questions:

1. What happens if `populate_initial_experts=0`? How many particles will the search use?
2. Find the line where `wandb.log()` is called. What metrics are logged per iteration?
3. The `clean_up_on_end` flag deletes auxiliary directories. Which directories are deleted? Which are kept? Why?
4. Explain why `torch.multiprocessing.set_start_method('spawn')` is called. What would happen with `fork`?

## [Exercise 5.2] The Evaluation Pipeline

Study `evaluate.py` and answer:

1. Why does the `multiple_choice` evaluation use `max_new_tokens=10`? What would happen with `max_new_tokens=1`?
2. In the `exact_match` evaluation for GSM8k, why does the code take `" ".join(output.split(" ")[-5:])` before checking for the answer? (Hint: GSM8k answers follow chain-of-thought reasoning.)
3. The `AbstainQA` evaluation involves two model inference passes. Describe both passes and explain what "effective reliability" measures.

## [Exercise 5.3] Merge Operation Analysis

Study `merge.py` and answer:

1. In the slow merge path, only one model object is created and reused for saving. Which one? Why?
2. The fast merge path loads everything to CPU. What would change if you loaded to GPU instead? (Consider memory and speed trade-offs.)
3. Write a test that verifies: `merge([0.5, 0.5], [A, A]) == A` (merging a model with itself at equal weights should return the same model).

## [Exercise 5.4] Architectural Improvement Proposals

Identify one limitation of the current implementation and propose a concrete improvement. Consider:
- Memory efficiency (e.g., could velocity be stored implicitly rather than as a separate set of weights?)
- Parallelization (e.g., could evaluations be distributed across multiple machines?)
- Convergence (e.g., could adaptive hyperparameter scheduling improve results?)
- Code quality (e.g., which parts would benefit from refactoring?)

Write a short (1-2 paragraph) design proposal for your improvement.

---

**Next: [Module 6 — Hands-On Lab: Running Experiments →](module_06_hands_on_lab.md)**
