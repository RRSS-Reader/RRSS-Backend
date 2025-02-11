from typing import Any
from loguru import logger as _logger
from pydantic import BaseModel, ConfigDict, validate_call
from asyncer import create_task_group

from extensions.reg_mgr import RegistryGroupManager, ListRegistryManager

from .types import Event, EventHandler
from . import errors as event_errors
from utils import types as util_types
from utils.types import RRSSEntityIdField, RRSSEntityIdKeyDict, SnakeCaseField
from utils.asyncers import ensure_asyncify


class _SingleEventMgr[EventDataType](ListRegistryManager[EventHandler[EventDataType]]):

    event_name: RRSSEntityIdField
    """Name of the event this `SingleEventManager` instance should process"""

    @property
    def registty_id(self):
        return self.event_name

    async def emit(self, event: Event[EventDataType]) -> None:
        """
        Emit an event, execute all handlers managed by this _SingleEventMgr.

        About Handlers:
            Handlers could be sync or async function.
            Sync function handlers will first be converted into async function using `ensure_asyncify()`,
            then all handlers will be gathered into a task group and executed.

            About sync-to-async conversion, check out `ensure_asyncify()` function.
        """

        _logger.info(f"Emit event: {self.event_name!r}")

        async with create_task_group() as task_group:
            for handler_model in self:
                task_group.soonify(ensure_asyncify(handler_model.handler))(event=event)
                _logger.debug(f"Handler added to task: {handler_model}")

        _logger.info(f"Event emit finished: {self.event_name!r}")


class EventManager(RegistryGroupManager[_SingleEventMgr]):

    def __init__(self):
        super().__init__(reg_mgr_cls=_SingleEventMgr)

    @validate_call
    async def emit(self, event: Event[Any]):
        """
        Emit an event which is managed by this EventManager.

        Args:
            event:
                The event object. This object is used to:
                1. Determine which event will be emitted.
                2. Be passed to handlers as the only parameter.

                This event object will be validated using Pydantic.

        Raises:
            EventNotRegistered: Could not found corresponding event name.
            ValidationError: Event validation failed.
        """
        single_event_mgr = self._try_get_registry(registry_id=event.event_name)
        await single_event_mgr.emit(event)


instance = EventManager()


def get_instance():
    """
    Get the singleton instance of event manager
    """
    return instance


def restart_manager():
    global instance
    _logger.debug("Restart RRSS event manager...")
    instance = EventManager()
    _logger.info("RRSS event manager has been restarted")
