import pytest
from pydantic import ValidationError
from extensions.event import types


class TestEventType:
    def test_invalid_event_name_regex(self, invalid_dsk_names):
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                ins = types.Event(
                    sender=name,
                    event_name="test_event",
                    data={"some_data_key": "some_data_value"},
                )

    def test_valid_event_name_regex(self, valid_dsk_names):
        for name in valid_dsk_names:
            ins = types.Event(
                sender=name,
                event_name="test_event",
                data={"some_data_key": "some_data_value"},
            )

    def test_event_invalid_sender_regex(self, invalid_dsk_names):
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                ins = types.Event(
                    sender="test_sender_name",
                    event_name=name,
                    data={"some_data_key": "some_data_value"},
                )
