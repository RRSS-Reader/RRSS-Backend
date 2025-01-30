from typing import Any
import pytest
from pydantic import ValidationError, TypeAdapter, BaseModel

from utils import types as util_types


class TestDottedSnakeCaseKeyDict:
    def test_invalid_key(self, invalid_dsk_names):
        typed_dict = util_types.RRSSEntityIdKeyDict[Any]()
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                typed_dict[name] = "some_value"

    def test_valid_key(self, valid_dsk_names):
        typed_dict = util_types.RRSSEntityIdKeyDict[Any]()
        for name in valid_dsk_names:
            typed_dict[name] = "some_value"

    def test_invalid_values(self, valid_dsk_names) -> None:
        typed_dict = util_types.RRSSEntityIdKeyDict[int]()

        # no runtime check on value type
        # should pass with no raise
        for name in valid_dsk_names:
            typed_dict[name] = "some_value"  # type: ignore


class TestKeyCheckedDict:
    def test_invalid_key(self, invalid_dsk_names):
        typed_dict = util_types.KeyCheckedDict[util_types.RRSSEntityIdField, Any]()
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                typed_dict[name] = "some_value"

    def test_valid_key(self, valid_dsk_names):
        typed_dict = util_types.KeyCheckedDict[util_types.RRSSEntityIdField, Any]()
        for name in valid_dsk_names:
            typed_dict[name] = "some_value"


class TestSnakeCaseField:
    adapter = TypeAdapter(util_types.SnakeCaseField)

    def __repr__(self):
        return f"<Test curname={self.cur_name}>"

    def test_valid_snake_case_names(self, valid_snake_case_names):
        for name in valid_snake_case_names:
            self.cur_name = name
            self.adapter.validate_python(name)

    def test_invalid_snake_case_names(self, invalid_snake_case_names):
        for name in invalid_snake_case_names:
            with pytest.raises(ValidationError):
                self.cur_name = name
                self.adapter.validate_python(name)
