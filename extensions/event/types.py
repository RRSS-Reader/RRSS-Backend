from typing import Annotated, Protocol, runtime_checkable, Any, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from utils.types import RRSSEntityIdField


class Event[EventDataType = Any](BaseModel):
    # enable data to be any valid python object
    model_config = ConfigDict(arbitrary_types_allowed=True)

    sender: RRSSEntityIdField | None = None
    """Sender of this event, default to `None`"""

    event_name: RRSSEntityIdField
    """Name of this event, determine what handlers will be triggered"""

    data: EventDataType
    """Data passed to the handlers of this event"""


HandlerDataType = TypeVar("HandlerDataType", covariant=True, default=Any)


class EventHandlerModel[HandlerDataType](BaseModel):
    # allow validate from Python object attrs
    model_config = ConfigDict(from_attributes=True)

    registrant: RRSSEntityIdField
    """
    Dot-separated snake-case name for entity who register this handler.
    
    E.g.: `rrss.sys`
    """

    identifier: RRSSEntityIdField
    """
    Identifier of this event handler, should be unique across all handlers 
    registered by the same registrant.
    """

    def handler(data: HandlerDataType) -> Any:
        """Actual handler method to be called when event received"""
        ...
