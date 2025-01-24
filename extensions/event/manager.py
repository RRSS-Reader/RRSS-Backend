from loguru import logger as _logger
from pydantic import BaseModel, validate_call
from .types import Event, EventHandlerModel
from utils.types import RRSSEntityIdField


class _SingleEventMgr(BaseModel):
    name: RRSSEntityIdField
    """Name of the event this SingleEventManager should process"""

    handler_list: list[EventHandlerModel] = []
    """Dictionary to store handlers of this event"""

    def __init__(self, name: str):
        self.name = name

    def add(self, handler: EventHandlerModel):
        self.handler_list.append(handler)

    def remove(
        self,
        registrant: RRSSEntityIdField,
        identifier: RRSSEntityIdField,
    ):
        # TODO
        pass


class EventManager:
    event_handler_mgr_dict: dict[str, _SingleEventMgr]


_event_manager_instance = EventManager()


def get_instance():
    return _event_manager_instance


def restart_manager():
    global _event_manager_instance
    _logger.debug("Restart RRSS event manager...")
    _event_manager_instance = EventManager()
    _logger.info("RRSS event manager has been restarted")
