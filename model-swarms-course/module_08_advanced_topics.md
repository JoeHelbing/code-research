# Module 8: Advanced Topics — Token Swarms, Extensions & Open Problems

**Estimated time: 30 minutes**

---

## 8.1 Token Swarms: Beyond Shared Architectures

A fundamental limitation of weight-space swarms: **all models must share the same architecture.** You can't combine a Gemma-7B adapter with a Mistral-7B adapter because their weight tensors have different structures.

**Token Swarms** solve this by moving the search from weight space to **output probability space**.

### How Token Swarms Work

Instead of each particle being a set of model weights, each particle is a **weighted combination of output probability distributions**:

```
For input x and vocabulary token v:
  p_combined(v|x) = Σ_j w_{i,j} * p_j(v|x)
```

where `p_j(v|x)` is model j's probability of token v given input x, and `w_{i,j}` are mixture weights (analogous to a location in probability space).

The PSO update operates on these mixture weights rather than on model weights:

```
Particle i's "position" = [w_{i,1}, w_{i,2}, ..., w_{i,M}]  (one weight per model)
```

### Advantages and Disadvantages

| Aspect | Weight Swarms | Token Swarms |
|--------|--------------|-------------|
| Architecture requirement | All same architecture | Any architecture |
| What's searched | LoRA weight space | Probability mixture space |
| Dimensionality | ~18M (LoRA params) | M (number of models) |
| Capabilities discovered | New weight configs | New probability blends |
| Can create new behaviors | Yes (weight synergies) | Limited (convex combinations of existing outputs) |

### Preliminary Results

The paper reports Token Swarms with 4 Gemma + 4 Mistral models achieving **+29.3% average improvement** across datasets. This is competitive with weight-based swarms despite the architectural heterogeneity.

### Implementation Sketch

```python
class TokenSwarmParticle:
    def __init__(self, n_models):
        # Position: mixture weights over models
        self.weights = np.random.dirichlet(np.ones(n_models))
        # Velocity: direction of weight change
        self.velocity = np.random.randn(n_models) * 0.1

    def generate(self, models, tokenizer, prompt, max_tokens=100):
        """Generate text using weighted probability combination."""
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        generated = input_ids.clone()

        for _ in range(max_tokens):
            # Get probability distributions from all models
            all_probs = []
            for model in models:
                with torch.no_grad():
                    logits = model(generated).logits[:, -1, :]
                    probs = torch.softmax(logits, dim=-1)
                    all_probs.append(probs)

            # Weighted combination
            combined_probs = sum(
                w * p for w, p in zip(self.weights, all_probs)
            )

            # Sample next token
            next_token = torch.argmax(combined_probs, dim=-1)
            generated = torch.cat([generated, next_token.unsqueeze(0)], dim=-1)

            if next_token.item() == tokenizer.eos_token_id:
                break

        return tokenizer.decode(generated[0], skip_special_tokens=True)
```

---

## 8.2 Limitations and Honest Assessment

### Limitation 1: Adaptation, Not Learning

Model Swarms reallocates existing knowledge — it doesn't create new knowledge from scratch. The paper confirms this with a perplexity experiment: using perplexity (a memorization proxy) as the utility function doesn't lead to meaningful improvement.

**Implication**: If your task requires knowledge that no expert possesses (e.g., facts from after the training cutoff), Model Swarms won't help. You'll need retrieval augmentation or additional fine-tuning.

### Limitation 2: Local Optima

The weight space is non-convex. PSO provides no guarantee of finding the global optimum. The mitigation strategies (random coefficients, repulsion, restart, diversity) help but don't solve the problem theoretically.

**Implication**: Results are stochastic. Different random seeds produce different outcomes. The paper likely reports best-of-several runs (standard practice but worth noting).

### Limitation 3: Evaluation Cost

Each iteration requires N model evaluations. For large models or large validation sets, this becomes expensive. The dropout-K/N mechanism helps but introduces its own approximation error.

**Implication**: The method scales poorly with model size. A 70B model would require ~10x more compute per evaluation than a 7B model, making each search proportionally more expensive.

