from typing import Annotated, Protocol, runtime_checkable, Any, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from utils.types import DotSeparatedSnakeCaseNameField


class Event[EventDataType = Any](BaseModel):
    # enable data to be any valid python object
    model_config = ConfigDict(arbitrary_types_allowed=True)

    sender: DotSeparatedSnakeCaseNameField | None = None
    """Sender of this event, default to `None`"""

    event_name: DotSeparatedSnakeCaseNameField
    """Name of this event, determine what handlers will be triggered"""

    data: EventDataType
    """Data passed to the handlers of this event"""


T = TypeVar("T", covariant=True)


@runtime_checkable
class EventHandler(Protocol[T]):
    registrant: str
    """
    Dot-separated snake-case name for entity who register this handler.
    
    E.g.: `rrss.sys`
    """

    def handler(data: T) -> Any: ...

    """Actual handler method to be called when event received"""
