
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import Polygon

# ============================================================
# side_blotched_advanced.py
# Advanced well-mixed model:
#   - stochastic births / deaths
#   - mutation matrix
#   - absolute population expansion
#   - frequency time series
#   - simplex trajectory
#
# Morph order: [orange, blue, yellow]
# ============================================================

# -----------------------------
# PARAMETERS TO TOGGLE
# -----------------------------
RANDOM_SEED = 7

T_MAX = 220.0
DT = 0.2

# Demography
BASE_BIRTH = 0.72
BASE_DEATH = 0.28
CROWDING = 0.0045   # larger = smaller total population

# Game / selection
SELECTION_STRENGTH = 1.35
PAYOFF_MATRIX = np.array([
    [ 0.0,  1.0, -1.0],   # orange beats blue, loses to yellow
    [-1.0,  0.0,  1.0],   # blue beats yellow, loses to orange
    [ 1.0, -1.0,  0.0],   # yellow beats orange, loses to blue
], dtype=float)

# Mutation matrix Q:
# Q[i, j] = probability that parent morph i produces offspring morph j
# each row must sum to 1
MUTATION_MATRIX = np.array([
    [0.985, 0.010, 0.005],
    [0.005, 0.985, 0.010],
    [0.010, 0.005, 0.985],
], dtype=float)

# Initial integer counts
INITIAL_COUNTS = np.array([55, 35, 20], dtype=int)

# Output
SAVE_FIGURE = True
FIGURE_PATH = "figures/side_blotched_advanced.png"
SHOW_PLOT = True

LABELS = [
    "Orange (aggressive)",
    "Blue (mate-guarding)",
    "Yellow (sneaker)",
]
COLORS = ["orange", "royalblue", "gold"]
EPS = 1e-12


def validate_inputs():
    if np.any(INITIAL_COUNTS < 0):
        raise ValueError("INITIAL_COUNTS must be non-negative.")
    if not np.allclose(MUTATION_MATRIX.sum(axis=1), 1.0):
        raise ValueError("Each row of MUTATION_MATRIX must sum to 1.")
    if np.any(MUTATION_MATRIX < 0):
        raise ValueError("MUTATION_MATRIX cannot contain negative entries.")
    if DT <= 0 or T_MAX <= 0:
        raise ValueError("DT and T_MAX must be positive.")


def softplus(x: np.ndarray) -> np.ndarray:
    """Stable positive mapping."""
    return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0.0)


def simulate():
    rng = np.random.default_rng(RANDOM_SEED)
    n_steps = int(T_MAX / DT) + 1
    t = np.linspace(0.0, T_MAX, n_steps)

    counts = np.zeros((n_steps, 3), dtype=int)
    counts[0] = INITIAL_COUNTS

    for k in range(n_steps - 1):
        current = counts[k].astype(int)
        total = current.sum()

        if total == 0:
            counts[k + 1] = current
            continue

        freqs = current / total
        payoff = PAYOFF_MATRIX @ freqs

        # Positive per-capita birth rates shaped by strategic success
        birth_rates = BASE_BIRTH * np.exp(SELECTION_STRENGTH * payoff)

        # Death rates increase with total population (density dependence)
        death_rates = BASE_DEATH + CROWDING * total

        # Tau-leap births / deaths
        expected_births = current * birth_rates * DT
        births_by_parent = rng.poisson(expected_births)

        expected_deaths = current * death_rates * DT
        deaths = rng.poisson(expected_deaths)
        deaths = np.minimum(deaths, current)

        # Offspring mutate at birth according to MUTATION_MATRIX
        offspring = np.zeros(3, dtype=int)
        for i in range(3):
            n_births = int(births_by_parent[i])
            if n_births > 0:
                offspring += rng.multinomial(n_births, MUTATION_MATRIX[i])

        next_counts = current - deaths + offspring
        next_counts = np.maximum(next_counts, 0)
        counts[k + 1] = next_counts.astype(int)

    totals = counts.sum(axis=1).astype(float)
    freqs = np.divide(counts, totals[:, None], out=np.zeros_like(counts, dtype=float), where=totals[:, None] > 0)
    return t, counts.astype(float), totals, freqs


def barycentric_to_cartesian(freqs: np.ndarray) -> np.ndarray:
    """
    Map frequencies [orange, blue, yellow] to a 2D simplex triangle.
    Vertices:
      Orange -> (0, 0)
      Blue   -> (1, 0)
      Yellow -> (0.5, sqrt(3)/2)
    """
    v_orange = np.array([0.0, 0.0])
    v_blue = np.array([1.0, 0.0])
    v_yellow = np.array([0.5, np.sqrt(3) / 2.0])

    pts = (
        freqs[:, [0]] * v_orange
        + freqs[:, [1]] * v_blue
        + freqs[:, [2]] * v_yellow
    )
    return pts


