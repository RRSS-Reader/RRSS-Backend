import pytest
from typing import Any
from pydantic import ValidationError
from extensions.event import types as event_types
from extensions.event.manager import _SingleEventMgr
from extensions.event import errors as event_errs


class TestEventType:
    def test_invalid_event_name_regex(self, invalid_dsk_names):
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                ins = event_types.Event(
                    sender=name,
                    event_name="test_event",
                    data={"some_data_key": "some_data_value"},
                )

    def test_valid_event_name_regex(self, valid_dsk_names):
        for name in valid_dsk_names:
            ins = event_types.Event(
                sender=name,
                event_name="test_event",
                data={"some_data_key": "some_data_value"},
            )

    def test_event_invalid_sender_regex(self, invalid_dsk_names):
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                ins = event_types.Event(
                    sender="test_sender_name",
                    event_name=name,
                    data={"some_data_key": "some_data_value"},
                )


class TestEventHandlerType:
    def test_invalid_handler_name(self, invalid_p_event_handler_list) -> None:

        for cls in invalid_p_event_handler_list:
            with pytest.raises(ValidationError):
                event_types.EventHandler.model_validate(cls())

    def test_valid_event_handler_protocol(self, valid_p_event_handler_list) -> None:
        for cls in valid_p_event_handler_list:
            event_types.EventHandler.model_validate(cls())


class TestEventSingleHandler:
    # TODO
    def test_event_adding(self, event_handlers_sample_list) -> None:
        # create single event mgr
        mgr = _SingleEventMgr[str]("rrss.test.test_event_1")

        # add
        for event in event_handlers_sample_list:
            mgr.add(event)

        # try add duplicated handler
        with pytest.raises(event_errs.DuplicatedHandlerID):
            mgr.add(event_handlers_sample_list[0])

        # custom new handler
        class CustomEventHandler(event_types.EventHandler):

            def __init__(self):
                super().__init__(registrant="rrss.test.another", identifier="sync.1")

            def handler(self, data):
                return f"Sync handler with data: {data}"

        # add new handler
        mgr.add(CustomEventHandler())

        # check .has() method
        assert mgr.has("rrss.test.another")
        assert mgr.has("rrss.test.another", "sync.1")
        assert mgr.has("rrss.test.another", "async.1") == False

        # try remove non-exists handler
        with pytest.raises(event_errs.HandlerNotFound):
            mgr.remove("rrss.test.not_exists", "some.id")
        with pytest.raises(event_errs.HandlerNotFound):
            mgr.remove("rrss.test.another", "some.id.not_exists")

        # remove handler
        mgr.remove("rrss.test.another", "sync.1")
        # registrant should no longer exists after all handlers being removed
        assert mgr.has("rrss.test.another") == False

        # check handlers() generator
        assert len([i for i in mgr.handlers()]) == len(event_handlers_sample_list)
