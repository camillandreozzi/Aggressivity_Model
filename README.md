# Evolutionary Game Theory Simulations

This repository is a small but growing collection of simulations inspired by the work of **John Maynard Smith** and the development of **evolutionary game theory**.

Rather than treating strategy as something chosen by perfectly rational agents, evolutionary game theory studies what happens when different behavioural types reproduce, compete, and change in frequency over time. In that setting, success is not defined by abstract rationality alone, but by whether a strategy can persist, spread, or resist invasion in a population.

This repository focuses on simple, interpretable models that help make those ideas concrete through simulation.

---

## John Maynard Smith

John Maynard Smith was one of the central figures in twentieth-century theoretical biology. Trained originally as an engineer and later becoming a major evolutionary biologist, he helped bring mathematical reasoning into the study of behaviour, conflict, and adaptation.

He is especially known for developing **evolutionary game theory** as a biological framework. His work showed that strategic interaction is not only a matter for economics or philosophy, but also a core part of evolution itself. Organisms do not need to consciously calculate optimal choices: if a behavioural strategy performs well in a population, it can spread by natural selection.

Among his best-known contributions is the concept of the **Evolutionarily Stable Strategy (ESS)**: a strategy that, once common in a population, cannot easily be invaded by an alternative strategy. This idea became one of the foundations of modern evolutionary thinking about conflict, cooperation, signalling, and social behaviour.

Maynard Smith’s work connects directly to classic models such as:

- Hawk–Dove conflict
- Rock–Paper–Scissors style cyclic competition
- signalling and contest behaviour
- frequency-dependent selection more broadly

This repository is built in that intellectual tradition.

---

## What is evolutionary game theory?

Evolutionary game theory studies populations of interacting strategies.

The key idea is that the success of a strategy depends on the strategies it meets. In other words, fitness is often **frequency-dependent**. A strategy may do well when rare and poorly when common, or vice versa.

This makes evolutionary game theory different from simpler fixed-fitness models. Instead of assigning each type a constant reproductive advantage, it models interaction itself as the source of selective pressure.

Typical questions include:

- Which strategies increase when rare?
- Is there a stable mixture of strategies?
- Does the system converge to equilibrium or cycle over time?
- Can one strategy resist invasion by another?
- How closely do simulations match theoretical ESS predictions?

The models in this repository are intended as computational illustrations of those questions.

---

## Models currently simulated

At the moment, the repository contains two evolutionary game theory systems.

### 1. Aggressivity model: Hawk vs Dove

This is the classic **Hawk–Dove** game associated with conflict over shared resources.

The basic interpretation is:

- **Hawk** escalates conflict
- **Dove** avoids costly escalation

The model captures a central Maynard Smith insight: aggressive behaviour is not always expected to take over completely. When fights are costly enough, selection can favour a **mixed equilibrium** rather than a population of only aggressive or only peaceful individuals.

This model is the natural starting point for the repository because it introduces:

- payoff matrices
- expected payoffs
- frequency-dependent selection
- replicator dynamics
- theoretical mixed equilibria
- comparison between analytical prediction and simulation

### 2. Rock–Paper–Scissors model: side-blotched lizard game

This model represents a **cyclic dominance system**, where no single strategy is universally best.

It is inspired by the well-known side-blotched lizard example, where alternative mating strategies can behave in a Rock–Paper–Scissors pattern:

- one strategy beats a second,
- the second beats a third,
- the third beats the first.

This type of system is important because it shows that evolutionary dynamics do not always settle to a simple fixed point. Depending on the formulation, they may instead produce:

- oscillations,
- cyclic invasions,
- long transients,
- or coexistence maintained by strategic turnover.

This makes the lizard game an excellent contrast to Hawk–Dove: one model emphasizes mixed equilibrium under conflict, the other emphasizes cyclic competition.

---

## Purpose of the repository

This repository is meant to be a clear modelling workspace for evolutionary game theory.

Its goals are to:

- implement classic evolutionary game models in a transparent way,
- connect simulation output to theory,
- provide interpretable examples of frequency-dependent selection,
- and create a base for gradually richer evolutionary dynamics.

The emphasis is on conceptual clarity first, and model complexity second.

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
│   ├── hawk_dove_minimal.py
│   ├── hawk_dove_box_with_time_series.py
│   └── rps_side_blotched_lizard.py
└── notebooks/
