from pydantic import BaseModel

from exceptions.general import RRSSBaseError
from extensions.event.types import EventHandler

from extensions.reg_mgr import errors as regmgr_errs
from extensions.reg_mgr import types as regmgr_types


class RRSSEventSystemError(RRSSBaseError):
    pass


class HandlerNotFound(regmgr_errs.RRSSRegistryDataNotFound, RRSSEventSystemError):
    def __init__(self, title="event_handler_not_found"):
        super().__init__(title)


class DuplicatedHandler(regmgr_errs.RRSSDuplicatedRegistryData, RRSSEventSystemError):

    def __init__(
        self,
        title="duplicated_event_handler",
    ):
        super().__init__(title)


class EventNotRegistered(regmgr_errs.RRSSRegistryNotFound, RRSSEventSystemError):
    """
    Raise when trying to:
    - Add a handler with `registry_id` that not exists
    - Emit an event with non-exists event name
    """

    def __init__(self, title="event_not_found"):
        super().__init__(title)


class DuplicatedEvent(regmgr_errs.RRSSDuplicatedRegistry, RRSSEventSystemError):
    def __init__(self, title="duplicated_event"):
        super().__init__(title)


_event_system_reg_mgr_custom_exceptions_config_dict: (
    regmgr_types.RegistryManagerCustomErrorConfig
) = {
    "registry_data_not_found": HandlerNotFound,
    "duplicated_registry_data": DuplicatedHandler,
    "registry_not_found": EventNotRegistered,
    "duplicated_registry": DuplicatedEvent,
}
