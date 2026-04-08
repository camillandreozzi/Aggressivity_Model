
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.colors import ListedColormap

# ============================================================
# side_blotched_spatial.py
# Spatial local-interaction model on a toroidal grid:
#   - empty sites allowed
#   - local payoff from neighboring morphs
#   - stochastic colonization / death
#   - mutation at reproduction
#   - global frequency time series + spatial snapshots
#
# States:
#   -1 = empty
#    0 = orange
#    1 = blue
#    2 = yellow
# ============================================================

# -----------------------------
# PARAMETERS TO TOGGLE
# -----------------------------
RANDOM_SEED = 11
GRID_NX = 70
GRID_NY = 70
N_STEPS = 280

# Initial probabilities must sum to 1
P_INIT_EMPTY = 0.45
P_INIT_ORANGE = 0.22
P_INIT_BLUE = 0.18
P_INIT_YELLOW = 0.15

# Local game parameters
SELECTION_STRENGTH = 1.4
BASE_COLONIZATION = 0.22
BASE_DEATH = 0.06
LOCAL_CROWDING = 0.10      # extra mortality from local crowding
NEIGHBORHOOD = "moore"     # "moore" (8 neighbors) or "von_neumann" (4 neighbors)

# Mutation at birth
MUTATION_MATRIX = np.array([
    [0.985, 0.010, 0.005],
    [0.005, 0.985, 0.010],
    [0.010, 0.005, 0.985],
], dtype=float)

# Payoff matrix, order [orange, blue, yellow]
PAYOFF_MATRIX = np.array([
    [ 0.0,  1.0, -1.0],
    [-1.0,  0.0,  1.0],
    [ 1.0, -1.0,  0.0],
], dtype=float)

SAVE_FIGURE = True
FIGURE_PATH = "figures/side_blotched_spatial.png"
SHOW_PLOT = True

LABELS = ["Orange", "Blue", "Yellow"]
COLORS = ["orange", "royalblue", "gold"]


def validate_inputs():
    if not np.allclose(MUTATION_MATRIX.sum(axis=1), 1.0):
        raise ValueError("Each row of MUTATION_MATRIX must sum to 1.")
    if np.any(MUTATION_MATRIX < 0):
        raise ValueError("MUTATION_MATRIX cannot contain negative entries.")
    p_total = P_INIT_EMPTY + P_INIT_ORANGE + P_INIT_BLUE + P_INIT_YELLOW
    if not np.isclose(p_total, 1.0):
        raise ValueError("Initial probabilities must sum to 1.")
    if NEIGHBORHOOD not in {"moore", "von_neumann"}:
        raise ValueError("NEIGHBORHOOD must be 'moore' or 'von_neumann'.")


def get_neighbor_offsets():
    if NEIGHBORHOOD == "von_neumann":
        return [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]


OFFSETS = None


def initialize_grid(rng):
    probs = [P_INIT_EMPTY, P_INIT_ORANGE, P_INIT_BLUE, P_INIT_YELLOW]
    draws = rng.choice(4, size=(GRID_NX, GRID_NY), p=probs)
    # map 0->empty(-1), 1->orange(0), 2->blue(1), 3->yellow(2)
    grid = draws - 1
    return grid.astype(int)


def local_counts(grid, i, j):
    counts = np.zeros(3, dtype=int)
    occupied_neighbors = 0
    empty_neighbors = 0

    for di, dj in OFFSETS:
        ni = (i + di) % GRID_NX
        nj = (j + dj) % GRID_NY
        state = grid[ni, nj]
        if state == -1:
            empty_neighbors += 1
        else:
            counts[state] += 1
            occupied_neighbors += 1

    return counts, occupied_neighbors, empty_neighbors


def local_payoff(grid, i, j):
    state = grid[i, j]
    if state == -1:
        return 0.0

    counts, occupied_neighbors, _ = local_counts(grid, i, j)
    if occupied_neighbors == 0:
        return 0.0

    freqs = counts / occupied_neighbors
    payoff = PAYOFF_MATRIX @ freqs
    return float(payoff[state])


