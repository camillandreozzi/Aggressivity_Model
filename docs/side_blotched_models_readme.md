# Side-Blotched Lizard Models

This document explains the three side-blotched lizard simulations in the repository:

- `src/rps_side_blotched_lizard.py` — the **simple** well-mixed deterministic model
- `src/side_blotched_advanced.py` — the **advanced** well-mixed stochastic model with mutation and simplex visualization
- `src/side_blotched_spatial.py` — the **spatial** local-interaction model on a grid

Together, these files form a progression from a minimal evolutionary game model to richer evolutionary-dynamics simulations.

---

## Biological context

The side-blotched lizard system is a classic example of **cyclic dominance**. In a stylized Rock–Paper–Scissors interpretation, the three male morphs correspond to three strategic types:

- **Orange**: aggressive, high-contest, territorial strategy
- **Blue**: mate-guarding, cooperative or defensive territorial strategy
- **Yellow**: sneaker strategy

The key idea is that no one strategy is globally best. Instead:

- orange tends to do well against blue,
- blue tends to do well against yellow,
- yellow tends to do well against orange.

This produces **frequency-dependent selection**: the success of a morph depends on how common the other morphs currently are.

That is the core reason this system is naturally modeled with **evolutionary game theory**.

---

## The three versions

### 1. The simple model
To understand the **basic game logic**.

It is the best entry point for:
- payoff matrices,
- cyclic dominance,
- frequency-dependent selection,
- total population growth with density dependence,
- and time series.

### 2. The advanced model
Use this when the goal is to move closer to a more realistic evolutionary-dynamics simulation.

It adds:
- **stochastic births and deaths**,
- **mutation / morph switching at reproduction**,
- **integer counts instead of only smooth deterministic trajectories**,
- and a **simplex plot** showing the population composition trajectory in three-strategy space with a finite population constraint.

### 3. The spatial model
Use this when the goal is to study what changes once interactions become **local rather than well-mixed**.

It adds:
- a 2D grid,
- local neighborhoods,
- spatial colonization,
- local competition,
- mutation,
- and spatial pattern formation.

This version is useful for studying coexistence through spatial structure and the difference between global averages and local ecological structure.

---

# 1. `rps_side_blotched_lizard.py` — simple model

## Concept

This is a **well-mixed deterministic ecological game model**.

"Well-mixed" means every morph effectively interacts with the whole population through global frequencies. There is no space, no local neighborhood, and no randomness.

The model tracks **absolute populations** of the three morphs:

- orange,
- blue,
- yellow.

Let:

- \(N_i\) = absolute population of morph \(i\),
- \(N_{\text{tot}} = \sum_i N_i\) = total population,
- \(x_i = N_i / N_{\text{tot}}\) = frequency of morph \(i\).

The model uses:

\[
\frac{dN_i}{dt} = N_i\Big(r + s(Ax)_i - cN_{\text{tot}}\Big)
\]

where:

- \(r\) is baseline growth,
- \(s\) is selection strength,
- \(A\) is the payoff matrix,
- \(c\) is the crowding coefficient.

So this script combines:
- an **evolutionary game term** \((Ax)_i\),
- with an **ecological density-dependence term** \(-cN_{\text{tot}}\).

## What it shows

The output figure has two main pieces of information:

1. **Absolute population expansion**
   - how large the orange, blue, and yellow populations become,
   - and how the total population changes over time.

2. **Morph frequencies**
   - how the relative composition changes,
   - whether the three morphs oscillate,
   - and whether one morph becomes temporarily dominant.

## Main parameters

### `INITIAL_POPULATIONS`
Sets the starting absolute counts for orange, blue, and yellow.

This changes the starting point of the trajectory, but not the underlying game itself.

### `BASE_GROWTH`
The baseline per-capita growth rate shared by all morphs.

Higher values make the whole population grow faster when density is low.

### `CROWDING`
The strength of density dependence.

Higher values push the total population down sooner. Lower values allow larger total populations.

### `SELECTION_STRENGTH`
How strongly the Rock–Paper–Scissors game affects growth.

Higher values make the cyclic strategic effects more pronounced.

### `PAYOFF_MATRIX`
The game itself.

In the simple model the matrix is:

```python
PAYOFF_MATRIX = np.array([
    [ 0.0,  1.0, -1.0],
    [-1.0,  0.0,  1.0],
    [ 1.0, -1.0,  0.0],
])
```