### Limitation 4: Utility Function Design

The algorithm is only as good as its utility function. A poorly designed utility function leads to a well-optimized but useless model. For example:
- Using accuracy on a biased dataset → model learns biases
- Using reward model scores → model learns to game the reward model
- Using too few validation examples → overfitting to the validation set

### Limitation 5: LoRA Constraint

The requirement that all experts be LoRA adapters of the same base model limits the expert pool. In practice, the most diverse and capable experts often use different base architectures.

---

## 8.3 Extensions and Future Directions

### Extension 1: Adaptive Hyperparameters

Current Model Swarms uses fixed hyperparameters (inertia, coefficients) throughout the search. Adaptive variants could:
- Increase inertia when diversity drops (encourage exploration)
- Increase social coefficient when progress stalls (encourage exploitation)
- Adjust step length based on improvement rate rather than a fixed schedule

### Extension 2: Multi-Objective Optimization

The current multi-task setting uses a single scalar utility (harmonic mean). True multi-objective PSO (MOPSO) maintains a **Pareto front** of non-dominated solutions:

```
Solution A dominates Solution B if A is better on ALL objectives.
The Pareto front = set of all non-dominated solutions.
```

This would give users a menu of models along the Pareto front rather than a single "best" model.

### Extension 3: Continual Adaptation

The paper treats each search as a one-shot process. A continual version could:
- Start from the previous search's best when new data arrives
- Add/remove experts from the pool over time
- Track distribution shift through utility function changes

### Extension 4: Heterogeneous Search Spaces

Combining weight-space search (for same-architecture models) with token-space search (for cross-architecture models) in a unified framework.

### Extension 5: Learned Utility Functions

Instead of hand-designing utility functions, learn them from human preferences:
```
human ranks outputs → train reward model → use as utility function → run swarm
```
This creates a pipeline from human feedback to model adaptation without any gradient-based training.

---

## 8.4 Connection to the MoCo Framework

The README notes that "a better implementation is now available in [MoCo](https://github.com/BunsenFeng/model_collaboration)." MoCo (Model Collaboration) generalizes Model Swarms to a broader framework for model composition research.

If you continue working in this area, the MoCo codebase is the recommended starting point for new experiments.

---

## 8.5 Broader Context: Where Is Model Composition Going?

Model Swarms is one point in a rapidly evolving design space:

### The Spectrum of Model Composition

```
Simple ←──────────────────────────────────────────────→ Complex
Averaging    Merging     Routing      Swarms      MoE Training

- Uniform    - TIES      - cBTM       - Model     - GShard
  Soup       - DARE      - Pack of      Swarms    - Switch
- Greedy     - SLERP       LLMs       - Token       Transformer
  Soup       - Model     - Branch-      Swarms    - Mixtral
               Stocks      Train-
                           Merge
```

The trend is toward methods that are:
1. **More dynamic** — adapting the composition to the specific input or task
2. **More data-efficient** — working with fewer examples
3. **More modular** — allowing easy addition/removal of components
4. **More theoretically grounded** — with convergence guarantees

Model Swarms advances (1), (2), and (3) but lacks (4). Future work combining swarm dynamics with theoretical optimization guarantees would be valuable.

---

## 8.6 Ethical Considerations

The paper acknowledges a dual-use risk: the utility function determines what the model optimizes for. This flexibility is a strength (adapt to any objective) and a risk (could optimize for harmful objectives).

Concrete risks:
- **Toxicity optimization**: Using a "toxicity score" as utility function would produce maximally toxic models
- **Bias amplification**: If the validation data reflects biases, the search will amplify them
- **Reward hacking**: If the utility function has exploitable shortcuts, the search will find them

Mitigations discussed in the paper:
- Careful utility function design with safety constraints
- Red-teaming the resulting models
- Restricting the expert pool to vetted, aligned models

---

## [Exercise 8.1] Token Swarms Implementation

Implement a simplified Token Swarms algorithm:

