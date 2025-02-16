import pytest

from tests.fixtures.types import *

from extensions.event.types import EventHandler


@pytest.fixture
def invalid_p_event_handler_list() -> list[type]:
    """
    Return a list of class type which should not pass PEventHandler
    runtime protocol check
    """

    class TestClass1:
        registrant: str = ""
        identifier: str = ""

    class TestClass2:
        event_name: str = "some_name"
        registrant: str = ""
        identifier: str = ""
        extra_field: int = 4

    class TestClass3:
        registry_id: str = "some_name"
        registrant: str = ""
        identifier: str = ""
        handler: int = 1
        extra_field: int = 3

    return [TestClass1, TestClass2, TestClass3]


@pytest.fixture
def valid_p_event_handler_list() -> list[type]:
    class TestClass1:
        registry_id: str = "some_name"
        registrant: str = "some_thing"
        identifier: str = "some_other.id"

        def handler(self, some_value):
            pass

    class WithoutHandlerFunc:
        registry_id: str = "some_name"
        registrant: str = "some_thing"
        identifier: str = "some_other.id"

    class TestClass2:
        registry_id: str = "some_name"
        registrant: str = "sdf"
        identifier: str = "dfhs"
        extra: int = 3

        def handler(self):
            pass

    class HasHandlerButNotFunc:
        registry_id: str = "some_name"
        registrant: str = "some_thing"
        identifier: str = "some_other.id"
        handler: int = 3

    return [TestClass1, TestClass2, HasHandlerButNotFunc, WithoutHandlerFunc]


@pytest.fixture
def event_handlers_sample_list(request) -> list[EventHandler]:
    event_name = getattr(request, "param", "default_event")

    class EventHandler1(EventHandler):
        def __init__(self):
            super().__init__(
                registry_id=event_name, registrant="rrss.test", identifier="sync.1"
            )

        def handler(self, data):
            return f"Sync handler with data: {data}"

    class EventHandler2(EventHandler):
        def __init__(self):
            super().__init__(
                registry_id=event_name, registrant="rrss.test", identifier="async.1"
            )

        async def handler(self, data):
            return f"Async handler with data: {data}"

    return [EventHandler1(), EventHandler2()]
