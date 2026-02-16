# Module 7: Results, Analysis & Ablation Studies

**Estimated time: 45 minutes**

This module dives into the paper's experimental results. We'll analyze each table and figure, understand what the numbers mean, and explore the ablation studies that reveal *why* the algorithm works.

---

## 7.1 Single-Task Results (Table 1)

Open the paper to **Table 1** (page 6). This is the main results table for Objective 1: adapting LLM experts to a single task.

### The Numbers

| Task Category | Tasks | Best Baseline | Model Swarms | Improvement |
|--------------|-------|---------------|-------------|-------------|
| Knowledge | MMLU, MMLU-pro, HellaSwag | Varies | SOTA on all 3 | +4.9% avg |
| Reasoning | GSM8k, K-Crosswords, NLGraph | Varies | SOTA on all 3 | +21.0% avg |
| Safety | TruthfulQA, RealToxicity, AbstainQA | Varies | SOTA on all 3 | +14.1% avg |

Key observations:

**1. Reasoning sees the largest gains (+21%).** This makes sense intuitively: reasoning tasks require combining multiple capabilities (mathematical knowledge + step-by-step logic + output formatting), and the swarm search is uniquely equipped to find weight configurations that activate these complementary capabilities simultaneously.

**2. Knowledge sees the smallest gains (+4.9%).** Knowledge tasks are closer to simple memorization/recall. The individual experts already have most of the knowledge they need; the search primarily finds better weighting rather than discovering new capabilities.

**3. GSM8k improvement is 29.7%.** This is the single largest improvement and is remarkable. GSM8k requires mathematical reasoning over word problems — the search apparently discovers weight configurations where mathematical and linguistic capabilities reinforce each other.

### Baseline Analysis

Look at how different baselines perform across categories:

- **Uniform Soup** is consistently mediocre — it dilutes expertise
- **Greedy Soup** is decent on knowledge but poor on reasoning — the greedy addition strategy misses non-linear complementarities
- **LoraHub** (gradient-based) performs well on some tasks but poorly on others — the gradient signal from 200 examples is insufficient for reliable optimization
- **DARE-TIES** and **SLERP** are competitive on knowledge but fall behind on reasoning and safety — static merging can't handle the complexity of multi-capability tasks

---

## 7.2 Multi-Task Results (Table 2)

**Table 2** shows Objective 2: adapting to an entire domain (two tasks simultaneously).

### The Pareto Optimality Finding

The most interesting result here isn't just that Model Swarms wins — it's the observation of **Pareto-optimal experts**. The paper reports:

> "We observe that the best expert for the legal domain is not the best expert for either hearsay or citation prediction individually."

This means the search found a weight configuration that is **jointly better** on both tasks than any expert optimized for either task alone. The harmonic mean utility function successfully steered the search toward balanced, multi-capable solutions.

### Cross-Domain Variation

| Domain | Improvement |
|--------|------------|
| Legal | +10.9% average |
| Medical | +4.2% average |
| Science | +3.8% average |
| Culture | +4.0% average |

Legal sees the largest gain. One hypothesis: legal reasoning requires a specific combination of language understanding (hearsay detection) and structural knowledge (citation patterns) that no single expert possesses, but the swarm can discover.

---

## 7.3 Reward Model Results (Table 4)

**Table 4** tests Objective 3: steering generation toward different reward models.

### The Steerability Result

This table reveals something subtle. Most baselines show a trade-off:

| Method | General RM | Verbose RM | Concise RM |
|--------|-----------|-----------|-----------|
| SLERP | Good | **Good** | Poor |
| DARE-TIES | Moderate | Good | Poor |
| Model Swarms | **Best** | **Best** | **Best** |

SLERP and DARE-TIES tend to produce verbose models — their merging strategies inadvertently favor verbosity. Only Model Swarms achieves SOTA on the **concise** reward model while also being SOTA on the verbose one.

This demonstrates "steerability" — the algorithm genuinely adapts its output to match whatever reward function you specify, rather than finding a single "generally good" model.

### Practical Implication

If you have a production scenario where different users want different response styles (some prefer detailed explanations, others prefer brief answers), Model Swarms can produce specialized models for each preference from the same initial expert pool. No retraining needed — just change the utility function.

---

## 7.4 Human Interest Results (Table 3)

**Table 3** evaluates Objective 4: adapting to niche human interest topics.

### Win Rate Analysis

The paper reports human evaluation win rates against the best baseline, across 16 topics:

