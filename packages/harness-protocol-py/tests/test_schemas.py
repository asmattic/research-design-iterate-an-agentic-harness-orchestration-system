"""Schema-level contract tests: validity, $id convention, and key enums."""

from __future__ import annotations

import pytest

harness_protocol = pytest.importorskip("harness_protocol")
jsonschema = pytest.importorskip("jsonschema")

from protocol_testlib import EXPECTED_SCHEMA_NAMES, EXPECTED_VERSION, SCHEMA_ID_TEMPLATE

TICKET_LIFECYCLE_KINDS = {
    "ticket_claimed",
    "ticket_resolved",
    "fog_graduated",
    "scope_ruled_out",
}
ORCHESTRATOR_STATE_FIELDS = {
    "phase",
    "destination",
    "decisions",
    "fog",
    "out_of_scope",
    "tickets",
}
TICKET_TYPES = {"grilling", "prototype", "research", "task", "implementation"}


def _find_property_schema(schema, prop_name):
    """Depth-first search for the subschema of a property named prop_name.

    Tolerates nesting under items/additionalProperties/anyOf/etc. so the tests
    do not over-specify the schema's internal layout.
    """
    if isinstance(schema, dict):
        props = schema.get("properties")
        if isinstance(props, dict) and prop_name in props:
            return props[prop_name]
        for value in schema.values():
            found = _find_property_schema(value, prop_name)
            if found is not None:
                return found
    elif isinstance(schema, list):
        for value in schema:
            found = _find_property_schema(value, prop_name)
            if found is not None:
                return found
    return None


def _collect_enum_values(schema):
    """Union of every ``enum`` list reachable inside a subschema."""
    values = set()
    if isinstance(schema, dict):
        enum = schema.get("enum")
        if isinstance(enum, list):
            values.update(v for v in enum if isinstance(v, str))
        for value in schema.values():
            values.update(_collect_enum_values(value))
    elif isinstance(schema, list):
        for value in schema:
            values.update(_collect_enum_values(value))
    return values


def test_version_constants():
    assert harness_protocol.__version__ == EXPECTED_VERSION
    assert harness_protocol.PROTOCOL_VERSION == EXPECTED_VERSION


def test_schema_names_tuple():
    assert tuple(harness_protocol.SCHEMA_NAMES) == EXPECTED_SCHEMA_NAMES


@pytest.mark.parametrize("name", EXPECTED_SCHEMA_NAMES)
def test_schema_is_valid_draft_2020_12(name):
    schema = harness_protocol.load_schema(name)
    assert isinstance(schema, dict)
    jsonschema.Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("name", EXPECTED_SCHEMA_NAMES)
def test_schema_id_follows_convention(name):
    schema = harness_protocol.load_schema(name)
    assert schema.get("$id") == SCHEMA_ID_TEMPLATE.format(name=name)


def test_event_envelope_kind_covers_ticket_lifecycle():
    schema = harness_protocol.load_schema("event-envelope")
    kind = _find_property_schema(schema, "kind")
    assert kind is not None, "event-envelope schema has no 'kind' property"
    kinds = _collect_enum_values(kind)
    missing = TICKET_LIFECYCLE_KINDS - kinds
    assert not missing, (
        f"event-envelope kind enum is missing ticket-lifecycle kinds "
        f"{sorted(missing)} (PRD section 15.3); enum values found: {sorted(kinds)}"
    )


def test_orchestrator_state_has_all_map_fields():
    schema = harness_protocol.load_schema("orchestrator-state")
    props = schema.get("properties")
    assert isinstance(props, dict), "orchestrator-state schema has no properties"
    missing = ORCHESTRATOR_STATE_FIELDS - set(props)
    assert not missing, (
        f"orchestrator-state is missing fields {sorted(missing)} "
        f"(PRD section 15.5); properties present: {sorted(props)}"
    )


def test_orchestrator_state_phase_enum():
    schema = harness_protocol.load_schema("orchestrator-state")
    phase = _find_property_schema(schema, "phase")
    assert phase is not None, "orchestrator-state schema has no 'phase' property"
    assert phase.get("enum") == ["wayfinding", "execution"]


def test_orchestrator_state_ticket_type_enum():
    schema = harness_protocol.load_schema("orchestrator-state")
    tickets = _find_property_schema(schema, "tickets")
    assert tickets is not None, "orchestrator-state schema has no 'tickets' property"
    ticket_type = _find_property_schema(tickets, "type")
    assert ticket_type is not None, (
        "orchestrator-state tickets items have no 'type' property"
    )
    types = _collect_enum_values(ticket_type)
    missing = TICKET_TYPES - types
    assert not missing, (
        f"orchestrator-state ticket type enum is missing {sorted(missing)} "
        f"(PRD section 15.5); enum values found: {sorted(types)}"
    )


def test_memory_index_sensitivity_enum():
    schema = harness_protocol.load_schema("memory-index")
    sensitivity = _find_property_schema(schema, "sensitivity")
    assert sensitivity is not None, (
        "memory-index schema has no 'sensitivity' property"
    )
    assert sensitivity.get("enum") == ["public", "internal", "pii", "secret"]
