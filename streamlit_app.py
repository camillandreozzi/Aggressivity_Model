from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from egt_core.registry import get_model, get_models


st.set_page_config(
    page_title="Evolutionary Game Theory Lab",
    page_icon="🧬",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def run_model_cached(model_key: str, config_json: str) -> dict[str, Any]:
    model = get_model(model_key)
    config = json.loads(config_json)
    return model.run(config)


def main() -> None:
    st.title("Evolutionary Game Theory Lab")
    st.caption(
        "Interactive front-end for the simulation code. New models can be added by "
        "registering one module in the model registry."
    )

    models = get_models()
    labels = {model.label: model.key for model in models}

    with st.sidebar:
        st.header("Model")
        selected_label = st.selectbox("Choose a model", list(labels.keys()))
        model = get_model(labels[selected_label])

        st.markdown(f"**{model.label}**")
        st.write(model.description)
        st.divider()
        config = model.render_controls(st)
        run_now = st.button("Run simulation", type="primary", use_container_width=True)

    if "last_model_key" not in st.session_state:
        st.session_state.last_model_key = model.key
    if "last_config_json" not in st.session_state:
        st.session_state.last_config_json = json.dumps(config, sort_keys=True)

    current_config_json = json.dumps(config, sort_keys=True)

    if run_now or model.key != st.session_state.last_model_key or current_config_json != st.session_state.last_config_json:
        st.session_state.last_model_key = model.key
        st.session_state.last_config_json = current_config_json

    config_json = st.session_state.last_config_json

    with st.spinner("Simulating..."):
        result = run_model_cached(st.session_state.last_model_key, config_json)

    model.render(st, result, json.loads(config_json))


if __name__ == "__main__":
    main()
