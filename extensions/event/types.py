from typing import Annotated, Protocol, Any, Generic
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
