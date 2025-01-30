from typing import Annotated, Dict, Any, TypeVar, override
from pydantic import Field, ConfigDict, TypeAdapter, validate_call

SnakeCaseField = Annotated[str, Field(pattern=r"^[a-z0-9_]+?$")]

RRSSEntityIdField = Annotated[str, Field(pattern=r"^([a-z0-9_]+?)(\.[a-z0-9_]+?)*$")]
"""
Dot-separated snake-case variable name format. 

E.g.: `rrss.sys.plug.rate_limiter`
"""


class RRSSEntityIdKeyDict[VT](dict[RRSSEntityIdField, VT]):
    """
    Custom dict that limit key type to `RRSSEntityId` format.

    Provide runtime check for keys type and static type check for value type `VT`
    """

    # type adapter used to provide runtime check of dict key
    type_adapter = TypeAdapter(
        dict[RRSSEntityIdField, VT], config=ConfigDict(arbitrary_types_allowed=True)
    )

    @override
    @validate_call
    def __setitem__(self, key: RRSSEntityIdField, value: VT) -> None:
        super().__setitem__(key, value)

    @override
    def validate_dict_key(self):
        self.type_adapter.validate_python(self)