| Performance Band | Number of Topics | Examples |
|-----------------|-----------------|---------|
| Strong win (>80%) | 4 | Electric vehicles, PhD applications |
| Moderate win (60-80%) | 7 | Indoor gardening, board games |
| Marginal win (50-60%) | 3 | Cocktail recipes, pet care |
| Loss (<50%) | 2 | Specific niche topics |

**Average win rate: 70.8%**

The topics where Model Swarms loses tend to be ones requiring very specific factual knowledge that none of the initial experts possess. This confirms an important limitation: **the search adapts existing knowledge, it doesn't create new knowledge**. If no expert knows about a topic, the swarm can't learn it from scratch.

### Extremely Low-Resource Setting

These experiments use only **25 validation examples** per topic (not the 200 used elsewhere). That the search still works with 25 examples is notable — it suggests that the utility function landscape, even with very few data points, is smooth enough for PSO to navigate productively.

---

## 7.5 Correctness Emergence (Section 4.5, Figure 4)

This is perhaps the paper's most scientifically interesting finding.

### What Is Correctness Emergence?

The paper defines two metrics:
- **C-surge**: Percentage of questions where the final model answers correctly but at least one initial expert answered incorrectly
- **C-emerge**: Percentage of questions where the final model answers correctly but **ALL** initial experts answered incorrectly

### The Numbers

| Metric | Range | Mean |
|--------|-------|------|
| C-surge | 40-55% | ~48% |
| C-emerge | 36-53.5% | ~44% |

**44% C-emerge means**: On average, for almost half the problems that NO initial expert could solve, the swarm-optimized model CAN solve them.

### Why This Matters

This contradicts the naive view that model merging can only redistribute existing capabilities. The search doesn't just pick the best expert per question — it discovers weight configurations where capabilities from different experts combine synergistically to solve previously unsolvable problems.

This is analogous to how combining ingredients can create flavors that none of the individual ingredients possess. The whole becomes greater than the sum of its parts.

### Possible Mechanisms

The paper doesn't provide a definitive mechanistic explanation, but several hypotheses are plausible:

1. **Cross-capability activation**: Expert A has knowledge X, Expert B has reasoning pattern Y. Combining their weights activates a pathway where X feeds into Y, producing correct answers to questions requiring both.

2. **Destructive interference removal**: Some expert weights may actively suppress correct answers (e.g., a safety-trained expert might refuse to answer certain questions). The search finds weight configurations that reduce these suppressions.

3. **Distributional alignment**: The combined model may have a token distribution that better matches the expected output format, improving parsing accuracy.

---

## 7.6 Diamond in the Rough (Section 4.6)

### The Finding

89.6% of final best particles were NOT the initially highest-performing expert.

56.9% of final best particles started in the **bottom half** of performance rankings.

### Interpretation

The initial performance of an expert on a validation set is a poor predictor of its contribution to the final optimized model. An expert that scores 45% on a task might contain weight configurations that, when combined with other experts' weights, reach 75%.

This has practical implications: **don't prune "weak" experts from your pool**. Their weakness on the target task doesn't mean they lack valuable capabilities — it might just mean those capabilities aren't aligned with the task in their current weight configuration.

### Connection to PSO Dynamics

In PSO terms, a "diamond in the rough" particle starts in a low-fitness region but, through velocity updates influenced by higher-performing particles, navigates to a high-fitness region that other particles haven't explored. The particle's unique starting position gives it access to different regions of weight space.

---

## 7.7 Ablation Studies (Table 5)

The paper includes ablation studies that systematically remove or modify components of the algorithm. These are crucial for understanding which design choices actually matter.

### Component Ablations

| Ablation | Effect on Performance |
|----------|---------------------|
| Remove repulsion term | -5 to -10% on most tasks |
| Remove randomness (deterministic coefficients) | -5 to -15% |
| Remove particle restart | -3 to -8% |
| Zero initial velocity (instead of random) | -2 to -5% |
| Reduce particle count (10 → 5) | -5 to -12% |

### Key Takeaways

**1. Randomness is essential.** Without stochastic coefficients, particles converge too quickly to a single point, losing the diversity that enables exploration. The performance drop of 5-15% is the largest single-component ablation.

**2. Repulsion helps more than expected.** The repulsion term (which has no counterpart in classic PSO) provides a meaningful improvement. It acts as a regularizer, preventing the swarm from collapsing toward bad solutions.

**3. Particle restart is a modest but consistent win.** It prevents wasted computation on "zombie" particles, giving them a fresh chance to contribute.

