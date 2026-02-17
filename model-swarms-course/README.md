# Model Swarms: Collaborative LLM Adaptation via Swarm Intelligence

## A Comprehensive Course on the Paper, Theory, and Code

**Paper:** [Model Swarms: Collaborative Search to Adapt LLM Experts via Swarm Intelligence](https://arxiv.org/abs/2410.11163)  
**Authors:** Shangbin Feng, Zifeng Wang, Yike Wang, Sayna Ebrahimi, Hamid Palangi, Lesly Miculicich, Achin Kulshrestha, Nathalie Rauschmayr, Yejin Choi, Yulia Tsvetkov, Chen-Yu Lee, Tomas Pfister  
**Venue:** ICML 2025  
**Code:** [github.com/BunsenFeng/model_swarm](https://github.com/BunsenFeng/model_swarm)

---

## Course Overview

This course provides a deep, hands-on exploration of the Model Swarms paper — a method that applies **Particle Swarm Optimization (PSO)** to adapting and composing multiple LLM experts in weight space. The curriculum remains notebook-first, but reusable code now lives in `src/model_swarms_course` and is validated with linting, typing, tests, and notebook checks.

### Who This Course Is For

- Python developers with solid data science and ML fundamentals
- Practitioners familiar with PyTorch, Hugging Face Transformers, and basic LLM concepts
- Researchers interested in model merging, ensemble methods, and optimization

### Prerequisites

- Python 3.11+
- PyTorch experience (tensor operations, model loading, GPU usage)
- Familiarity with Hugging Face `transformers` and `peft` libraries
- Understanding of LoRA adapters (reviewed in Module 3)

### Estimated Time: 5–6 Hours

---

## Course Modules

| Module | Title | Format | Est. Time |
|--------|-------|--------|-----------|
| 1 | [Introduction: Why Model Swarms?](module_01_introduction.ipynb) | Reading + Discussion | 30 min |
| 2 | [Background: Swarm Intelligence & PSO](module_02_swarm_intelligence.ipynb) | Theory + Code | 45 min |
| 3 | [Background: LLM Experts, LoRA & Model Merging](module_03_lora_and_merging.ipynb) | Theory + Code | 45 min |
| 4 | [The Model Swarms Algorithm: Deep Dive](module_04_algorithm_deep_dive.ipynb) | Paper Analysis + Code | 60 min |
| 5 | [Code Architecture & Implementation Walkthrough](module_05_code_walkthrough.ipynb) | Code Reading | 45 min |
| 6 | [Hands-On Lab: Running Experiments](module_06_hands_on_lab.ipynb) | Lab | 45 min |
| 7 | [Results, Analysis & Ablation Studies](module_07_results_analysis.ipynb) | Paper Analysis + Exercises | 45 min |
| 8 | [Advanced Topics: Token Swarms, Extensions & Open Problems](module_08_advanced_topics.ipynb) | Reading + Exercises | 30 min |
| -- | [Exercises & Coding Challenges](exercises.ipynb) | Hands-on | integrated |

---

## Quick Start (mise + uv)

```bash
mise install
mise run setup
mise run verify
```

### Individual checks

```bash
mise run lint
mise run typecheck
mise run test
mise run notebooks:check
```

### Running notebooks interactively

```bash
uv run jupyter lab
```

---

## Heavy Experiment Path (Optional)

Default verification is CPU-only and deterministic. For full paper-style experiments (Module 6), additionally install heavy deps:

```bash
uv sync --group heavy
```

You may also need:

1. GPU-enabled machine
2. Hugging Face auth for gated models
3. Original repo + model artifacts

```bash
git clone https://github.com/BunsenFeng/model_swarm.git
cd model_swarm
huggingface-cli login
# follow upstream instructions for heavyweight downloads / training
```

---

## Repository Structure

```text
model-swarms-course/
├── .mise.toml
├── pyproject.toml
├── uv.lock
├── src/model_swarms_course/             # shared course utilities used by notebooks
├── tests/                               # deterministic unit tests
├── docs/engineering-workflow.md         # contributor workflow
├── module_01_introduction.ipynb
├── ...
└── exercises.ipynb
```

For daily development conventions and troubleshooting, see [`docs/engineering-workflow.md`](docs/engineering-workflow.md).
