from __future__ import annotations

import time
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from egt_core.base import ModelSpec


def theoretical_hawk_equilibrium(v: float, c: float, d: float) -> float | None:
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


def pairwise_payoff(s1: int, s2: int, v: float, c: float, d: float) -> tuple[float, float]:
    if s1 == 1 and s2 == 1:
        payoff = (v - c) / 2.0
        return payoff, payoff
    if s1 == 1 and s2 == 0:
        return v, 0.0
    if s1 == 0 and s2 == 1:
        return 0.0, v
    payoff = v / 2.0 - d
    return payoff, payoff


def render_controls(ui: Any) -> dict[str, Any]:
    ui.subheader("Population")
    n = ui.slider("Agents", 20, 400, 120, 10)
    box_size = ui.number_input("Box size", min_value=0.5, max_value=10.0, value=1.0, step=0.1)
    initial_hawk_fraction = ui.slider("Initial hawk fraction", 0.0, 1.0, 0.95, 0.01)

    ui.subheader("Payoff")
    v = ui.number_input("Resource value (V)", min_value=0.0, max_value=500.0, value=50.0, step=5.0)
    c = ui.number_input("Injury cost (C)", min_value=0.0, max_value=500.0, value=100.0, step=5.0)
    d = ui.number_input("Display cost (D)", min_value=0.0, max_value=500.0, value=10.0, step=1.0)

    ui.subheader("Dynamics")
    frames = ui.slider("Frames", 50, 1000, 300, 25)
    rounds_per_frame = ui.slider("Encounter rounds per frame", 1, 10, 1, 1)
    updates_per_frame = ui.slider("Strategy updates per frame", 1, 20, 5, 1)
    mutation_rate = ui.slider("Mutation / experimentation rate", 0.0, 0.2, 0.01, 0.001)
    beta = ui.slider("Imitation strength (beta)", 0.01, 1.0, 0.10, 0.01)
    jitter_scale = ui.slider("Visual movement", 0.0, 0.1, 0.01, 0.001)
    seed = ui.number_input("Random seed", min_value=0, max_value=1_000_000, value=42, step=1)

    return {
        "n": int(n),
        "box_size": float(box_size),
        "initial_hawk_fraction": float(initial_hawk_fraction),
        "v": float(v),
        "c": float(c),
        "d": float(d),
        "frames": int(frames),
        "rounds_per_frame": int(rounds_per_frame),
        "updates_per_frame": int(updates_per_frame),
        "mutation_rate": float(mutation_rate),
        "beta": float(beta),
        "jitter_scale": float(jitter_scale),
        "seed": int(seed),
    }


def run(config: dict[str, Any]) -> dict[str, Any]:
    rng = np.random.default_rng(config["seed"])
    n = config["n"]
    frames = config["frames"]
    box_size = config["box_size"]

    positions = rng.uniform(0.0, box_size, size=(n, 2))
    strategies = (rng.random(n) < config["initial_hawk_fraction"]).astype(int)
    payoffs = np.zeros(n, dtype=float)

    positions_history = np.zeros((frames + 1, n, 2), dtype=float)
    strategies_history = np.zeros((frames + 1, n), dtype=np.int8)
    mean_payoff_history = np.zeros(frames + 1, dtype=float)
    hawk_history = np.zeros(frames + 1, dtype=float)

    positions_history[0] = positions
    strategies_history[0] = strategies
    hawk_history[0] = float(np.mean(strategies))

    for frame in range(1, frames + 1):
        payoffs[:] = 0.0
        for _ in range(config["rounds_per_frame"]):
            order = rng.permutation(n)
            for k in range(0, n - 1, 2):
                i = order[k]
                j = order[k + 1]
                p_i, p_j = pairwise_payoff(
                    int(strategies[i]),
                    int(strategies[j]),
                    config["v"],
                    config["c"],
                    config["d"],
                )
                payoffs[i] += p_i
                payoffs[j] += p_j

        for _ in range(config["updates_per_frame"]):
            i, j = rng.choice(n, size=2, replace=False)
            prob_copy_j = 1.0 / (1.0 + np.exp(-config["beta"] * (payoffs[j] - payoffs[i])))
            if rng.random() < prob_copy_j:
                strategies[i] = strategies[j]
            if rng.random() < config["mutation_rate"]:
                strategies[i] = 1 - strategies[i]

        positions += rng.normal(0.0, config["jitter_scale"], size=positions.shape)
        positions = np.clip(positions, 0.0, box_size)

        positions_history[frame] = positions
        strategies_history[frame] = strategies
        hawk_history[frame] = float(np.mean(strategies))
        mean_payoff_history[frame] = float(np.mean(payoffs))

    return {
        "positions_history": positions_history,
        "strategies_history": strategies_history,
        "hawk_history": hawk_history,
        "mean_payoff_history": mean_payoff_history,
        "x_star": theoretical_hawk_equilibrium(config["v"], config["c"], config["d"]),
        "box_size": box_size,
        "frames": frames,
    }


