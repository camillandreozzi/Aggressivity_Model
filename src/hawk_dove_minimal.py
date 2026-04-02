from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt


# -------------------------------------------------------------------------
# 1. Parameters from Chapter 5 of "The Selfish Gene" by Richard Dawkins
# -------------------------------------------------------------------------


V = 50    # value of winning
L = 0     # value of losing
C = 100   # cost of serious injury
D = 10    # cost of a long display / wasted time

# Payoff matrix:
# rows = focal player's strategy, cols = opponent's strategy
# order: Hawk, Dove
A = np.array([
    [(V - C) / 2, V],      # Hawk vs Hawk, Hawk vs Dove
    [L, (V / 2) - D]       # Dove vs Hawk, Dove vs Dove
], dtype=float)


def expected_payoffs(x_hawk: float, payoff_matrix: np.ndarray) -> tuple[float, float]:
    """
    Compute expected payoff of Hawk and Dove when the population
    has hawk proportion x_hawk and dove proportion 1 - x_hawk.
    """
    population = np.array([x_hawk, 1.0 - x_hawk], dtype=float)
    payoffs = payoff_matrix @ population
    return float(payoffs[0]), float(payoffs[1])


def average_population_payoff(x_hawk: float, payoff_matrix: np.ndarray) -> float:
    """
    Compute mean payoff in the current population.
    """
    population = np.array([x_hawk, 1.0 - x_hawk], dtype=float)
    payoffs = payoff_matrix @ population
    return float(population @ payoffs)


# -------------------------------------------------------------------------
# 2. Replicator dynamics and simulation
# -------------------------------------------------------------------------

def replicator_step(x_hawk: float, payoff_matrix: np.ndarray, dt: float = 0.05) -> float:
    """
    One discrete-time replicator update:
        x' = x + dt * x * (f_H - f_bar)
    """
    f_hawk, _ = expected_payoffs(x_hawk, payoff_matrix)
    f_bar = average_population_payoff(x_hawk, payoff_matrix)

    x_next = x_hawk + dt * x_hawk * (f_hawk - f_bar)

    # keep numerical errors from taking us outside [0, 1]
    x_next = min(max(x_next, 0.0), 1.0)
    return x_next

# -------------------------------------------------------------------------
# 3. Simulation and plotting
# -------------------------------------------------------------------------

def theoretical_mixed_equilibrium(payoff_matrix: np.ndarray) -> float:
    """
    For a 2x2 matrix [[a,b],[c,d]], solve:
        x*a + (1-x)*b = x*c + (1-x)*d
    """
    a, b = payoff_matrix[0, 0], payoff_matrix[0, 1]
    c, d = payoff_matrix[1, 0], payoff_matrix[1, 1]

    denominator = a - b - c + d
    if np.isclose(denominator, 0.0):
        raise ValueError("No unique interior equilibrium for this payoff matrix.")

    x_star = (d - b) / denominator
    return float(x_star)


def simulate(
    x0: float,
    payoff_matrix: np.ndarray,
    n_steps: int = 400,
    dt: float = 0.05
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate hawk frequency through time.
    Returns arrays for:
        time, hawk frequency, hawk payoff, dove payoff
    """
    times = np.arange(n_steps + 1)
    hawk_freq = np.zeros(n_steps + 1)
    hawk_payoff = np.zeros(n_steps + 1)
    dove_payoff = np.zeros(n_steps + 1)

    x = x0
    hawk_freq[0] = x
    hawk_payoff[0], dove_payoff[0] = expected_payoffs(x, payoff_matrix)

    for t in range(1, n_steps + 1):
        x = replicator_step(x, payoff_matrix, dt=dt)
        hawk_freq[t] = x
        hawk_payoff[t], dove_payoff[t] = expected_payoffs(x, payoff_matrix)

    return times, hawk_freq, hawk_payoff, dove_payoff


def main() -> None:
    x0 = 0.99  # initial hawk proportion
    n_steps = 400
    dt = 0.05

    x_star = theoretical_mixed_equilibrium(A)
    times, hawk_freq, hawk_payoff, dove_payoff = simulate(x0, A, n_steps=n_steps, dt=dt)

    print("Payoff matrix:")
    print(A)
    print()
    print(f"Theoretical mixed equilibrium hawk frequency: {x_star:.6f}")
    print(f"Final simulated hawk frequency:              {hawk_freq[-1]:.6f}")

    # Plot hawk frequency
    plt.figure(figsize=(8, 5))
    plt.plot(times, hawk_freq, label="Hawk frequency")
    plt.axhline(x_star, linestyle="--", label=f"Theoretical equilibrium = {x_star:.4f}")
    plt.xlabel("Time step")
    plt.ylabel("Proportion of hawks")
    plt.title("Hawk–Dove replicator dynamics")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/hawk_frequency.png", dpi=200)
    plt.close()

    # Plot expected payoffs
    plt.figure(figsize=(8, 5))
    plt.plot(times, hawk_payoff, label="Expected Hawk payoff")
    plt.plot(times, dove_payoff, label="Expected Dove payoff")
    plt.xlabel("Time step")
    plt.ylabel("Expected payoff")
    plt.title("Expected payoffs through time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/payoffs.png", dpi=200)
    plt.close()


if __name__ == "__main__":
    main()