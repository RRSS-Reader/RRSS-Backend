import pytest

from tests.fixtures.types import *


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
        registrant: str = ""
        identifier: str = ""
        extra_field: int = 4

    class TestClass3:
        registrant: str = ""
        identifier: str = ""
        handler: int = 1
        extra_field: int = 3

    return [TestClass1, TestClass2, TestClass3]


@pytest.fixture
def valid_p_event_handler_list() -> list[type]:
    class TestClass1:
        registrant: str = "some_thing"
        identifier: str = "some_other.id"

        def handler(self, some_value):
            pass

    class TestClass2:
        registrant: str = "sdf"
        identifier: str = "dfhs"
        extra: int = 3

        def handler(self):
            pass

    return [TestClass1, TestClass2]
