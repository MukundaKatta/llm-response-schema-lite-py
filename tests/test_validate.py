"""Tests for ``llm_response_schema_lite.validate``."""

import pytest

from llm_response_schema_lite import (
    ValidationResult,
    parse_and_validate,
    validate,
    validate_response,
)


def test_validate_returns_ValidationResult():
    r = validate({}, {})
    assert isinstance(r, ValidationResult)
    assert r.valid is True


def test_validate_shape_format_passes():
    r = validate({"name": "Ada", "age": 36}, {"name": "str", "age": "int"})
    assert r.valid is True
    assert r.errors == []


def test_validate_shape_format_required_missing():
    r = validate({"name": "Ada"}, {"name": "str", "age": "int"})
    assert r.valid is False
    assert {"path": "age", "message": "required"} in r.errors


def test_validate_shape_format_optional_with_question_mark():
    r = validate({"name": "Ada"}, {"name": "str", "email": "str?"})
    assert r.valid is True


def test_validate_shape_type_mismatch():
    r = validate({"age": "thirty-six"}, {"age": "int"})
    assert r.valid is False
    assert {"path": "age", "message": "expected_int"} in r.errors


def test_validate_rule_format_with_enum():
    schema = {"status": {"type": "str", "required": True, "enum": ["ok", "error"]}}
    assert validate({"status": "ok"}, schema).valid is True
    assert validate({"status": "weird"}, schema).valid is False


def test_validate_rule_format_required_false_allows_missing():
    schema = {"opt": {"type": "int", "required": False}}
    assert validate({}, schema).valid is True


def test_validate_bool_distinct_from_int():
    # True/False must NOT satisfy "int".
    r = validate({"x": True}, {"x": "int"})
    assert r.valid is False


def test_validate_list_and_dict_shape():
    r = validate(
        {"tags": ["a", "b"], "meta": {"k": 1}},
        {"tags": "list", "meta": "dict"},
    )
    assert r.valid is True


def test_validate_js_aliases_work():
    # JS-style names (string/number/boolean/array/object) accepted.
    r = validate(
        {"a": "x", "b": 1, "c": True, "d": [], "e": {}},
        {"a": "string", "b": "number", "c": "boolean", "d": "array", "e": "object"},
    )
    assert r.valid is True


def test_validate_response_alias_works():
    assert validate_response({"x": 1}, {"x": "int"}).valid is True


def test_parse_and_validate_invalid_json():
    r = parse_and_validate("{not json", {"x": "int"})
    assert r.valid is False
    assert r.value is None
    assert {"path": "$", "message": "invalid_json"} in r.errors


def test_parse_and_validate_valid_json():
    r = parse_and_validate('{"x": 1}', {"x": "int"})
    assert r.valid is True
    assert r.value == {"x": 1}


def test_validate_non_dict_schema_raises():
    with pytest.raises(TypeError):
        validate({}, "nope")  # type: ignore[arg-type]
