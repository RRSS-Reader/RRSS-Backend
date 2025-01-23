from typing import Annotated
from pydantic import Field

type DotSeparatedSnakeCaseNameField = Annotated[
    str, Field(pattern=r"^([a-z_]+?)(\.[a-z_]+?)*$")
]
"""
Dot-separated snake-case variable name format. 

E.g.: `rrss.sys.plug.rate_limiter`
"""
