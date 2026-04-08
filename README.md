# Evolutionary Game Theory Simulations


7/12 ≈ 0.583333
```

So the stable state is neither all hawks nor all doves.

This is the conceptual starting point of the repository.

---

## What this repository is for

This repo is organized as a gradual modelling project.

### Phase 1 — Minimal deterministic model

Implement the two-strategy Hawk–Dove game with replicator dynamics.

Goal:

- define the payoff matrix,
- compute expected payoffs,
- simulate the hawk proportion through time,
- verify convergence to the theoretical mixed equilibrium.

### Phase 2 — Finite-population / agent-based model

Move from expected payoffs to explicit random pairwise interactions.

Goal:

- simulate contests between individuals,
- track realized instead of expected payoffs,
- compare deterministic and stochastic dynamics.

### Phase 3 — More strategic richness

Add conditional strategies such as:

- Retaliator,
- Bully,
- Prober-retaliator.

This follows Dawkins's own discussion of more complex strategies beyond the minimal Hawk–Dove example.

### Phase 4 — Extensions in evolutionary dynamics

Possible future directions:

- finite-population stochasticity,
- mutation,
- spatial or network interaction,
- parameter sweeps,
- sensitivity analysis,
- comparison between ESS reasoning and dynamic simulation.

---

## Repository structure

Suggested layout:

```text
Aggressivity_Model/
├── README.md
├── requirements.txt
├── docs/
│   └── hawk_dove_minimal_explanation.md
├── figures/
├── src/
│   └── hawk_dove_minimal.py
└── notebooks/
```

---

## Current implementation

The first script is:

```text
src/hawk_dove_minimal.py
```

It implements the smallest useful deterministic model.

Core features:

- parameter block for payoff values,
- Hawk–Dove payoff matrix,
- expected payoff computation,
- average population payoff,
- replicator-dynamics update,
- theoretical mixed-equilibrium calculation,
- saved plots of hawk frequency and expected payoffs.

For a line-by-line explanation, see:

[`docs/hawk_dove_minimal_explanation.md`](docs/hawk_dove_minimal_explanation.md)

---

## Why replicator dynamics first

Replicator dynamics is the cleanest first implementation because it expresses the core evolutionary idea directly:

- strategies that perform better than average increase,
- strategies that perform worse than average decrease.

This makes it possible to verify the theoretical equilibrium before introducing stochasticity or finite-population effects.

---

## Important conceptual note



## Historical note



---

## Installation

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `requirements.txt` is not yet present, the minimal dependencies are:

```bash
pip install numpy matplotlib
```

---

## Running the minimal model

From the repository root:

```bash
python src/hawk_dove_minimal.py
```

Expected output:

- a printed theoretical equilibrium,
- a simulated final hawk frequency,
- saved plots in `figures/`.

---

## Minimal research questions behind the repo



---

## Roadmap

Planned additions:

- [ ] multi-start deterministic experiments
- [ ] finite-population agent-based simulation
- [ ] stochastic encounter model
- [ ] conditional strategies
- [ ] parameter sweeps for `V`, `C`, and `D`
- [ ] notebook visualizations
- [ ] comparison of ESS predictions with dynamic simulation

---

## References

Primary conceptual source:



## License

Add a license here if you want the repository to be public and reusable.

Common choices:

- `MIT` for open reuse,
- `Apache-2.0` for a more explicit patent-oriented structure.
