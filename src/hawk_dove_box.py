from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# =====================================
# Parameters
# =====================================
N = 120
BOX_SIZE = 1.0
INITIAL_HAWK_FRACTION = 0.95

V = 50      # value of resource
C = 100     # cost of injury
D = 10      # cost of display / wasted time

ROUNDS_PER_FRAME = 1
UPDATES_PER_FRAME = 5
MUTATION_RATE = 0.01
SEED = 42


rng = np.random.default_rng(SEED)


# =====================================
# Agent state
# strategy: 1 = Hawk, 0 = Dove
# =====================================
positions = rng.uniform(0, BOX_SIZE, size=(N, 2))
strategies = (rng.random(N) < INITIAL_HAWK_FRACTION).astype(int)
payoffs = np.zeros(N, dtype=float)


def pairwise_payoff(s1: int, s2: int) -> tuple[float, float]:
    """
    Returns payoff for player 1 and player 2.
    1 = Hawk, 0 = Dove
    """
    if s1 == 1 and s2 == 1:
        # Hawk vs Hawk
        return (V - C) / 2, (V - C) / 2
    elif s1 == 1 and s2 == 0:
        # Hawk vs Dove
        return V, 0.0
    elif s1 == 0 and s2 == 1:
        # Dove vs Hawk
        return 0.0, V
    else:
        # Dove vs Dove
        return V / 2 - D, V / 2 - D


def run_encounters() -> None:
    """
    Randomly pair agents and accumulate payoffs.
    """
    global payoffs
    payoffs[:] = 0.0

    for _ in range(ROUNDS_PER_FRAME):
        order = rng.permutation(N)

        for i in range(0, N - 1, 2):
            a = order[i]
            b = order[i + 1]

            p_a, p_b = pairwise_payoff(strategies[a], strategies[b])
            payoffs[a] += p_a
            payoffs[b] += p_b


def evolutionary_update() -> None:
    """
    Agents may copy better-performing agents.
    """
    global strategies

    for _ in range(UPDATES_PER_FRAME):
        i, j = rng.choice(N, size=2, replace=False)

        # Fermi imitation rule: higher-payoff agents are more likely to be copied
        beta = 0.1
        prob_copy_j = 1.0 / (1.0 + np.exp(-beta * (payoffs[j] - payoffs[i])))

        if rng.random() < prob_copy_j:
            strategies[i] = strategies[j]

        # small mutation / experimentation
        if rng.random() < MUTATION_RATE:
            strategies[i] = 1 - strategies[i]


def jitter_positions(scale: float = 0.01) -> None:
    """
    Small random motion so the box looks alive.
    """
    global positions
    positions += rng.normal(0.0, scale, size=positions.shape)
    positions = np.clip(positions, 0.0, BOX_SIZE)


# =====================================
# Plot setup
# =====================================
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(0, BOX_SIZE)
ax.set_ylim(0, BOX_SIZE)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Hawk–Dove evolution in a box")

colors = np.where(strategies == 1, "red", "blue")
scatter = ax.scatter(positions[:, 0], positions[:, 1], c=colors, s=60, alpha=0.8)

text = ax.text(
    0.02, 1.02, "", transform=ax.transAxes, fontsize=11, verticalalignment="bottom"
)


def update(frame: int):
    run_encounters()
    evolutionary_update()
    jitter_positions()

    colors = np.where(strategies == 1, "red", "blue")
    scatter.set_offsets(positions)
    scatter.set_color(colors)

    hawks = np.sum(strategies == 1)
    doves = np.sum(strategies == 0)
    mean_payoff = np.mean(payoffs)

    text.set_text(
        f"frame={frame}   hawks={hawks}   doves={doves}   mean payoff={mean_payoff:.2f}"
    )

    return scatter, text


anim = FuncAnimation(fig, update, frames=300, interval=120, blit=False)

plt.tight_layout()
plt.show()