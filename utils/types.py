from typing import Annotated, Dict, Any, TypeVar
from pydantic import Field, RootModel, validate_call

type RRSSEntityIdField = Annotated[str, Field(pattern=r"^([a-z_]+?)(\.[a-z_]+?)*$")]
"""
Dot-separated snake-case variable name format. 

E.g.: `rrss.sys.plug.rate_limiter`
"""


class DottedSnakeCaseKeyDict(RootModel):
    root: dict[RRSSEntityIdField, Any] = dict()

    def __iter__(self):
        return self.root.__iter__()

    @validate_call
    def __getitem__(self, key: RRSSEntityIdField):
        return self.root.__getitem__(key)

    @validate_call
    def __setitem__(self, key: RRSSEntityIdField, value: Any):
        self.root.__setitem__(key, value)