def update(grid, rng):
    new_grid = grid.copy()

    # Random sweep order
    sites = [(i, j) for i in range(GRID_NX) for j in range(GRID_NY)]
    rng.shuffle(sites)

    for i, j in sites:
        state = new_grid[i, j]

        if state == -1:
            # Empty site can be colonized by neighboring occupied sites
            candidates = []
            weights = []

            for di, dj in OFFSETS:
                ni = (i + di) % GRID_NX
                nj = (j + dj) % GRID_NY
                parent_state = new_grid[ni, nj]
                if parent_state != -1:
                    p = local_payoff(new_grid, ni, nj)
                    # Convert payoff into a positive colonization weight
                    weight = BASE_COLONIZATION * np.exp(SELECTION_STRENGTH * p)
                    candidates.append(parent_state)
                    weights.append(weight)

            if weights:
                weights = np.array(weights, dtype=float)
                total_weight = weights.sum()
                p_birth = 1.0 - np.exp(-total_weight)
                if rng.random() < p_birth:
                    probs = weights / total_weight
                    chosen_idx = rng.choice(len(candidates), p=probs)
                    parent_state = candidates[chosen_idx]
                    child_state = rng.choice(3, p=MUTATION_MATRIX[parent_state])
                    new_grid[i, j] = int(child_state)

        else:
            # Occupied site can die; death is higher if neighborhood is crowded
            _, occupied_neighbors, _ = local_counts(new_grid, i, j)
            local_density = occupied_neighbors / len(OFFSETS)
            payoff = local_payoff(new_grid, i, j)

            # Better local payoff lowers death slightly; crowding raises death
            death_prob = BASE_DEATH + LOCAL_CROWDING * local_density - 0.04 * payoff
            death_prob = np.clip(death_prob, 0.0, 1.0)

            if rng.random() < death_prob:
                new_grid[i, j] = -1

    return new_grid


def summarize_grid(grid):
    total_sites = grid.size
    occupied = np.count_nonzero(grid != -1)
    orange = np.count_nonzero(grid == 0)
    blue = np.count_nonzero(grid == 1)
    yellow = np.count_nonzero(grid == 2)
    empty = total_sites - occupied

    if occupied > 0:
        freqs_occ = np.array([orange, blue, yellow], dtype=float) / occupied
    else:
        freqs_occ = np.zeros(3, dtype=float)

    return {
        "occupied": occupied,
        "empty": empty,
        "orange": orange,
        "blue": blue,
        "yellow": yellow,
        "freqs_occ": freqs_occ,
        "occupancy": occupied / total_sites,
    }


def parameter_block():
    return (
        "Parameters\n"
        f"RANDOM_SEED = {RANDOM_SEED}\n"
        f"GRID = {GRID_NX} x {GRID_NY}\n"
        f"N_STEPS = {N_STEPS}\n"
        f"NEIGHBORHOOD = {NEIGHBORHOOD}\n\n"
        f"BASE_COLONIZATION = {BASE_COLONIZATION}\n"
        f"BASE_DEATH = {BASE_DEATH}\n"
        f"LOCAL_CROWDING = {LOCAL_CROWDING}\n"
        f"SELECTION_STRENGTH = {SELECTION_STRENGTH}\n\n"
        "Initial probabilities\n"
        f"  empty  = {P_INIT_EMPTY}\n"
        f"  orange = {P_INIT_ORANGE}\n"
        f"  blue   = {P_INIT_BLUE}\n"
        f"  yellow = {P_INIT_YELLOW}\n\n"
        "Morph order = [orange, blue, yellow]\n"
        "PAYOFF_MATRIX =\n"
        f"{np.array2string(PAYOFF_MATRIX, precision=3, suppress_small=True)}\n\n"
        "MUTATION_MATRIX =\n"
        f"{np.array2string(MUTATION_MATRIX, precision=3, suppress_small=True)}"
    )


