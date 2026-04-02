# `hawk_dove_minimal.py` — code explanation

This document explains the first minimal implementation of the Hawk–Dove model in the `Aggressivity_Model` repository.

## Where this file should go

Place this file here:

```text
Aggressivity_Model/
├── README.md
├── requirements.txt
├── docs/
│   └── hawk_dove_minimal_explanation.md
├── figures/
└── src/
    └── hawk_dove_minimal.py
```

Recommended GitHub path:

`docs/hawk_dove_minimal_explanation.md`

Then add a link to it from the root `README.md`.

---

## Purpose of the script

The goal of `src/hawk_dove_minimal.py` is to implement the smallest deterministic version of the Hawk–Dove game discussed in *The Selfish Gene*.

The script does four things:

1. defines the payoff matrix,
2. computes expected payoffs for hawks and doves,
3. updates the hawk proportion through replicator dynamics,
4. plots the trajectory of the population over time.

This is the cleanest first step because it isolates the core strategic idea before moving to finite-population or agent-based simulations.

---

## Theoretical background in one paragraph

In the Hawk–Dove model, individuals compete over a resource. Hawks escalate fights and risk injury. Doves avoid serious escalation and instead rely on display or retreat. The central question is not whether one strategy is always best, but whether a population can reach a stable strategic composition. In Dawkins's illustrative example, the stable proportion is not all hawks and not all doves, but a mixed equilibrium in which hawks make up `7/12` of the population.

---

## Code structure

The file is best read in six blocks.

### 1. Parameters

```python
V = 50
L = 0
C = 100
D = 10
```

These are the numerical assumptions of the toy model.

- `V`: value of winning the resource
- `L`: payoff from losing
- `C`: cost of serious injury
- `D`: cost of a long display / time waste

These are deliberately simple illustrative values.

---

### 2. Payoff matrix

```python
A = np.array([
    [(V - C) / 2, V],
    [L, (V / 2) - D]
], dtype=float)
```

This matrix encodes the payoff to the **row player**.

Rows and columns are ordered as:

- row/column `0`: Hawk
- row/column `1`: Dove

So the entries mean:

- `A[0,0]`: Hawk vs Hawk
- `A[0,1]`: Hawk vs Dove
- `A[1,0]`: Dove vs Hawk
- `A[1,1]`: Dove vs Dove

With the chosen values, this becomes:

```python
[[-25, 50],
 [  0, 15]]
```

Interpretation:

- Hawk vs Hawk: each gets half the chance of winning, but also risks injury
- Hawk vs Dove: Hawk takes the resource
- Dove vs Hawk: Dove retreats
- Dove vs Dove: the resource is split, but time is lost in display

---

### 3. Expected payoffs

```python
def expected_payoffs(x_hawk: float, payoff_matrix: np.ndarray) -> tuple[float, float]:
    population = np.array([x_hawk, 1.0 - x_hawk], dtype=float)
    payoffs = payoff_matrix @ population
    return float(payoffs[0]), float(payoffs[1])
```

This function computes the expected payoff of each strategy, given the current hawk proportion `x_hawk`.

If the population state is

```python
[x_hawk, 1 - x_hawk]
```

then matrix multiplication gives the expected payoffs against the current population.

This is the key step that turns the game from a static payoff table into a population model.

---

### 4. Average population payoff

```python
def average_population_payoff(x_hawk: float, payoff_matrix: np.ndarray) -> float:
    population = np.array([x_hawk, 1.0 - x_hawk], dtype=float)
    payoffs = payoff_matrix @ population
    return float(population @ payoffs)
```

This computes the mean payoff currently achieved in the whole population.

Why this matters:

- if hawks do better than average, hawks should increase,
- if hawks do worse than average, hawks should decrease.

That logic is exactly what replicator dynamics formalizes.

---

### 5. Replicator update

```python
def replicator_step(x_hawk: float, payoff_matrix: np.ndarray, dt: float = 0.05) -> float:
    f_hawk, _ = expected_payoffs(x_hawk, payoff_matrix)
    f_bar = average_population_payoff(x_hawk, payoff_matrix)

    x_next = x_hawk + dt * x_hawk * (f_hawk - f_bar)
    x_next = min(max(x_next, 0.0), 1.0)
    return x_next
```

This is the evolutionary update rule.

The formula is:

```text
x' = x + dt * x * (f_H - f̄)
```

where:

- `x` is the current hawk proportion,
- `f_H` is the expected Hawk payoff,
- `f̄` is the average population payoff,
- `dt` is a small time step.

Interpretation:

- if Hawk is outperforming the population average, `x` rises,
- if Hawk is underperforming, `x` falls.

The clipping to `[0,1]` is only there to prevent numerical spillover.

---

### 6. Theoretical mixed equilibrium

```python
def theoretical_mixed_equilibrium(payoff_matrix: np.ndarray) -> float:
    a, b = payoff_matrix[0, 0], payoff_matrix[0, 1]
    c, d = payoff_matrix[1, 0], payoff_matrix[1, 1]

    denominator = a - b - c + d
    x_star = (d - b) / denominator
    return float(x_star)
```

For a two-strategy game, the interior equilibrium is found by setting:

```text
expected payoff of Hawk = expected payoff of Dove
```

That gives the hawk proportion `x_star` at which neither strategy has an advantage.

For this specific matrix, the result is:

```text
x_star = 7/12 ≈ 0.583333
```

This is the famous stable hawk frequency in Dawkins's example.

---

### 7. Simulation loop

```python
def simulate(x0: float, payoff_matrix: np.ndarray, n_steps: int = 400, dt: float = 0.05):
```

This function:

- starts from an initial hawk proportion `x0`,
- repeatedly applies the replicator step,
- stores time, hawk frequency, and payoffs,
- returns arrays for plotting.

This is where the dynamic behavior of the model appears.

---

### 8. Main function

The `main()` function is the entry point.

It:

- chooses an initial condition,
- computes the theoretical equilibrium,
- runs the simulation,
- prints key values,
- saves the figures.

The generated figures are typically:

- `figures/hawk_frequency.png`
- `figures/payoffs.png`

---

## What counts as a correct result

A correct implementation should show:

- all-dove is not stable,
- all-hawk is not stable,
- the system moves toward an interior equilibrium,
- the long-run hawk frequency approaches `7/12`.

A good debugging check is to start from several different initial conditions such as:

- `0.05`
- `0.20`
- `0.50`
- `0.80`
- `0.95`

All trajectories should move toward roughly the same equilibrium.

---

## Why this is the right first model

This version is intentionally minimal.

It avoids:

- finite-population noise,
- pairwise agent simulation,
- mutation,
- conditional strategies,
- spatial structure,
- retaliation and bullying strategies.

That is a strength, not a limitation. It gives a transparent baseline that can later be extended.

---

## Recommended next steps after this file

Once `hawk_dove_minimal.py` works, the natural extensions are:

1. **multi-start deterministic simulations** to show convergence from different initial states,
2. **agent-based simulation** with a finite number of individuals,
3. **stochastic update rules**,
4. **conditional strategies** such as Retaliator and Bully,
5. **parameter sweeps** for `V`, `C`, and `D`.

---

## Suggested README link

Add this line to the root `README.md`:

```md
See [`docs/hawk_dove_minimal_explanation.md`](docs/hawk_dove_minimal_explanation.md) for a detailed explanation of the first implementation.
```

---

## Suggested commit

```bash
git add docs/hawk_dove_minimal_explanation.md README.md
git commit -m "Add documentation for minimal Hawk-Dove model"
```