def make_figure(result: dict[str, Any], frame_idx: int) -> plt.Figure:
    positions = result["positions_history"][frame_idx]
    strategies = result["strategies_history"][frame_idx]
    hawk_history = result["hawk_history"]
    mean_payoff_history = result["mean_payoff_history"]
    box_size = result["box_size"]
    x_star = result["x_star"]

    fig, (ax_box, ax_ts) = plt.subplots(
        1,
        2,
        figsize=(12, 5.5),
        gridspec_kw={"width_ratios": [1.1, 1.2]},
    )

    ax_box.set_xlim(0.0, box_size)
    ax_box.set_ylim(0.0, box_size)
    ax_box.set_xticks([])
    ax_box.set_yticks([])
    ax_box.set_title("Hawks and doves in a box")
    colors = np.where(strategies == 1, "red", "blue")
    ax_box.scatter(
        positions[:, 0],
        positions[:, 1],
        c=colors,
        s=55,
        alpha=0.8,
        edgecolors="black",
        linewidths=0.3,
    )

    hawks = int(np.sum(strategies == 1))
    doves = int(np.sum(strategies == 0))
    ax_box.text(
        0.02,
        1.02,
        f"frame={frame_idx:03d}  hawks={hawks}  doves={doves}",
        transform=ax_box.transAxes,
        fontsize=10,
        va="bottom",
    )

    ax_ts.set_xlim(0, len(hawk_history) - 1)
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

    x_vals = np.arange(frame_idx + 1)
    ax_ts.plot(x_vals, hawk_history[: frame_idx + 1], linewidth=2.0, label="Observed hawk proportion")

    payoff_arr = mean_payoff_history[: frame_idx + 1]
    if np.max(payoff_arr) > np.min(payoff_arr):
        scaled_payoff = (payoff_arr - np.min(payoff_arr)) / (np.max(payoff_arr) - np.min(payoff_arr))
    else:
        scaled_payoff = np.zeros_like(payoff_arr)

    ax_ts.plot(x_vals, scaled_payoff, linewidth=1.5, linestyle=":", label="Scaled mean payoff")
    ax_ts.legend(loc="upper right")
    fig.tight_layout()
    return fig


def render(st: Any, result: dict[str, Any], config: dict[str, Any]) -> None:
    st.subheader("Hawk–Dove")
    c1, c2, c3 = st.columns(3)
    c1.metric("Final hawk share", f"{result['hawk_history'][-1]:.3f}")
    c2.metric("Final dove share", f"{1 - result['hawk_history'][-1]:.3f}")
    c3.metric(
        "Theoretical hawk equilibrium",
        "—" if result["x_star"] is None else f"{result['x_star']:.3f}",
    )

    frame_idx = st.slider("Frame", 0, int(result["frames"]), int(result["frames"]), 1)
    fig = make_figure(result, frame_idx)
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)

    with st.expander("Play animation"):
        speed = st.slider("Delay (seconds)", 0.01, 0.20, 0.04, 0.01, key="hawk_speed")
        step = st.slider("Frame step", 1, 20, 5, 1, key="hawk_step")
        if st.button("Play", key="hawk_play"):
            placeholder = st.empty()
            for idx in range(0, int(result["frames"]) + 1, int(step)):
                fig = make_figure(result, idx)
                placeholder.pyplot(fig, clear_figure=True)
                plt.close(fig)
                time.sleep(float(speed))


MODEL = ModelSpec(
    key="hawk_dove",
    label="Hawk–Dove",
    description=(
        "Agent-based Hawk–Dove with pairwise encounters, Fermi imitation, "
        "small mutation, and the original box-plus-time-series view."
    ),
    render_controls=render_controls,
    run=run,
    render=render,
)
