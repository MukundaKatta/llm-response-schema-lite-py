# llm-response-schema-lite-py

[![PyPI](https://img.shields.io/pypi/v/llm-response-schema-lite-py.svg)](https://pypi.org/project/llm-response-schema-lite-py/)
[![Python](https://img.shields.io/pypi/pyversions/llm-response-schema-lite-py.svg)](https://pypi.org/project/llm-response-schema-lite-py/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Tiny schema validator for structured LLM responses.** Two schema formats: a one-line shape spec (`{"name": "str", "age": "int"}`) and the JS-sibling rule format (`{"name": {"type": "str", "required": True, "enum": [...]}}`). Returns a `(valid, errors)` result you can hand straight back to the LLM as feedback. Zero runtime dependencies.

Python port of [@mukundakatta/llm-response-schema-lite](https://www.npmjs.com/package/@mukundakatta/llm-response-schema-lite).

## Install

```bash
pip install llm-response-schema-lite-py
```

## Quick start

### Shape format (Python-friendly, 1-liner)

```python
from llm_response_schema_lite import validate

schema = {"name": "str", "age": "int", "tags": "list", "email": "str?"}

validate({"name": "Ada", "age": 36, "tags": ["scientist"]}, schema)
# ValidationResult(valid=True, value={...}, errors=[])

validate({"name": "Ada", "age": "thirty-six"}, schema)
# ValidationResult(valid=False, errors=[
#   {"path": "age", "message": "expected_int"},
#   {"path": "tags", "message": "required"}
# ])
```

Suffix a type with `?` to mark it optional. Supported types: `str`, `int`,
`float`, `bool`, `list`, `dict` (and JS aliases: `string`, `number`,
`boolean`, `array`, `object`).

### JS-sibling rule format (full feature parity)

```python
schema = {
    "status": {"type": "str", "required": True, "enum": ["ok", "error"]},
    "code":   {"type": "int", "required": False},
}

validate({"status": "ok", "code": 200}, schema)        # valid
validate({"status": "weird"}, schema)                  # not_in_enum
validate({}, schema)                                   # required
```

### Parse JSON + validate in one shot

```python
from llm_response_schema_lite import parse_and_validate

result = parse_and_validate('{"name": "Ada"}', {"name": "str"})
result.valid   # True
result.value   # {"name": "Ada"}
```

If JSON parsing fails, you get back `ValidationResult(valid=False, value=None, errors=[{"path": "$", "message": "invalid_json"}])`.

## API

* `validate(value, schema) -> ValidationResult`
* `parse_and_validate(json_str, schema) -> ValidationResult`
* `validate_response(value, schema)` -- JS-parity alias of `validate`.

`ValidationResult` is a dataclass with `valid: bool`, `value: Any | None`, `errors: list[dict]`.

## License

MIT
