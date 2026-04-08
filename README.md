# Evolutionary Game Theory Simulations

This repository is a small but growing collection of simulations inspired by the work of **John Maynard Smith** and the development of **evolutionary game theory**.

Evolutionary game theory studies what happens when different behavioural types reproduce, compete, and change in frequency over time. In that setting, success is defined by whether a strategy can survive, spread, or perish in a population.

This repository is built in the spirit that visualisation and simulation are best to learn and frame such theoretical concepts.

---

## John Maynard Smith

John Maynard Smith was one of the central figures in twentieth-century theoretical biology. 
He is especially known for developing **evolutionary game theory** as a biological framework. His work showed that strategic interaction is a core part of evolution. Organisms do not consciously calculate optimal choices, it is natural selection driving the performance of a behavioural strategy.

Among his best-known contributions is the concept of the **Evolutionarily Stable Strategy (ESS)**. With the term we refer to a strategy that, once common in a population, cannot easily be invaded by an alternative strategy. This idea became one of the foundations of modern evolutionary thinking about conflict, cooperation, signalling, and social behaviour.

---

## What is evolutionary game theory?

Evolutionary game theory studies populations of interacting strategies.
Fitness of a population is often **frequency-dependent**. A strategy may do well when rare and poorly when common, or vice versa. This makes evolutionary game theory peculiar in his biologically-rooted assumptions and constrains.

---

## Models currently simulated

At the moment, the repository contains two evolutionary game theory systems.

### 1. Aggressivity model: Hawk vs Dove

This is the classic **Hawk–Dove** game associated with conflict over shared resources.

There is only two types of creatures in the population:

- **Hawk** escalates conflict (the aggressive kind)
- **Dove** avoids conflict (the peaceful kind)

The insight captured my Maynard Smith is that aggressive behaviour is not always expected to take over completely, especially when fights are costly enough.
Selection favours a **mixed equilibrium** rather than a population of only aggressive or only peaceful individuals.

This model is an easy & natural starting point for the repository because it introduces:

- payoff matrices
- expected payoffs
- frequency-dependent selection
- replicator dynamics
- theoretical mixed equilibria
- comparison between analytical prediction and simulation

### 2. Rock–Paper–Scissors model: side-blotched lizard game

This model represents a **cyclic dominance system**, where no single strategy is universally best.

It is inspired by the well-known side-blotched lizard example (https://en.wikipedia.org/wiki/Side-blotched_lizard), where alternative mating strategies can behave in a Rock–Paper–Scissors pattern:

- one strategy beats a second,
- the second beats a third,
- the third beats the first

This type of system is important because it shows that evolutionary dynamics do not always settle to a simple fixed point. Depending on the formulation, they may instead produce:

- oscillations
- cyclic invasions
- long transients
- or coexistence maintained by strategic turnover

This makes the lizard game an excellent contrast to Hawk–Dove: one model emphasizes mixed equilibrium under conflict, the other emphasizes cyclic competition.

---

## Purpose of the repository

This repository is meant to be a clear modelling workspace for evolutionary game theory.

---

## Repository structure

Suggested layout:

```text
Aggressivity_Model/
├── README.md
├── requirements.txt
├── docs/
│   ├── hawk_dove_minimal_explanation.md
│   └── side_blotched_models_readme.md
├── figures/
├── src/
│   ├── hawk_dove_minimal.py
│   ├── hawk_dove_box_with_time_series.py
│   ├── side_blotched_advanced.py
│   ├── side_blotched_spatial.py
│   └── rps_side_blotched_lizard.py
└── notebooks/
```

---

## Current implementation

The repository currently includes simulations for:

- **Hawk–Dove**
- **Rock–Paper–Scissors / side-blotched lizard dynamics**

Core features across the implemented models include:

- explicit payoff structures
- expected payoff computation
- population-share updates through time
- visualisation of strategy frequencies
- and comparison with known theoretical behaviour

For the Hawk–Dove model, the current documentation is:

[`docs/hawk_dove_minimal_explanation.md`](docs/hawk_dove_minimal_explanation.md)

For the RPS Side-Blotched Lizard:

[`docs/side_blotched_models_readme.md`](docs/side_blotched_models_readme.md)

---

## Why start with these models?

These two systems give two of the cleanest introductions to evolutionary game theory. Together, they cover two core phenomena of the field:

- **stable mixed equilibria**
- **cyclic frequency-dependent dynamics**

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

## Running the models

From the repository root, run the relevant script, for example:

```bash
python src/hawk_dove_minimal.py
```

or

```bash
python src/rps_side_blotched_lizard.py
```

Expected output depends on the model, but typically includes:

- printed parameters or equilibrium information
- simulated strategy frequencies through time
- and saved plots in `figures/`


---

## References

Primary conceptual sources include the work of:

- **John Maynard Smith**
- George R. Price
- Richard Dawkins
- Martin A. Nowak
- other contributors to evolutionary game theory and evolutionary dynamics

---

## License

Add a license here if you want the repository to be public and reusable.

Common choices:

- `MIT` for open reuse
- `Apache-2.0` for a more explicit patent-oriented structure
