from typing import Any
import pytest
from pydantic import ValidationError

from utils import types


class TestDottedSnakeCaseKeyDict:
    def test_invalid_key(self, invalid_dsk_names):
        typed_dict = types.RRSSEntityIdKeyDict[Any]()
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                typed_dict[name] = "some_value"

    def test_valid_key(self, valid_dsk_names):
        typed_dict = types.RRSSEntityIdKeyDict[Any]()
        for name in valid_dsk_names:
            typed_dict[name] = "some_value"

    def test_invalid_values(self, valid_dsk_names) -> None:
        typed_dict = types.RRSSEntityIdKeyDict[int]()

        # no runtime check on value type
        # should pass with no raise
        for name in valid_dsk_names:
            typed_dict[name] = "some_value"  # type: ignore