with morph order:

```python
[orange, blue, yellow]
```

This means:
- orange does well against blue and badly against yellow,
- blue does well against yellow and badly against orange,
- yellow does well against orange and badly against blue.

So this matrix encodes the Rock–Paper–Scissors cycle directly.

## When to use this version

Use the simple script when you want:
- a clear first model,
- easy parameter tuning,
- fast computation,
- and an intuitive demonstration of cyclic dominance.

---

# 2. `side_blotched_advanced.py` — advanced model

## Concept

This is a **well-mixed stochastic model** with:

- births,
- deaths,
- mutation,
- density dependence,
- and frequency-dependent selection.

It still assumes the population is well-mixed, but it is much richer than the simple version.

Instead of smooth deterministic population updates, it uses **Poisson birth and death events** and treats population counts as integers.

## Core logic

At each time step:

1. Current morph frequencies are computed from current counts.
2. The payoff matrix is applied to those frequencies.
3. Payoffs modify per-capita birth rates.
4. Death rates depend on:
   - a baseline death rate,
   - plus density dependence through total population size.
5. Births and deaths are drawn stochastically.
6. Offspring may **mutate** into a different morph according to the mutation matrix.

This means the model includes both:
- **selection**, because some morphs reproduce more successfully depending on current composition,
- and **innovation / switching**, because offspring are not guaranteed to keep the parent morph.

## What is new compared with the simple model

### Stochasticity
The same parameters do not always produce exactly the same counts unless the random seed is fixed.

This lets the model capture:
- demographic noise,
- random fluctuations,
- and more realistic-looking trajectories.

### Mutation matrix
This script introduces:

```python
MUTATION_MATRIX
```

where row \(i\) gives the probabilities that a parent of morph \(i\) produces orange, blue, or yellow offspring.

So if the orange row is:

```python
[0.985, 0.010, 0.005]
```

that means an orange parent produces:
- orange offspring with probability 0.985,
- blue offspring with probability 0.010,
- yellow offspring with probability 0.005.

This prevents the model from being locked into perfectly inherited morph identity.

### Simplex plot
This is one of the most useful additions.

Because the system has three morphs whose frequencies sum to one, the population state can be represented in a **triangle simplex**.

- one corner = all orange,
- one corner = all blue,
- one corner = all yellow,
- interior points = mixed populations.

The simplex plot shows how the system moves through three-strategy state space over time.

## Main parameters

### `BASE_BIRTH`
Baseline birth rate before game effects.

### `BASE_DEATH`
Baseline death rate before density effects.

### `CROWDING`
Density-dependent contribution to mortality.

### `SELECTION_STRENGTH`
How strongly payoffs modify birth success.

### `PAYOFF_MATRIX`
Same strategic meaning as in the simple model.

### `MUTATION_MATRIX`
Controls morph switching at reproduction.

### `RANDOM_SEED`
Controls reproducibility of the stochastic run.

### `INITIAL_COUNTS`
Initial integer population counts.

## What the figure contains

The figure has three components:

1. **Absolute populations** over time
2. **Morph frequencies** over time
3. **Simplex trajectory** of frequency composition

This makes it much easier to separate:
- ecological scale,
- frequency composition,
- and cyclic state-space motion.

## When to use this version

Use the advanced script when you want:
- a better research-style model,
- mutation,
- demographic noise,
- frequency trajectory geometry,
- and a bridge between simple deterministic dynamics and spatial models.

---

# 3. `side_blotched_spatial.py` — spatial model

## Concept

This is a **local-interaction spatial model** on a 2D toroidal grid.

Each site can be:
- empty,
- orange,
- blue,
- or yellow.

A toroidal grid means the boundaries wrap around. There are no edges in the ecological sense.

The model is no longer well-mixed. Instead, everything depends on **local neighborhoods**.

## Why this matters

In real ecological systems, individuals do not interact uniformly with the whole population. They interact locally through:
- territory,
- proximity,
- movement,
- mate access,
- and local crowding.

Spatial structure can change evolutionary outcomes dramatically.

A morph that would disappear in a well-mixed model may persist locally in patches. Cycles can occur through waves or invasion fronts rather than only through global oscillations.

## Core logic

At each update:

### Empty sites
An empty site can be colonized by neighboring occupied sites.

