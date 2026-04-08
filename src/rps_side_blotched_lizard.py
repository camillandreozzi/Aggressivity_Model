import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# PARAMETERS TO TOGGLE
# ============================================================
T_MAX = 250.0          # total simulation time
DT = 0.05              # time step (smaller = smoother, slower)

# Demography
BASE_GROWTH = 0.35     # baseline per-capita growth shared by all morphs
CROWDING = 0.0025      # density dependence; lower = larger total population

# Game dynamics
SELECTION_STRENGTH = 1.20  # how strongly the RPS interaction affects growth

# Initial absolute population sizes: [orange, blue, yellow]
INITIAL_POPULATIONS = np.array([45.0, 30.0, 20.0], dtype=float)

# Stylized side-blotched lizard cyclic dominance:
# orange beats blue, blue beats yellow, yellow beats orange
# Rows = focal morph, columns = opponent morph
# Order: [orange, blue, yellow]
PAYOFF_MATRIX = np.array([
 [0,  1, -1],
 [-1, 0,  1],
 [1, -1,  0]
], dtype=float)

# Plot / output
SAVE_FIGURE = True
FIGURE_PATH = "figures/rps_side_blotched_lizard_timeseries.png"
SHOW_PLOT = True

# Colors and labels
LABELS = [
    "Orange (aggressive)",
    "Blue (mate-guarding)",
    "Yellow (sneaker)",
]
COLORS = ["orange", "royalblue", "gold"]

# ============================================================
# MODEL
# ============================================================
# We simulate absolute populations N_i(t), not just frequencies.
#
# Let x_i = N_i / N_total be the current frequency of each morph.
# The per-capita growth of morph i is:
#
#   growth_i = BASE_GROWTH
#              + SELECTION_STRENGTH * (PAYOFF_MATRIX @ x)_i
#              - CROWDING * N_total
#
# Therefore:
#
#   dN_i/dt = N_i * growth_i
#
# This gives:
# - cyclic RPS selection through the payoff term
# - total population expansion / saturation through density dependence
# ============================================================

def simulate():
    n_steps = int(T_MAX / DT) + 1
    t = np.linspace(0.0, T_MAX, n_steps)

    N = np.zeros((n_steps, 3), dtype=float)
    N[0] = INITIAL_POPULATIONS

    eps = 1e-12

    for k in range(n_steps - 1):
        total = max(N[k].sum(), eps)
        freqs = N[k] / total

        # Frequency-dependent payoff
        game_payoff = PAYOFF_MATRIX @ freqs

        # Per-capita growth for each morph
        growth = BASE_GROWTH + SELECTION_STRENGTH * game_payoff - CROWDING * total

        # Euler step
        dN = N[k] * growth
        N[k + 1] = np.maximum(N[k] + DT * dN, 0.0)

    totals = N.sum(axis=1)
    freqs = N / np.maximum(totals[:, None], eps)

    return t, N, totals, freqs


def parameter_block():
    approx_K = BASE_GROWTH / CROWDING if CROWDING > 0 else np.inf
    matrix_str = np.array2string(PAYOFF_MATRIX, precision=2, suppress_small=True)

    text = (
        "Parameters\n"
        f"T_MAX = {T_MAX}\n"
        f"DT = {DT}\n"
        f"BASE_GROWTH = {BASE_GROWTH}\n"
        f"CROWDING = {CROWDING}\n"
        f"Approx. carrying capacity ≈ {approx_K:.1f}\n"
        f"SELECTION_STRENGTH = {SELECTION_STRENGTH}\n"
        f"INITIAL_POPULATIONS = {INITIAL_POPULATIONS.tolist()}\n\n"
        "Morph order = [orange, blue, yellow]\n"
        "Payoff matrix:\n"
        f"{matrix_str}"
    )
    return text


def print_summary(t, N, totals, freqs):
    print("=" * 60)
    print("SIDE-BLOTCHED LIZARD RPS SIMULATION")
    print("=" * 60)
    print(parameter_block())
    print("\nFinal populations:")
    print(f"  Orange: {N[-1, 0]:.3f}")
    print(f"  Blue:   {N[-1, 1]:.3f}")
    print(f"  Yellow: {N[-1, 2]:.3f}")
    print(f"  Total:  {totals[-1]:.3f}")
    print("\nFinal frequencies:")
    print(f"  Orange: {freqs[-1, 0]:.3f}")
    print(f"  Blue:   {freqs[-1, 1]:.3f}")
    print(f"  Yellow: {freqs[-1, 2]:.3f}")
    print("=" * 60)


def make_plot(t, N, totals, freqs):
    fig, axes = plt.subplots(
        2, 1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.2]}
    )

    ax1, ax2 = axes

    # Top panel: absolute population sizes
    ax1.stackplot(
        t,
        N[:, 0], N[:, 1], N[:, 2],
        colors=COLORS,
        labels=LABELS,
        alpha=0.80
    )
    ax1.plot(t, totals, color="black", linewidth=2.4, label="Total population")

    ax1.set_title("Rock–Paper–Scissors side-blotched lizard simulation", fontsize=15)
    ax1.set_ylabel("Absolute population size")
    ax1.grid(alpha=0.25, linestyle="--")
    ax1.legend(loc="upper left", frameon=True)

    # Bottom panel: frequencies
    ax2.plot(t, freqs[:, 0], color=COLORS[0], linewidth=2.5, label=LABELS[0])
    ax2.plot(t, freqs[:, 1], color=COLORS[1], linewidth=2.5, label=LABELS[1])
    ax2.plot(t, freqs[:, 2], color=COLORS[2], linewidth=2.5, label=LABELS[2])

    ax2.set_ylim(0, 1)
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Frequency")
    ax2.grid(alpha=0.25, linestyle="--")

    # Parameter box on the right
    fig.text(
        0.985, 0.5, parameter_block(),
        ha="right", va="center",
        fontsize=9.5,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.95)
    )

    plt.tight_layout(rect=[0.0, 0.0, 0.82, 1.0])

    if SAVE_FIGURE:
        out_path = Path(FIGURE_PATH)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=220, bbox_inches="tight")
        print(f"\nFigure saved to: {out_path}")

    if SHOW_PLOT:
        plt.show()
    else:
        plt.close(fig)


def main():
    t, N, totals, freqs = simulate()
    print_summary(t, N, totals, freqs)
    make_plot(t, N, totals, freqs)


if __name__ == "__main__":
    main()