def parameter_block() -> str:
    approx_k = (BASE_BIRTH - BASE_DEATH) / CROWDING if CROWDING > 0 else np.inf
    return (
        "Parameters\n"
        f"RANDOM_SEED = {RANDOM_SEED}\n"
        f"T_MAX = {T_MAX}\n"
        f"DT = {DT}\n\n"
        f"BASE_BIRTH = {BASE_BIRTH}\n"
        f"BASE_DEATH = {BASE_DEATH}\n"
        f"CROWDING = {CROWDING}\n"
        f"Approx. carrying capacity ≈ {approx_k:.1f}\n\n"
        f"SELECTION_STRENGTH = {SELECTION_STRENGTH}\n"
        f"INITIAL_COUNTS = {INITIAL_COUNTS.tolist()}\n\n"
        "Morph order = [orange, blue, yellow]\n"
        "PAYOFF_MATRIX =\n"
        f"{np.array2string(PAYOFF_MATRIX, precision=3, suppress_small=True)}\n\n"
        "MUTATION_MATRIX =\n"
        f"{np.array2string(MUTATION_MATRIX, precision=3, suppress_small=True)}"
    )


def print_summary(t, counts, totals, freqs):
    print("=" * 70)
    print("SIDE-BLOTCHED LIZARD ADVANCED SIMULATION")
    print("=" * 70)
    print(parameter_block())
    print("\nFinal absolute counts:")
    print(f"  Orange: {int(counts[-1, 0])}")
    print(f"  Blue:   {int(counts[-1, 1])}")
    print(f"  Yellow: {int(counts[-1, 2])}")
    print(f"  Total:  {int(totals[-1])}")

    print("\nFinal frequencies:")
    print(f"  Orange: {freqs[-1, 0]:.3f}")
    print(f"  Blue:   {freqs[-1, 1]:.3f}")
    print(f"  Yellow: {freqs[-1, 2]:.3f}")
    print("=" * 70)


def make_plot(t, counts, totals, freqs):
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.4, 1.0], height_ratios=[1.15, 1.0])

    ax_counts = fig.add_subplot(gs[0, 0])
    ax_freqs = fig.add_subplot(gs[1, 0], sharex=ax_counts)
    ax_simplex = fig.add_subplot(gs[:, 1])

    # Absolute populations
    ax_counts.stackplot(
        t,
        counts[:, 0], counts[:, 1], counts[:, 2],
        colors=COLORS,
        alpha=0.80,
        labels=LABELS
    )
    ax_counts.plot(t, totals, color="black", linewidth=2.0, label="Total population")
    ax_counts.set_title("Advanced side-blotched lizard simulation", fontsize=15)
    ax_counts.set_ylabel("Absolute population size")
    ax_counts.grid(alpha=0.25, linestyle="--")
    ax_counts.legend(loc="upper left", frameon=True)

    # Frequencies
    for i in range(3):
        ax_freqs.plot(t, freqs[:, i], color=COLORS[i], linewidth=2.2, label=LABELS[i])
    ax_freqs.set_ylim(0, 1)
    ax_freqs.set_ylabel("Frequency")
    ax_freqs.set_xlabel("Time")
    ax_freqs.grid(alpha=0.25, linestyle="--")

    # Simplex plot
    triangle = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, np.sqrt(3) / 2.0],
    ])
    ax_simplex.add_patch(Polygon(triangle, closed=True, fill=False, linewidth=2.0, edgecolor="black"))

    pts = barycentric_to_cartesian(freqs)
    ax_simplex.plot(pts[:, 0], pts[:, 1], color="black", linewidth=1.5, alpha=0.9)
    ax_simplex.scatter(pts[0, 0], pts[0, 1], color="green", s=70, zorder=3, label="Start")
    ax_simplex.scatter(pts[-1, 0], pts[-1, 1], color="red", s=70, zorder=3, label="End")

    # A few time markers
    n_markers = 8
    idx = np.linspace(0, len(pts) - 1, n_markers, dtype=int)
    ax_simplex.scatter(pts[idx, 0], pts[idx, 1], c=np.linspace(0, 1, n_markers), cmap="viridis", s=30, zorder=3)

    ax_simplex.text(-0.04, -0.04, "Orange", color="darkorange", fontsize=12, ha="right")
    ax_simplex.text(1.04, -0.04, "Blue", color="royalblue", fontsize=12, ha="left")
    ax_simplex.text(0.50, np.sqrt(3) / 2.0 + 0.05, "Yellow", color="goldenrod", fontsize=12, ha="center")
    ax_simplex.set_title("Simplex trajectory (frequencies)", fontsize=14)
    ax_simplex.set_xlim(-0.08, 1.08)
    ax_simplex.set_ylim(-0.08, np.sqrt(3) / 2.0 + 0.10)
    ax_simplex.set_aspect("equal")
    ax_simplex.axis("off")
    ax_simplex.legend(loc="upper right", frameon=True)

    fig.text(
        0.985, 0.50, parameter_block(),
        ha="right", va="center",
        fontsize=9.5, family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.97)
    )

    plt.tight_layout(rect=[0.0, 0.0, 0.83, 1.0])

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
    validate_inputs()
    t, counts, totals, freqs = simulate()
    print_summary(t, counts, totals, freqs)
    make_plot(t, counts, totals, freqs)


if __name__ == "__main__":
    main()
