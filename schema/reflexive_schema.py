#!/usr/bin/env python3
"""
reflexive_schema.py: the Python kit's reader for schema/reflexive.schema.json.

That JSON file is the single source of truth. This module loads it and checks
documents against one of its $defs, using only the JSON Schema keywords the
file actually uses: type, const, enum, pattern, minLength, minimum, required,
properties, additionalProperties (false), oneOf, $ref (local). Any other
keyword makes validation fail loudly instead of passing silently, so the
schema cannot quietly outgrow this reader. The TypeScript workspace validates
the same file with Ajv (schema/typescript/).

    from reflexive_schema import SCHEMA, enum, validate
    errors = validate(doc, "mobile_envelope")   # [] means valid

Stdlib only.
"""
import json
import re
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / "reflexive.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

# Keywords this reader implements, plus annotations it may safely ignore.
HANDLED = {"type", "const", "enum", "pattern", "minLength", "minimum", "required",
           "properties", "additionalProperties", "oneOf", "$ref"}
IGNORED = {"description", "title", "$comment"}

TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "null": lambda v: v is None,
}


def definition(name: str) -> dict:
    return SCHEMA["$defs"][name]


def enum(name: str) -> list:
    """The allowed values of an enum $def, e.g. enum("fidelity")."""
    return list(definition(name)["enum"])


def _check(value, node, path, errors):
    unknown = {k for k in node if k not in HANDLED | IGNORED and not k.startswith("x-")}
    if unknown:
        raise ValueError(f"schema keyword(s) {sorted(unknown)} at {path or '/'} not supported by this reader")

    if "$ref" in node:
        ref = node["$ref"]
        if not ref.startswith("#/$defs/"):
            raise ValueError(f"only local $defs refs are supported, got {ref}")
        _check(value, definition(ref[len("#/$defs/"):]), path, errors)
    if "type" in node and not TYPES[node["type"]](value):
        errors.append(f"{path or '/'}: must be {node['type']}")
        return
    if "const" in node and value != node["const"]:
        errors.append(f"{path or '/'}: must be {node['const']!r}")
    if "enum" in node and value not in node["enum"]:
        errors.append(f"{path or '/'}: must be one of {node['enum']}")
    if "pattern" in node and isinstance(value, str) and not re.search(node["pattern"], value):
        errors.append(f"{path or '/'}: has the wrong shape")
    if "minLength" in node and isinstance(value, str) and len(value) < node["minLength"]:
        errors.append(f"{path or '/'}: too short")
    if "minimum" in node and TYPES["number"](value) and value < node["minimum"]:
        errors.append(f"{path or '/'}: must be >= {node['minimum']}")
    if "oneOf" in node:
        passing = 0
        for option in node["oneOf"]:
            sub = []
            _check(value, option, path, sub)
            passing += not sub
        if passing != 1:
            errors.append(f"{path or '/'}: must match exactly one allowed form")
    if isinstance(value, dict):
        props = node.get("properties", {})
        for key in node.get("required", []):
            if key not in value:
                errors.append(f"{path}/{key}: missing")
        if node.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}/{key}: unknown field")
        for key, sub in props.items():
            if key in value:
                _check(value[key], sub, f"{path}/{key}", errors)


def validate(doc, def_name: str) -> list:
    """Return a list of problems; an empty list means doc is valid."""
    errors = []
    _check(doc, definition(def_name), "", errors)
    return errors
