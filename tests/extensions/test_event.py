from typing import cast
import pytest
import anyio
from typing import Any
from pydantic import ValidationError
from extensions.event import types as event_types
from extensions.event import errors as event_errs
from extensions.event.types import Event, EventHandler
from extensions.event.manager import _SingleEventMgr, EventManager


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
    def test_event_adding(self, event_handlers_sample_list) -> None:
        """
        Test event adding, existence checking, and removing.
        """
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
                super().__init__(
                    event_name="some_name",
                    registrant="rrss.test.another",
                    identifier="sync.1",
                )

            def handler(self, data):
                return f"Sync handler with data: {data}"

        # add new handler
        mgr.add(CustomEventHandler())

        # check .has() method
        assert mgr.has("rrss.test.another", None)
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
        assert mgr.has("rrss.test.another", None) == False

        # check handlers() generator
        assert len([i for i in mgr.list()]) == len(event_handlers_sample_list)

    async def test_event_emitting(self, anyio_backend):
        ret1: int = 0
        ret2: int = 1
        mgr = _SingleEventMgr[int]("rrss.test.emit_test")

        class EventHandler1(event_types.EventHandler[int]):
            def __init__(self):
                super().__init__(
                    event_name="some_name",
                    registrant="rrss.test",
                    identifier="rrss.test.1",
                )

            def handler(self, event):
                nonlocal ret1
                ret1 = event.data + 1

        class EventHandler2(event_types.EventHandler[int]):
            def __init__(self):
                super().__init__(
                    event_name="some_name",
                    registrant="rrss.test",
                    identifier="rrss.test.2",
                )

            async def handler(self, event):
                nonlocal ret2
                await anyio.sleep(0.2)
                ret2 = event.data + 2

        mgr.add(EventHandler1())
        mgr.add(EventHandler2())

        await mgr.emit(event_types.Event(event_name="unnecessary", data=3))

        # check if two handlers were both triggered
        assert ret1 == 4
        assert ret2 == 5

        mgr.remove("rrss.test", "rrss.test.2")

        await mgr.emit(event_types.Event(event_name="unnecessary", data=10))

        assert ret1 == 11
        assert ret2 == 5


class TestEventManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mgr = EventManager()

    def test_add_event(self):
        self.mgr.add_registry("rrss.test.test_event")
        assert self.mgr.add_registry("rrss.test.test_event")

    def test_add_duplicate_event(self):
        self.mgr.add_registry("rrss.test.test_event")
        self.mgr.add_registry("rrss.test.test_event")
        assert self.mgr.has_registry("rrss.test.test_event")

    @pytest.mark.parametrize(
        "event_handlers_sample_list",
        ["rrss.test.handler_test"],
        indirect=True,
    )
    def test_add_handler(self, event_handlers_sample_list):
        event_name = "rrss.test.handler_test"

        self.mgr.add_registry(event_name)

        for handler in event_handlers_sample_list:
            handler = cast(EventHandler, handler)
            self.mgr.add_data(handler)

        assert self.mgr.has_registry(event_name)

        for handler in event_handlers_sample_list:
            handler = cast(event_types.EventHandler, handler)
            assert self.mgr._try_get_registry(event_name).has(
                handler.registrant, handler.identifier
            )

    async def test_emit_event(self, anyio_backend):
        event_name = "rrss.test.emit_test"
        self.mgr.add_registry(event_name)

        ret = {"value": 0}

        class EventHandler1(event_types.EventHandler[int]):
            def __init__(self):
                super().__init__(
                    event_name=event_name,
                    registrant="rrss.test",
                    identifier="rrss.test.1",
                )

            def handler(self, event):
                ret["value"] = event.data + 1

        handler = EventHandler1()
        self.mgr.add_data(handler)

        await self.mgr.emit(event_types.Event(event_name=event_name, data=10))
        assert ret["value"] == 11

    @pytest.mark.parametrize(
        "event_handlers_sample_list",
        ["rrss.test.remove_handler"],
        indirect=True,
    )
    def test_remove_handler(self, event_handlers_sample_list):
        event_name = "rrss.test.remove_handler"
        self.mgr.add_registry(event_name)

        handler = event_handlers_sample_list[0]
        handler = cast(event_types.EventHandler, handler)
        self.mgr.add_data(handler)

        assert self.mgr._try_get_registry(event_name).has(
            handler.registrant, handler.identifier
        )

        self.mgr.remove_data(handler)

        assert not self.mgr._try_get_registry(event_name).has(
            handler.registrant, handler.identifier
        )

    @pytest.mark.parametrize(
        "event_handlers_sample_list",
        ["rrss.test.remove_all"],
        indirect=True,
    )
    def test_remove_all_by_registrant(self, event_handlers_sample_list):
        event_name = "rrss.test.remove_all"
        self.mgr.add_registry(event_name)

        for handler in event_handlers_sample_list:
            self.mgr.add_data(handler)

        registrant = event_handlers_sample_list[0].registrant
        self.mgr.remove_data(registrant)

        assert not any(
            self.mgr._try_get_registry(event_name).has(registrant, h.identifier)
            for h in event_handlers_sample_list
        )
