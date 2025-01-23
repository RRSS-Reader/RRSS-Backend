import pytest
from pydantic import ValidationError

from utils import types


class TestDottedSnakeCaseKeyDict:
    def test_invalid_key(self, invalid_dsk_names):
        typed_dict = types.DottedSnakeCaseKeyDict()
        for name in invalid_dsk_names:
            with pytest.raises(ValidationError):
                typed_dict[name] = "some_value"
