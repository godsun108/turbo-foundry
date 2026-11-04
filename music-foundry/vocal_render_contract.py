"""Provider-neutral vocal render contract. This validates plans; it does not render audio."""
from __future__ import annotations

from typing import Any

SCHEMA = "turbo.music-foundry.vocal-render.v1"
RENDERER_SCHEMA = "turbo.music-foundry.renderer.v1"
SUPPORTED_MODES = {"spoken", "sung"}
SUPPORTED_FORMATS = {"wav"}
SUPPORTED_SAMPLE_RATES = {44100, 48000}
SUPPORTED_BIT_DEPTHS = {16, 24}
SUPPORTED_CHANNELS = {1, 2}
FORBIDDEN_SECRET_KEYS = {
    "api_key", "apikey", "access_token", "refresh_token", "client_secret",
    "authorization", "password", "secret", "token",
}


class Validation:
    def __init__(self, ok: bool, errors: tuple[str, ...]):
        self.ok = ok
        self.errors = errors


def _secret_paths(value: Any, prefix: str = "") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key.lower().replace("-", "_") in FORBIDDEN_SECRET_KEYS:
                found.append(path)
            found.extend(_secret_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_secret_paths(child, f"{prefix}[{index}]"))
    return found


def validate_renderer_descriptor(descriptor: dict) -> Validation:
    errors = []
    if descriptor.get("schema") != RENDERER_SCHEMA:
        errors.append(f"schema must be {RENDERER_SCHEMA}")
    if not isinstance(descriptor.get("id"), str) or not descriptor["id"].strip():
        errors.append("id must be a non-empty string")
    if descriptor.get("execution") not in {"local", "remote"}:
        errors.append("execution must be local or remote")
    modes = descriptor.get("modes")
    if not isinstance(modes, list) or not modes or not set(modes) <= SUPPORTED_MODES:
        errors.append("modes must be a non-empty list containing only spoken and/or sung")
    formats = descriptor.get("formats")
    if not isinstance(formats, list) or "wav" not in formats:
        errors.append("formats must include wav")
    if descriptor.get("credential_handling") != "server_or_local_only":
        errors.append("credentials must remain server-side or local; never in browser descriptors")
    if _secret_paths(descriptor):
        errors.append("descriptor contains a forbidden credential field")
    return Validation(not errors, tuple(errors))


def validate_render_request(request: dict, renderer: dict | None = None) -> Validation:
    errors = []
    if request.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    mode = request.get("mode")
    if mode not in SUPPORTED_MODES:
        errors.append("mode must be spoken or sung")
    if not isinstance(request.get("project_id"), str) or not request["project_id"].strip():
        errors.append("project_id must be a non-empty string")
    if not isinstance(request.get("source_ref"), str) or not request["source_ref"].strip():
        errors.append("source_ref must identify the approved lyric/timing source")
    if request.get("format") not in SUPPORTED_FORMATS:
        errors.append("format must be wav")
    if request.get("sample_rate") not in SUPPORTED_SAMPLE_RATES:
        errors.append("sample_rate must be 44100 or 48000")
    if request.get("bit_depth") not in SUPPORTED_BIT_DEPTHS:
        errors.append("bit_depth must be 16 or 24")
    if request.get("channels") not in SUPPORTED_CHANNELS:
        errors.append("channels must be 1 or 2")
    layers = request.get("layers")
    if not isinstance(layers, list) or not layers or any(
        not isinstance(layer, str) or not layer.strip() for layer in layers
    ):
        errors.append("layers must be a non-empty list of named vocal layers")
    if _secret_paths(request):
        errors.append("render request contains a forbidden credential field")
    if renderer is not None:
        result = validate_renderer_descriptor(renderer)
        errors.extend(result.errors)
        if mode in SUPPORTED_MODES and mode not in renderer.get("modes", []):
            errors.append(f"renderer does not support {mode} mode")
        if request.get("format") not in renderer.get("formats", []):
            errors.append("renderer does not support the requested format")
    return Validation(not errors, tuple(errors))


def make_render_request(
    *, project_id: str, source_ref: str, mode: str, layers: list[str],
    sample_rate: int = 48000, bit_depth: int = 24, channels: int = 1,
) -> dict:
    """Create a deterministic WAV request; caller must validate before dispatch."""
    return {
        "schema": SCHEMA,
        "project_id": project_id,
        "source_ref": source_ref,
        "mode": mode,
        "format": "wav",
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "channels": channels,
        "layers": list(layers),
        "dispatch": "not_authorized",
    }
