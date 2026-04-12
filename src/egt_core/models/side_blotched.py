from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from egt_core.base import ModelSpec


LABELS = [
    "Orange (aggressive)",
    "Blue (mate-guarding)",
    "Yellow (sneaker)",
]
COLORS = ["orange", "royalblue", "gold"]


def barycentric_to_cartesian(freqs: np.ndarray) -> np.ndarray:
    v_orange = np.array([0.0, 0.0])
    v_blue = np.array([1.0, 0.0])
    v_yellow = np.array([0.5, np.sqrt(3) / 2.0])
    return (
        freqs[:, [0]] * v_orange
        + freqs[:, [1]] * v_blue
        + freqs[:, [2]] * v_yellow
    )


def render_controls(ui: Any) -> dict[str, Any]:
    ui.subheader("Time scale")
    t_max = ui.slider("T max", 20.0, 600.0, 220.0, 10.0)
    dt = ui.slider("Delta t", 0.05, 1.0, 0.20, 0.05)
    seed = ui.number_input("Random seed", min_value=0, max_value=1_000_000, value=7, step=1)

    ui.subheader("Demography")
    base_birth = ui.slider("Base birth", 0.05, 2.0, 0.72, 0.01)
    base_death = ui.slider("Base death", 0.01, 2.0, 0.28, 0.01)
    crowding = ui.slider("Crowding", 0.0001, 0.02, 0.0045, 0.0001, format="%.4f")
    selection_strength = ui.slider("Selection strength", 0.0, 3.0, 1.35, 0.05)

    ui.subheader("Initial counts")
    orange = ui.slider("Orange", 0, 500, 55, 1)
    blue = ui.slider("Blue", 0, 500, 35, 1)
    yellow = ui.slider("Yellow", 0, 500, 20, 1)

    with ui.expander("Payoff matrix"):
        o_b = ui.number_input("Orange vs Blue", value=1.0, step=0.1)
        o_y = ui.number_input("Orange vs Yellow", value=-1.0, step=0.1)
        b_o = ui.number_input("Blue vs Orange", value=-1.0, step=0.1)
        b_y = ui.number_input("Blue vs Yellow", value=1.0, step=0.1)
        y_o = ui.number_input("Yellow vs Orange", value=1.0, step=0.1)
        y_b = ui.number_input("Yellow vs Blue", value=-1.0, step=0.1)

    with ui.expander("Mutation matrix"):
        q_ob = ui.slider("Orange -> Blue", 0.0, 0.2, 0.010, 0.001)
        q_oy = ui.slider("Orange -> Yellow", 0.0, 0.2, 0.005, 0.001)
        q_bo = ui.slider("Blue -> Orange", 0.0, 0.2, 0.005, 0.001)
        q_by = ui.slider("Blue -> Yellow", 0.0, 0.2, 0.010, 0.001)
        q_yo = ui.slider("Yellow -> Orange", 0.0, 0.2, 0.010, 0.001)
        q_yb = ui.slider("Yellow -> Blue", 0.0, 0.2, 0.005, 0.001)

    mutation_matrix = np.array(
        [
            [1.0 - q_ob - q_oy, q_ob, q_oy],
            [q_bo, 1.0 - q_bo - q_by, q_by],
            [q_yo, q_yb, 1.0 - q_yo - q_yb],
        ],
        dtype=float,
    )

    if np.any(mutation_matrix < 0.0):
        ui.error("Mutation rows must sum to at most 1. Reduce the off-diagonal mutation values.")

    payoff_matrix = np.array(
        [
            [0.0, o_b, o_y],
            [b_o, 0.0, b_y],
            [y_o, y_b, 0.0],
        ],
        dtype=float,
    )

    return {
        "random_seed": int(seed),
        "t_max": float(t_max),
        "dt": float(dt),
        "base_birth": float(base_birth),
        "base_death": float(base_death),
        "crowding": float(crowding),
        "selection_strength": float(selection_strength),
        "initial_counts": [int(orange), int(blue), int(yellow)],
        "payoff_matrix": payoff_matrix.tolist(),
        "mutation_matrix": mutation_matrix.tolist(),
    }


