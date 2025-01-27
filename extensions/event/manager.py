from typing import Any
from loguru import logger as _logger
from pydantic import BaseModel
from asyncer import create_task_group

from .types import Event, EventHandler
from . import errors as event_errors
from utils.types import RRSSEntityIdField, RRSSEntityIdKeyDict
from utils.asyncers import ensure_asyncify


class _SingleEventMgr[EventDataType](BaseModel):
    name: RRSSEntityIdField
    """Name of the event this `SingleEventManager` instance should process"""

    handler_dict: RRSSEntityIdKeyDict[list[EventHandler[EventDataType]]] = (
        RRSSEntityIdKeyDict()
    )
    """
    Dictionary to store handlers of this event
    
    - key: Registrant EntityId of this handler
    - value: `EventHandlerModel` object
    """

    def __init__(self, name: str):
        self.name = name

    def add(self, handler: EventHandler[EventDataType]) -> None:
        """Add a new handler to this single event"""
        # set default, then get the list of handlers of this registrant
        self.handler_dict.setdefault(handler.registrant, list())
        handler_list = self.handler_dict[handler.registrant]

        # try add handlers
        handler_list.append(handler)

        # check identifier duplication
        handler_identifier_list = [
            h.identifier for h in self.handler_dict[handler.registrant]
        ]
        # rollback & raise if duplicated
        if len(set(handler_identifier_list)) < len(handler_identifier_list):
            handler_list.pop()
            raise event_errors.DuplicatedHandlerID(
                duplicated_identifier=handler.identifier
            )

    def has(
        self,
        registrant: RRSSEntityIdField,
        identifier: RRSSEntityIdField | None = None,
    ) -> bool:
        """
        Check if a handler with certain registrant/identifier is already added

        If `identifier` is None, only check if `registrant` exists
        """

        if self.handler_dict.get(registrant, None) is None:
            return False

        if identifier is not None:
            handler_list = self.handler_dict[registrant]
            for handler in handler_list:
                if handler.identifier == identifier:
                    return True
            return False
        else:
            return True

    def handlers(self):
        """
        Yield all handlers models added to this event

        Examples:

        ```
        mgr: _SingleEventMgr
        for handler in mgr.handlers():
            # do sth
        ```
        """
        for registrant, handler_list in self.handler_dict.items():
            for handler in handler_list:
                yield handler

    async def emit(self, data: EventDataType) -> None:
        _logger.info(f"Emit event: {self.name}")

        async with create_task_group() as task_group:
            for handler_model in self.handlers():
                task_group.soonify(ensure_asyncify(handler_model.handler))(data)
                _logger.debug(f"Handler added to task: {handler_model}")

    def remove(
        self, registrant: RRSSEntityIdField, identifier: RRSSEntityIdField
    ) -> EventHandler[EventDataType]:
        """Remove an existing handler by registrant and identifier"""
        # registrant not exists
        try:
            handler_list_of_registrant = self.handler_dict[registrant]
        except KeyError as e:
            raise event_errors.HandlerNotFound(
                registrant=registrant, identifier=identifier
            )

        # remove based on identifier
        for i in range(len(handler_list_of_registrant)):
            cur_handler = handler_list_of_registrant[i]

            # found handler to be removed
            if cur_handler.identifier == identifier:
                ret = handler_list_of_registrant.pop(i)

                # if no handler of this registrant, remove key
                if len(handler_list_of_registrant) == 0:
                    del self.handler_dict[registrant]

                return ret

        raise event_errors.HandlerNotFound(registrant=registrant, identifier=identifier)


class EventManager:
    event_handler_mgr_dict: dict[str, _SingleEventMgr]

    # TODO


_event_manager_instance = EventManager()


def get_instance():
    return _event_manager_instance


def restart_manager():
    global _event_manager_instance
    _logger.debug("Restart RRSS event manager...")
    _event_manager_instance = EventManager()
    _logger.info("RRSS event manager has been restarted")