**4. More particles is better.** But with diminishing returns — the jump from 5 to 10 particles is much more impactful than from 10 to 20.

---

## 7.8 Diversity Analysis (Section 4.7, Figure 5)

The paper runs a controlled experiment on expert diversity.

### Setup

Total particles: 20 (held constant). Vary the number of distinct experts:
- **1×20**: 1 unique expert, duplicated 20 times
- **2×10**: 2 unique experts, each duplicated 10 times
- **5×4**: 5 unique experts, each duplicated 4 times
- **10×2**: 10 unique experts, each duplicated 2 times
- **10×1 + interpolated**: 10 unique experts, 10 more created via interpolation (the paper's default)

### Results

Performance increases monotonically with diversity. The gain from 1×20 to 10×2 is approximately +35%.

### Why Diversity Matters in PSO Terms

With low diversity:
- All particles start in similar regions of weight space
- Personal bests cluster in a small neighborhood
- The swarm effectively becomes a single-particle search with noise
- Exploration is limited to a tiny region of the vast weight space

With high diversity:
- Particles start in different regions, each with unique capabilities
- Personal bests span a wider area, creating broader gradients for the social term
- The swarm effectively covers more of the weight space
- Cross-pollination between diverse regions is more likely to discover emergent capabilities

---

## 7.9 Computational Analysis

### Search Efficiency

Typical search trajectories:
- **Initial best** is established at iteration 0
- **Major improvements** happen in iterations 1-10
- **Refinements** in iterations 10-20
- **Convergence** (patience triggered) at iterations 15-30

The search rarely needs more than 30 iterations. With N=20 particles, this means ~600 model evaluations total — each involving a forward pass on 200 validation examples.

### Cost Comparison

| Method | Evaluations Needed | Gradient Computations | Other Costs |
|--------|-------------------|----------------------|-------------|
| Best Single Expert | N (test each expert) | 0 | None |
| Uniform Soup | 1 (merge + test) | 0 | 1 merge |
| LoraHub | 1 (per gradient step) | Many | Gradient computation |
| Model Swarms | ~300-600 | 0 | ~3000-6000 merges |

Model Swarms is more expensive than simple baselines but cheaper than gradient-based methods (which require backpropagation through the full model). The 3000-6000 merge operations are fast (each takes <1 second on CPU).

---

## [Exercise 7.1] Results Interpretation

Look at Table 1 from the paper and answer:

1. On which task does Model Swarms have the SMALLEST advantage over the best baseline? What might explain this?
2. On which task does Model Swarms have the LARGEST advantage? What does this task require that other tasks don't?
3. If you were a practitioner with limited compute, which tasks would you use Model Swarms for vs. simpler baselines?

## [Exercise 7.2] Design Your Own Ablation

Propose an ablation study NOT in the paper. For example:
- What if you used a different normalization strategy (L2 normalization instead of sum)?
- What if the step length increased when improvement is detected and decreased otherwise (adaptive scheduling)?
- What if global worst was the worst of the last K iterations rather than the all-time worst?

For your proposed ablation:
1. State your hypothesis (what you expect to happen)
2. Describe the experimental setup
3. Define the metric you'd use to measure success

## [Exercise 7.3] Correctness Emergence Analysis

Using the convergence data from your Lab run (Module 6), approximate C-surge and C-emerge:

```python
import json

# Load predictions from initial experts and final best
search_dir = "search/my_first_search_*"

# Load initial predictions (from "now" directories at start)
# Load final predictions (from "personal_best" of global best particle)
# Compare: which questions went from wrong → right?
# Count: how many questions were wrong in ALL initial experts but right in final?
```

## [Exercise 7.4] Scaling Analysis

Based on the paper's results, sketch a graph predicting how Model Swarms would perform with:
- 2, 5, 10, 20, 50, 100 initial experts
- 50, 100, 200, 500, 1000 validation examples

For each axis, predict whether the relationship is:
- Linear
- Logarithmic (diminishing returns)
- Step function (threshold effect)
- Something else

Justify your predictions with evidence from the paper.

## [Exercise 7.5] Critical Analysis

Write a short (3-4 paragraph) critical review of the paper's experimental methodology. Consider:

1. Are the baselines fair and comprehensive?
2. Are the evaluation metrics appropriate?
3. What confounding factors might explain the results?
4. What experiments are missing that would strengthen the claims?
5. How would you design a follow-up experiment to address the biggest weakness?

---

**Next: [Module 8 — Advanced Topics: Token Swarms, Extensions & Open Problems →](module_08_advanced_topics.md)**
