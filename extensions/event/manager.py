from loguru import logger as _logger
from . import types


class _SingleEventMgr:
    name: str
    handlers_dict: dict[]

    def __init__(self, name: str):
        self.name = name


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