The probability of colonization depends on:
- nearby parent availability,
- local payoff of the parent,
- baseline colonization rate,
- and mutation at reproduction.

### Occupied sites
An occupied site can die.

Death depends on:
- baseline death,
- local crowding,
- and local payoff.

So success is determined locally, not globally.

## Neighborhood choice

The script allows two neighborhood definitions:

### `"von_neumann"`
Four neighbors:
- up,
- down,
- left,
- right.

### `"moore"`
Eight neighbors:
- the four above,
- plus the four diagonals.

This is controlled by:

```python
NEIGHBORHOOD
```

The Moore neighborhood usually gives denser local interaction and smoother spatial patterning.

## State coding

The model uses integer site states:

- `-1` = empty
- `0` = orange
- `1` = blue
- `2` = yellow

## What is new compared with the advanced model

### Space
The most important change is that interaction is local.

### Empty sites
The model explicitly includes habitat occupancy and vacancy.

### Colonization
Reproduction is represented as local colonization into empty sites.

### Local crowding
Density is not only a global total. It is experienced locally.

### Spatial snapshots
The output figure includes images of the grid at different times, so you can see:
- patch formation,
- spatial turnover,
- clustering,
- and invasion structure.

## Main parameters

### `GRID_NX`, `GRID_NY`
Dimensions of the spatial grid.

Larger grids reduce finite-size artifacts and usually produce richer spatial structure, but they are slower.

### `N_STEPS`
Number of update steps.

### `P_INIT_EMPTY`, `P_INIT_ORANGE`, `P_INIT_BLUE`, `P_INIT_YELLOW`
Initial probabilities for site states.

These determine the initial habitat occupancy and starting morph composition.

### `BASE_COLONIZATION`
Baseline rate at which occupied neighboring sites colonize empty sites.

### `BASE_DEATH`
Baseline mortality of occupied sites.

### `LOCAL_CROWDING`
Additional mortality generated by local density.

### `SELECTION_STRENGTH`
How strongly local payoff affects colonization success.

### `MUTATION_MATRIX`
Morph switching at reproduction.

### `PAYOFF_MATRIX`
Local Rock–Paper–Scissors structure.

## What the figure contains

The figure includes:

1. **Spatial snapshots** of the lattice
2. **Global count trajectories** over time
3. **Occupancy fraction and morph frequencies among occupied sites**

This combination is important because the same global frequencies can correspond to very different spatial arrangements.

## When to use this version

Use the spatial script when you want:
- local ecological interaction,
- patch formation,
- habitat occupancy,
- spatial invasion patterns,
- and a less mean-field description of the system.

---

# How the three models relate mathematically

## Simple
A deterministic mean-field ecological game:

\[
\frac{dN_i}{dt} = N_i\Big(r + s(Ax)_i - cN_{\text{tot}}\Big)
\]

This is best thought of as a **minimal ecological extension** of a three-strategy evolutionary game.

## Advanced
A stochastic well-mixed birth–death–mutation model.

It keeps the same global frequency-dependent logic, but introduces:
- integer counts,
- random births,
- random deaths,
- mutation at reproduction.

## Spatial
A local colonization–death model on a grid.

It replaces global interaction frequencies with local neighborhoods and makes ecological structure explicit.

---

# Recommended use in the repository

A good way to present these files is:

- `rps_side_blotched_lizard.py` as the **introductory / minimal model**
- `side_blotched_advanced.py` as the **main well-mixed research model**
- `side_blotched_spatial.py` as the **structured-population extension**

This creates a natural progression:

1. understand the core game,
2. add mutation and stochasticity,
3. add local spatial structure.

---

# Suggested short descriptions for the main repo README

## Simple model
A deterministic well-mixed Rock–Paper–Scissors ecological simulation showing cyclic dominance, total population expansion, and morph frequencies over time.

## Advanced model
A stochastic well-mixed side-blotched lizard model with mutation, integer birth–death dynamics, density dependence, and simplex visualization of the three-morph trajectory.

## Spatial model
A local-interaction lattice model with empty sites, local colonization, local crowding, mutation, and spatial snapshots showing patch formation and invasion structure.

---

# File placement

This document is intended to live in:

```text
/docs/side_blotched_models_readme.md
```

A good top-level link from the repository `README.md` would be:

```md
[`docs/side_blotched_models_readme.md`](docs/side_blotched_models_readme.md)
```