def simulate():
    global OFFSETS
    OFFSETS = get_neighbor_offsets()
    rng = np.random.default_rng(RANDOM_SEED)

    grid = initialize_grid(rng)

    snapshots = {}
    snapshot_steps = [0, N_STEPS // 3, 2 * N_STEPS // 3, N_STEPS]

    occupied_series = np.zeros(N_STEPS + 1, dtype=float)
    orange_series = np.zeros(N_STEPS + 1, dtype=float)
    blue_series = np.zeros(N_STEPS + 1, dtype=float)
    yellow_series = np.zeros(N_STEPS + 1, dtype=float)
    occupancy_series = np.zeros(N_STEPS + 1, dtype=float)

    for step in range(N_STEPS + 1):
        if step in snapshot_steps:
            snapshots[step] = grid.copy()

        summary = summarize_grid(grid)
        occupied_series[step] = summary["occupied"]
        orange_series[step] = summary["orange"]
        blue_series[step] = summary["blue"]
        yellow_series[step] = summary["yellow"]
        occupancy_series[step] = summary["occupancy"]

        if step < N_STEPS:
            grid = update(grid, rng)

    counts = np.vstack([orange_series, blue_series, yellow_series]).T
    freqs_occ = np.divide(
        counts,
        occupied_series[:, None],
        out=np.zeros_like(counts),
        where=occupied_series[:, None] > 0
    )
    times = np.arange(N_STEPS + 1)

    return times, counts, occupied_series, occupancy_series, freqs_occ, snapshots


def print_summary(times, counts, occupied, occupancy, freqs_occ):
    print("=" * 70)
    print("SIDE-BLOTCHED LIZARD SPATIAL SIMULATION")
    print("=" * 70)
    print(parameter_block())
    print("\nFinal counts:")
    print(f"  Orange: {int(counts[-1, 0])}")
    print(f"  Blue:   {int(counts[-1, 1])}")
    print(f"  Yellow: {int(counts[-1, 2])}")
    print(f"  Occupied sites: {int(occupied[-1])}")
    print(f"  Occupancy fraction: {occupancy[-1]:.3f}")

    print("\nFinal frequencies among occupied sites:")
    print(f"  Orange: {freqs_occ[-1, 0]:.3f}")
    print(f"  Blue:   {freqs_occ[-1, 1]:.3f}")
    print(f"  Yellow: {freqs_occ[-1, 2]:.3f}")
    print("=" * 70)


def make_plot(times, counts, occupied, occupancy, freqs_occ, snapshots):
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.1], width_ratios=[1.0, 1.0, 1.15])

    ax_snap1 = fig.add_subplot(gs[0, 0])
    ax_snap2 = fig.add_subplot(gs[0, 1])
    ax_snap3 = fig.add_subplot(gs[0, 2])
    ax_time = fig.add_subplot(gs[1, 0:2])
    ax_occ = fig.add_subplot(gs[1, 2])

    cmap = ListedColormap(["white", "orange", "royalblue", "gold"])
    # remap states: empty=-1 -> 0, orange=0 -> 1, blue=1 -> 2, yellow=2 -> 3
    ordered_steps = sorted(snapshots.keys())
    show_steps = [ordered_steps[0], ordered_steps[1], ordered_steps[-1]]
    snap_axes = [ax_snap1, ax_snap2, ax_snap3]

    for ax, step in zip(snap_axes, show_steps):
        grid = snapshots[step]
        display_grid = grid + 1
        ax.imshow(display_grid, cmap=cmap, vmin=0, vmax=3, interpolation="nearest")
        ax.set_title(f"Spatial snapshot: step {step}")
        ax.set_xticks([])
        ax.set_yticks([])

    # Count time series
    ax_time.stackplot(
        times,
        counts[:, 0], counts[:, 1], counts[:, 2],
        colors=COLORS,
        alpha=0.80,
        labels=LABELS
    )
    ax_time.plot(times, occupied, color="black", linewidth=2.0, label="Occupied sites")
    ax_time.set_title("Global counts over time")
    ax_time.set_xlabel("Step")
    ax_time.set_ylabel("Count")
    ax_time.grid(alpha=0.25, linestyle="--")
    ax_time.legend(loc="upper left", frameon=True)

    # Occupancy and frequencies
    ax_occ.plot(times, occupancy, color="black", linewidth=2.0, label="Occupancy fraction")
    ax_occ.plot(times, freqs_occ[:, 0], color=COLORS[0], linewidth=2.0, label="Orange frequency")
    ax_occ.plot(times, freqs_occ[:, 1], color=COLORS[1], linewidth=2.0, label="Blue frequency")
    ax_occ.plot(times, freqs_occ[:, 2], color=COLORS[2], linewidth=2.0, label="Yellow frequency")
    ax_occ.set_title("Occupancy + frequencies among occupied sites")
    ax_occ.set_xlabel("Step")
    ax_occ.set_ylim(0, 1)
    ax_occ.grid(alpha=0.25, linestyle="--")
    ax_occ.legend(loc="upper right", frameon=True)

    fig.text(
        0.985, 0.5, parameter_block(),
        ha="right", va="center",
        fontsize=9.2, family="monospace",
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
    times, counts, occupied, occupancy, freqs_occ, snapshots = simulate()
    print_summary(times, counts, occupied, occupancy, freqs_occ)
    make_plot(times, counts, occupied, occupancy, freqs_occ, snapshots)


if __name__ == "__main__":
    main()
