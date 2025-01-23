from typing import Annotated, Any
from pydantic import Field, RootModel

type DotSeparatedSnakeCaseNameField = Annotated[
    str, Field(pattern=r"^([a-z_]+?)(\.[a-z_]+?)*$")
]
"""
Dot-separated snake-case variable name format. 

E.g.: `rrss.sys.plug.rate_limiter`
"""


class DottedSnakeCaseKeyDict[VT = Any](
    RootModel[dict[DotSeparatedSnakeCaseNameField, VT]]
):
    pass
