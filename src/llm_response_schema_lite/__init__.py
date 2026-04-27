"""llm_response_schema_lite -- tiny schema validator for structured LLM output.

Public surface:

* ``validate(value, schema)`` -- main entry point. Accepts either the
  one-line shape format (``{"name": "str"}``) or the JS-sibling rule
  format (``{"name": {"type": "str", "required": True}}``).
* ``validate_response(value, schema)`` -- JS-parity alias.
* ``parse_and_validate(json_str, schema)`` -- ``json.loads`` then
  validate. JSON parse errors are reported as
  ``ValidationResult(valid=False, value=None, errors=[{"path": "$", "message": "invalid_json"}])``.
* ``ValidationResult`` -- dataclass (``valid``, ``value``, ``errors``).
"""

from .validate import (
    ValidationResult,
    parse_and_validate,
    validate,
    validate_response,
)

__version__ = "0.1.0"
VERSION = __version__

__all__ = [
    "VERSION",
    "ValidationResult",
    "parse_and_validate",
    "validate",
    "validate_response",
]