def run(config: dict[str, Any]) -> dict[str, Any]:
    initial_counts = np.array(config["initial_counts"], dtype=int)
    mutation_matrix = np.array(config["mutation_matrix"], dtype=float)
    payoff_matrix = np.array(config["payoff_matrix"], dtype=float)

    if np.any(initial_counts < 0):
        raise ValueError("Initial counts must be non-negative.")
    if not np.allclose(mutation_matrix.sum(axis=1), 1.0):
        raise ValueError("Each row of mutation_matrix must sum to 1.")
    if np.any(mutation_matrix < 0):
        raise ValueError("Mutation probabilities cannot be negative.")

    rng = np.random.default_rng(config["random_seed"])
    n_steps = int(config["t_max"] / config["dt"]) + 1
    t = np.linspace(0.0, config["t_max"], n_steps)
    counts = np.zeros((n_steps, 3), dtype=int)
    counts[0] = initial_counts

    for k in range(n_steps - 1):
        current = counts[k].astype(int)
        total = int(current.sum())
        if total == 0:
            counts[k + 1] = current
            continue

        freqs = current / total
        payoff = payoff_matrix @ freqs
        birth_rates = config["base_birth"] * np.exp(config["selection_strength"] * payoff)
        death_rates = config["base_death"] + config["crowding"] * total

        expected_births = current * birth_rates * config["dt"]
        births_by_parent = rng.poisson(expected_births)

        expected_deaths = current * death_rates * config["dt"]
        deaths = rng.poisson(expected_deaths)
        deaths = np.minimum(deaths, current)

        offspring = np.zeros(3, dtype=int)
        for i in range(3):
            n_births = int(births_by_parent[i])
            if n_births > 0:
                offspring += rng.multinomial(n_births, mutation_matrix[i])

        next_counts = current - deaths + offspring
        counts[k + 1] = np.maximum(next_counts, 0)

    totals = counts.sum(axis=1).astype(float)
    freqs = np.divide(
        counts,
        totals[:, None],
        out=np.zeros_like(counts, dtype=float),
        where=totals[:, None] > 0,
    )
    simplex = barycentric_to_cartesian(freqs)

    return {
        "t": t,
        "counts": counts.astype(float),
        "totals": totals,
        "freqs": freqs,
        "simplex": simplex,
        "labels": LABELS,
        "colors": COLORS,
    }


def make_figure(result: dict[str, Any]) -> plt.Figure:
    t = result["t"]
    counts = result["counts"]
    totals = result["totals"]
    freqs = result["freqs"]
    pts = result["simplex"]

    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.4, 1.0], height_ratios=[1.15, 1.0])
    ax_counts = fig.add_subplot(gs[0, 0])
    ax_freqs = fig.add_subplot(gs[1, 0], sharex=ax_counts)
    ax_simplex = fig.add_subplot(gs[:, 1])

    ax_counts.stackplot(
        t,
        counts[:, 0], counts[:, 1], counts[:, 2],
        colors=COLORS,
        alpha=0.80,
        labels=LABELS,
    )
    ax_counts.plot(t, totals, color="black", linewidth=2.0, label="Total population")
    ax_counts.set_title("Advanced side-blotched lizard simulation", fontsize=15)
    ax_counts.set_ylabel("Absolute population size")
    ax_counts.grid(alpha=0.25, linestyle="--")
    ax_counts.legend(loc="upper left", frameon=True)

    for i in range(3):
        ax_freqs.plot(t, freqs[:, i], color=COLORS[i], linewidth=2.2, label=LABELS[i])
    ax_freqs.set_ylim(0, 1)
    ax_freqs.set_ylabel("Frequency")
    ax_freqs.set_xlabel("Time")
    ax_freqs.grid(alpha=0.25, linestyle="--")

    triangle = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, np.sqrt(3) / 2.0],
    ])
    ax_simplex.add_patch(Polygon(triangle, closed=True, fill=False, linewidth=2.0, edgecolor="black"))
    ax_simplex.plot(pts[:, 0], pts[:, 1], color="black", linewidth=1.5, alpha=0.9)
    ax_simplex.scatter(pts[0, 0], pts[0, 1], color="green", s=70, zorder=3, label="Start")
    ax_simplex.scatter(pts[-1, 0], pts[-1, 1], color="red", s=70, zorder=3, label="End")

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
    fig.tight_layout()
    return fig


def render(st: Any, result: dict[str, Any], config: dict[str, Any]) -> None:
    st.subheader("Side-blotched lizard / Rock–Paper–Scissors")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Orange", f"{result['freqs'][-1, 0]:.3f}")
    c2.metric("Final Blue", f"{result['freqs'][-1, 1]:.3f}")
    c3.metric("Final Yellow", f"{result['freqs'][-1, 2]:.3f}")
    c4.metric("Final population", f"{int(result['totals'][-1])}")

    fig = make_figure(result)
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)

    st.markdown("**Final counts**")
    st.write({
        "orange": int(result["counts"][-1, 0]),
        "blue": int(result["counts"][-1, 1]),
        "yellow": int(result["counts"][-1, 2]),
        "total": int(result["totals"][-1]),
    })

    with st.expander("Current parameters"):
        st.json(config)


MODEL = ModelSpec(
    key="side_blotched",
    label="Side-blotched lizard",
    description=(
        "Stochastic three-strategy RPS-style model with births, deaths, mutation, "
        "absolute population size, and simplex trajectory."
    ),
    render_controls=render_controls,
    run=run,
    render=render,
)
