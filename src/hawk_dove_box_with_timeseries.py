from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# ============================================================
# Parameters
# ============================================================
N = 120
BOX_SIZE = 1.0
INITIAL_HAWK_FRACTION = 0.95

# Dawkins-style payoff parameters
V = 50.0   # value of resource
C = 100.0  # cost of injury
D = 10.0   # cost of display / wasted time

# Simulation controls
FRAMES = 1000
ROUNDS_PER_FRAME = 1
UPDATES_PER_FRAME = 5
MUTATION_RATE = 0.01
BETA = 0.10          # intensity of selection in imitation step
JITTER_SCALE = 0.01  # purely visual motion
SEED = 42


# ============================================================
# Helpers
# ============================================================
def theoretical_hawk_equilibrium(v: float, c: float, d: float) -> float | None:
    """
    For the Hawk-Dove payoff matrix:
        H vs H = (V - C)/2
        H vs D = V
        D vs H = 0
        D vs D = V/2 - D
    solve for the interior equilibrium x* where Hawk and Dove
    have equal expected payoff.
    """
    a = (v - c) / 2.0
    b = v
    c_ = 0.0
    d_ = v / 2.0 - d

    denom = a - b - c_ + d_
    if np.isclose(denom, 0.0):
        return None

    x_star = (d_ - b) / denom
    if 0.0 <= x_star <= 1.0:
        return x_star
    return None


def pairwise_payoff(s1: int, s2: int) -> tuple[float, float]:
    """
    Strategy encoding:
        1 = Hawk
        0 = Dove
    """
    if s1 == 1 and s2 == 1:
        # Hawk vs Hawk
        payoff = (V - C) / 2.0
        return payoff, payoff
    if s1 == 1 and s2 == 0:
        # Hawk vs Dove
        return V, 0.0
    if s1 == 0 and s2 == 1:
        # Dove vs Hawk
        return 0.0, V

    # Dove vs Dove
    payoff = V / 2.0 - D
    return payoff, payoff


# ============================================================
# Main simulation
# ============================================================
def main() -> None:
    rng = np.random.default_rng(SEED)

    # Agent state
    positions = rng.uniform(0.0, BOX_SIZE, size=(N, 2))
    strategies = (rng.random(N) < INITIAL_HAWK_FRACTION).astype(int)
    payoffs = np.zeros(N, dtype=float)

    hawk_history: list[float] = [float(np.mean(strategies))]
    mean_payoff_history: list[float] = [0.0]

    x_star = theoretical_hawk_equilibrium(V, C, D)

    def run_encounters() -> None:
        nonlocal payoffs
        payoffs[:] = 0.0

        for _ in range(ROUNDS_PER_FRAME):
            order = rng.permutation(N)

            # Pair consecutive agents after shuffling
            for k in range(0, N - 1, 2):
                i = order[k]
                j = order[k + 1]

                p_i, p_j = pairwise_payoff(strategies[i], strategies[j])
                payoffs[i] += p_i
                payoffs[j] += p_j

    def evolutionary_update() -> None:
        nonlocal strategies

        for _ in range(UPDATES_PER_FRAME):
            i, j = rng.choice(N, size=2, replace=False)

            # Fermi imitation rule:
            # agent i copies j with probability increasing in payoff difference
            prob_copy_j = 1.0 / (1.0 + np.exp(-BETA * (payoffs[j] - payoffs[i])))

            if rng.random() < prob_copy_j:
                strategies[i] = strategies[j]

            # Small mutation / experimentation
            if rng.random() < MUTATION_RATE:
                strategies[i] = 1 - strategies[i]

    def jitter_positions() -> None:
        nonlocal positions
        positions += rng.normal(0.0, JITTER_SCALE, size=positions.shape)
        positions = np.clip(positions, 0.0, BOX_SIZE)

    # ========================================================
    # Plot setup
    # ========================================================
    fig, (ax_box, ax_ts) = plt.subplots(
        1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [1.1, 1.2]}
    )

    # Left panel: box with agents
    ax_box.set_xlim(0.0, BOX_SIZE)
    ax_box.set_ylim(0.0, BOX_SIZE)
    ax_box.set_xticks([])
    ax_box.set_yticks([])
    ax_box.set_title("Hawks and doves in a box")

    initial_colors = np.where(strategies == 1, "red", "blue")
    scatter = ax_box.scatter(
        positions[:, 0],
        positions[:, 1],
        c=initial_colors,
        s=60,
        alpha=0.80,
        edgecolors="black",
        linewidths=0.3,
    )

    stats_text = ax_box.text(
        0.02,
        1.02,
        "",
        transform=ax_box.transAxes,
        fontsize=10,
        va="bottom",
    )

    # Right panel: hawk frequency through time
    ax_ts.set_xlim(0, FRAMES)
    ax_ts.set_ylim(0.0, 1.0)
    ax_ts.set_xlabel("Frame")
    ax_ts.set_ylabel("Hawk proportion")
    ax_ts.set_title("Live hawk proportion")

    if x_star is not None:
        ax_ts.axhline(
            x_star,
            linestyle="--",
            linewidth=1.5,
            color="gray",
            label=f"Theoretical equilibrium = {x_star:.3f}",
        )

    hawk_line, = ax_ts.plot([], [], linewidth=2.0, label="Observed hawk proportion")
    mean_payoff_line, = ax_ts.plot(
        [], [], linewidth=1.5, linestyle=":", label="Scaled mean payoff"
    )

    ax_ts.legend(loc="upper right")

    def init():
        hawk_line.set_data([], [])
        mean_payoff_line.set_data([], [])
        return scatter, hawk_line, mean_payoff_line, stats_text

    def update(frame: int):
        run_encounters()
        evolutionary_update()
        jitter_positions()

        hawk_fraction = float(np.mean(strategies))
        mean_payoff = float(np.mean(payoffs))

        hawk_history.append(hawk_fraction)
        mean_payoff_history.append(mean_payoff)

        # Update scatter
        colors = np.where(strategies == 1, "red", "blue")
        scatter.set_offsets(positions)
        scatter.set_color(colors)

        hawks = int(np.sum(strategies == 1))
        doves = int(np.sum(strategies == 0))
        stats_text.set_text(
            f"frame={frame:03d}   hawks={hawks}   doves={doves}   mean payoff={mean_payoff:.2f}"
        )

        # Update time series
        x_vals = np.arange(len(hawk_history))
        hawk_line.set_data(x_vals, hawk_history)

        # Scale mean payoff into [0,1] just to show it on same axis
        payoff_arr = np.array(mean_payoff_history)
        if np.max(payoff_arr) > np.min(payoff_arr):
            scaled_payoff = (payoff_arr - np.min(payoff_arr)) / (
                np.max(payoff_arr) - np.min(payoff_arr)
            )
        else:
            scaled_payoff = np.zeros_like(payoff_arr)

        mean_payoff_line.set_data(x_vals, scaled_payoff)

        return scatter, hawk_line, mean_payoff_line, stats_text

    anim = FuncAnimation(
        fig,
        update,
        frames=FRAMES,
        init_func=init,
        interval=120,
        blit=False,
        repeat=False,
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()