# Model Swarms: Collaborative LLM Adaptation via Swarm Intelligence

## A Comprehensive Course on the Paper, Theory, and Code

**Paper:** [Model Swarms: Collaborative Search to Adapt LLM Experts via Swarm Intelligence](https://arxiv.org/abs/2410.11163)
**Authors:** Shangbin Feng, Zifeng Wang, Yike Wang, Sayna Ebrahimi, Hamid Palangi, Lesly Miculicich, Achin Kulshrestha, Nathalie Rauschmayr, Yejin Choi, Yulia Tsvetkov, Chen-Yu Lee, Tomas Pfister
**Venue:** ICML 2025
**Code:** [github.com/BunsenFeng/model_swarm](https://github.com/BunsenFeng/model_swarm)

---

## Course Overview

This course provides a deep, hands-on exploration of the Model Swarms paper — a method that applies **Particle Swarm Optimization (PSO)** to the problem of adapting and composing multiple Large Language Model (LLM) experts. You will learn the theory behind swarm intelligence, understand how it translates to weight-space search over neural networks, implement key components from scratch, and run the authors' code to reproduce experiments.

The entire course is delivered as **interactive Jupyter notebooks** — theory, code, visualizations, and exercises are all integrated step by step.

### Who This Course Is For

- Python developers with solid data science and ML fundamentals
- Practitioners familiar with PyTorch, Hugging Face Transformers, and basic LLM concepts
- Researchers interested in model merging, ensemble methods, and optimization

### Prerequisites

- Strong Python (3.8+)
- PyTorch experience (tensor operations, model loading, GPU usage)
- Familiarity with Hugging Face `transformers` and `peft` libraries
- Understanding of what LoRA adapters are (we review this, but prior exposure helps)
- Basic optimization theory (gradient descent, loss landscapes)

### Estimated Time: 5-6 Hours

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

## How to Use This Course

1. **Work through the notebooks linearly.** The modules build on each other. Module 1 sets the context, Modules 2-3 provide necessary background, Module 4 is the core algorithm, Modules 5-6 are hands-on with the real code, and Modules 7-8 analyze results and extensions.

2. **Run the code cells.** Each notebook is designed to be executed top-to-bottom. Code cells produce visualizations, run tests, and demonstrate algorithms interactively. Fill in the exercise cells as you go.

3. **Do the exercises.** Each module contains inline exercises. The standalone [exercises notebook](exercises.ipynb) has larger coding challenges including a complete mini-swarm implementation, hyperparameter sensitivity analysis, and ablation studies.

4. **Read the paper alongside.** Keep [the paper](https://arxiv.org/abs/2410.11163) open. This course references specific sections, figures, and tables throughout.

---

## Quick Setup

```bash
# Install dependencies for the course notebooks
pip install numpy matplotlib torch safetensors jupyter

# Clone the Model Swarms repository (for Module 6 hands-on lab)
git clone https://github.com/BunsenFeng/model_swarm.git
cd model_swarm

# Create the conda environment
conda env create -f swarm.yml
conda activate swarm

# Login to Hugging Face (required for Gemma model access)
huggingface-cli login

# Download initial experts
cd initial_experts
python initial_experts.py
cd ..
```

---

## Key Concepts You Will Learn

- **Particle Swarm Optimization** — a population-based metaheuristic for non-convex search
- **Weight-space arithmetic** — how linearly combining model weights produces new behaviors
- **LoRA adapters** — efficient parameter representations that make weight-space search tractable
- **Utility functions** — how to define what "good" means for model adaptation
- **Collaborative search dynamics** — how particles balance exploration vs. exploitation
- **Correctness emergence** — how search discovers capabilities absent from any individual expert
- **Model composition baselines** — the landscape of existing approaches and where Model Swarms fits

---

## Repository Structure

```
model-swarms-course/
├── README.md                              # This file (syllabus)
├── module_01_introduction.ipynb           # Why Model Swarms?
├── module_02_swarm_intelligence.ipynb     # PSO theory + implementation
├── module_03_lora_and_merging.ipynb       # LoRA & model merging background
├── module_04_algorithm_deep_dive.ipynb    # The core algorithm
├── module_05_code_walkthrough.ipynb       # Reading the real code
├── module_06_hands_on_lab.ipynb           # Running experiments
├── module_07_results_analysis.ipynb       # Understanding the results
├── module_08_advanced_topics.ipynb        # Extensions & open problems
└── exercises.ipynb                        # Standalone coding challenges
```
