from typing import Annotated, Protocol, runtime_checkable, Any, ClassVar, override
from abc import abstractmethod
from pydantic import BaseModel, Field, ConfigDict
from utils.types import RID

from extensions import reg_mgr


class Event[EventDataType](BaseModel):
    # enable data to be any valid python object
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    sender: RID | None = None
    """Sender of this event, default to `None`"""

    event_name: RID
    """Name of this event, determine what handlers will be triggered"""

    data: EventDataType
    """Data passed to the handlers of this event"""


class EventHandler[HandlerDataType](reg_mgr.RegisterableData):
    __reg_mgr_type_name__ = "EventHandler"

    event_name: RID

    @property
    def registry_id(self):
        return self.event_name

    def handler(self, event: Event[HandlerDataType]) -> Any:
        """Actual handler method to be called when event received"""
        return None