```python
class TokenSwarm:
    def __init__(self, models, tokenizer, n_particles=10):
        """
        Initialize a token swarm.

        Args:
            models: list of loaded language models
            tokenizer: shared tokenizer
            n_particles: number of particles (mixture weight sets)
        """
        self.models = models
        self.tokenizer = tokenizer
        self.n_particles = n_particles
        self.n_models = len(models)

        # Each particle is a set of mixture weights
        self.positions = [
            np.random.dirichlet(np.ones(self.n_models))
            for _ in range(n_particles)
        ]
        # Initialize velocities, bests, etc.
        # YOUR CODE HERE

    def evaluate_particle(self, particle_idx, validation_data):
        """Evaluate one particle on the validation set."""
        # YOUR CODE HERE
        pass

    def update(self):
        """Run one PSO iteration."""
        # YOUR CODE HERE
        pass
```

Test with 2-3 small models (e.g., GPT-2 variants) on a simple QA task.

## [Exercise 8.2] Multi-Objective Extension

Extend the Model Swarms algorithm to maintain a Pareto front instead of a single global best:

1. Define what "dominance" means for two particles with scores on two tasks
2. Implement Pareto front maintenance (adding/removing solutions)
3. Modify the social term: instead of attracting toward a single global best, attract toward a random point on the Pareto front
4. Test on a two-task scenario

## [Exercise 8.3] Scaling Laws Hypothesis

Based on everything you've learned, write a 1-page hypothesis paper predicting:

1. How does Model Swarms performance scale with:
   - Number of initial experts (n)
   - Number of particles (N)
   - Number of validation examples
   - Model size (7B vs. 13B vs. 70B)
   - LoRA rank

2. Where do you predict the method will break down?

3. What is the most important experiment to run to test your predictions?

## [Exercise 8.4] Literature Comparison

Read the abstract and method section of ONE of these related papers:
- [Model Soups](https://arxiv.org/abs/2203.05482) (Wortsman et al., 2022)
- [TIES-Merging](https://arxiv.org/abs/2306.01708) (Yadav et al., 2023)
- [Evolutionary Model Merge](https://arxiv.org/abs/2403.13187) (Akiba et al., 2024)

Write a 2-paragraph comparison with Model Swarms:
1. What does the other paper do differently?
2. In what scenarios would you prefer the other method over Model Swarms, and vice versa?

## [Exercise 8.5] Research Proposal

Write a 1-page research proposal for a follow-up paper to Model Swarms. Your proposal should include:

1. **Problem statement**: What limitation of Model Swarms does your proposal address?
2. **Proposed method**: What is your approach? (Be specific enough to implement.)
3. **Expected results**: What do you predict will happen?
4. **Evaluation plan**: How will you measure success?
5. **Baselines**: What methods will you compare against (including Model Swarms itself)?

---

## Course Conclusion

You've now completed a deep dive into Model Swarms, covering:

- **Module 1**: The problem of LLM adaptation and why existing approaches fall short
- **Module 2**: Swarm intelligence and PSO — the optimization foundation
- **Module 3**: LoRA adapters and model merging — the representation foundation
- **Module 4**: The complete Model Swarms algorithm — the core contribution
- **Module 5**: The implementation — how theory becomes code
- **Module 6**: Hands-on experimentation — running and interpreting results
- **Module 7**: Results analysis — what the paper proves and how
- **Module 8**: Extensions, limitations, and open problems

### Key Takeaways

1. **Simple algorithms can be powerful** when applied to the right representation. PSO is a 30-year-old algorithm. LoRA is straightforward. Their combination produces state-of-the-art results.

2. **Diversity is a resource.** The effectiveness of Model Swarms depends critically on having diverse initial experts. This principle applies broadly in ML.

3. **Emergence is real.** Combining model weights can produce capabilities that no individual model possesses. This is not intuitive and has deep implications for how we think about neural network representations.

4. **Utility function design is the new feature engineering.** As optimization methods become more powerful, the bottleneck shifts to specifying *what* to optimize, not *how* to optimize it.

5. **The field is moving fast.** Model composition is a rapidly evolving area. The techniques you've learned here are the foundation, but the specific methods will continue to advance.

---

**[Back to Course Overview →](README.md)**
