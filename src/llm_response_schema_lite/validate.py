"""Tiny schema validator for structured LLM responses.

Two schema formats are accepted; both are detected per-field:

1. **Shape (Python-friendly)**: a string type name, optionally suffixed
   with ``?`` for optional. E.g. ``{"name": "str", "email": "str?"}``.

2. **Rule (JS-sibling)**: a dict with ``type`` / ``required`` / ``enum``
   keys. E.g. ``{"name": {"type": "str", "required": True}}``.

Mixing both formats in one schema is allowed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, List, Mapping


@dataclass
class ValidationResult:
    """Result of :func:`validate`.

    Attributes:
        valid: True if all fields passed.
        value: The (untouched) input value, or ``None`` for parse errors.
        errors: List of ``{"path": str, "message": str}`` dicts. Empty if valid.
    """

    valid: bool
    value: Any = None
    errors: List[dict] = field(default_factory=list)


# Type-name -> Python type. Mirrors the JS sibling's ``typeof`` checks plus
# Python aliases for ergonomics.
_SYNONYMS = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "number": (int, float),
    "bool": bool,
    "boolean": bool,
    "list": list,
    "array": list,
    "dict": dict,
    "object": dict,
}


def _matches_type(value, type_name: str) -> bool:
    expected = _SYNONYMS.get(type_name)
    if expected is None:
        return False
    if expected is bool:
        # bool is a subclass of int in Python; handle distinctly so True/False
        # don't satisfy ``int``.
        return isinstance(value, bool)
    if expected in (int, float):
        if isinstance(value, bool):
            return False
        return isinstance(value, expected)
    if isinstance(expected, tuple):
        if isinstance(value, bool):
            return False
        return isinstance(value, expected)
    if expected is dict:
        return isinstance(value, dict)
    return isinstance(value, expected)


def _coerce_rule(rule) -> dict:
    """Turn a shape entry (``"str"`` / ``"str?"``) into the rule format."""
    if isinstance(rule, Mapping):
        return dict(rule)
    if isinstance(rule, str):
        if rule.endswith("?"):
            return {"type": rule[:-1], "required": False}
        return {"type": rule, "required": True}
    return {"type": None, "required": True}


def validate(value: Any, schema: Mapping) -> ValidationResult:
    """Validate ``value`` against ``schema``.

    See module docstring for the two accepted schema formats.
    """
    if not isinstance(schema, Mapping):
        raise TypeError("validate: schema must be a mapping (dict)")
    errors: List[dict] = []
    for key, raw_rule in schema.items():
        rule = _coerce_rule(raw_rule)
        present = isinstance(value, Mapping) and (key in value)
        required = rule.get("required", True)
        type_name = rule.get("type")
        enum = rule.get("enum")

        if not present:
            if required:
                errors.append({"path": str(key), "message": "required"})
            continue
        v = value[key]
        if type_name and not _matches_type(v, type_name):
            errors.append({"path": str(key), "message": "expected_" + str(type_name)})
        if enum is not None and v not in enum:
            errors.append({"path": str(key), "message": "not_in_enum"})

    return ValidationResult(valid=len(errors) == 0, value=value, errors=errors)


def validate_response(value: Any, schema: Mapping) -> ValidationResult:
    """JS-parity alias for ``validateResponse(value, schema)``."""
    return validate(value, schema)


def parse_and_validate(json_str: str, schema: Mapping) -> ValidationResult:
    """JSON-decode ``json_str``, then validate."""
    try:
        value = json.loads(json_str)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            value=None,
            errors=[{"path": "$", "message": "invalid_json"}],
        )
    return validate(value, schema)
