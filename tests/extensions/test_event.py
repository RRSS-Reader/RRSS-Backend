import pytest
from pydantic import ValidationError
from pytest import fixture
from extensions.event import types


@fixture
def invalid_dsk_names() -> list[str]:
    """Return a sequence of invalid dot-separated snake-case string"""
    return [
        "invalid-with-dash.some.name",
        "some.names.with.extra.dots.",
        "",
        ".dot.at.begining",
        "some.other&.invalid.charater",
        "invalid:char",
    ]


class TestEventType:
    def test_event_name_regex(self, invalid_dsk_names):
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                ins = types.Event(
                    sender=name,
                    event_name="test_event",
                    data={"some_data_key": "some_data_value"},
                )

    def test_event_sender_regex(self, invalid_dsk_names):
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                ins = types.Event(
                    sender="test_sender_name",
                    event_name=name,
                    data={"some_data_key": "some_data_value"},
                )
