from __future__ import annotations

from egt_core.base import ModelSpec
from egt_core.models import hawk_dove, side_blotched


_MODELS: dict[str, ModelSpec] = {
    hawk_dove.MODEL.key: hawk_dove.MODEL,
    side_blotched.MODEL.key: side_blotched.MODEL,
}


def get_models() -> list[ModelSpec]:
    return list(_MODELS.values())


def get_model(key: str) -> ModelSpec:
    return _MODELS[key]
