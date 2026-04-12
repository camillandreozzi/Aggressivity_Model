from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


RenderControls = Callable[[Any], dict[str, Any]]
RunModel = Callable[[dict[str, Any]], dict[str, Any]]
RenderModel = Callable[[Any, dict[str, Any], dict[str, Any]], None]


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    description: str
    render_controls: RenderControls
    run: RunModel
    render: RenderModel
