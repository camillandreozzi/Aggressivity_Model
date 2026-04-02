# Aggressivity_Model

A small computational repository for reconstructing and extending the strategic models of aggression discussed in Richard Dawkins's *The Selfish Gene*, especially the Hawk–Dove model from Chapter 5, *Aggression: stability and the selfish machine*.

## Motivation

This repository starts from a simple question:

> Can a classic evolutionary game-theoretic model of aggression be reconstructed clearly in Python and then extended into a broader project in evolutionary dynamics?

The first goal is not to build a biologically realistic simulator immediately. It is to begin with the smallest transparent model that captures the logic of strategic conflict.

That first model is the Hawk–Dove game.

---

## Theoretical background

In Chapter 5 of *The Selfish Gene*, Dawkins presents aggression not as a vague personality trait but as a strategic problem. The key idea is that the success of a behavioral strategy depends on the strategies used by others in the population.

The Hawk–Dove model formalizes this.

- **Hawk** escalates conflict.
- **Dove** avoids serious escalation and relies on display or retreat.

The important lesson is that neither pure aggression nor pure peacefulness is automatically favored. What matters is the payoff structure.

Dawkins uses an illustrative numerical example in which:

- winning a contested resource gives a payoff of `50`,
- losing gives `0`,
- serious injury costs `100`,
- a prolonged nonviolent display costs `10`.

From these assumptions, the payoff matrix becomes:

```text
           Opponent
           Hawk   Dove
Player Hawk  -25    50
       Dove    0    15
```

This yields a mixed equilibrium in which the stable hawk proportion is:

```text
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

The numerical values in the basic Hawk–Dove model are illustrative, not empirical. Dawkins explicitly presents the model as a simple one meant to clarify strategic logic rather than reproduce nature directly.

That matters for the scope of this repository.

This project begins as:

- a reconstruction,
- a computational learning tool,
- a stepping stone toward richer models.

It should not be mistaken for a calibrated biological model unless later stages add empirical grounding.

---

## Historical note

Dawkins later noted in the endnotes that one of the chapter's claims about Retaliator being evolutionarily stable was incorrect, and that dynamic computer simulation pointed instead to a stable mixture of Hawks and Bullies in that more complex game.

This repository takes that correction seriously.

One of the long-term aims is therefore not just to reproduce the original chapter, but to compare:

- verbal ESS reasoning,
- payoff-matrix logic,
- dynamic simulation,
- stochastic or finite-population behavior.

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

Even the first script already addresses real conceptual questions:

- Why is all-aggression unstable?
- Why is all-peacefulness unstable?
- Why can a mixed equilibrium be stable even if it is not best for every individual?
- How does evolutionary stability differ from collective welfare?

These are central themes of Chapter 5.

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

- Richard Dawkins, *The Selfish Gene*, Chapter 5: *Aggression: stability and the selfish machine*

Also relevant in the same book:

- Dawkins's later endnotes correcting the claim about Retaliator,
- the broader discussion of selfish genes, strategic interaction, and evolutionary stability.

---

## License

Add a license here if you want the repository to be public and reusable.

Common choices:

- `MIT` for open reuse,
- `Apache-2.0` for a more explicit patent-oriented structure.
