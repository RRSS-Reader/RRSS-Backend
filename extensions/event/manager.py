from typing import Any
from loguru import logger as _logger
from pydantic import BaseModel, ConfigDict, validate_call
from asyncer import create_task_group

from .types import Event, EventHandler
from . import errors as event_errors
from utils.types import RRSSEntityIdField, RRSSEntityIdKeyDict, SnakeCaseField
from utils.asyncers import ensure_asyncify


class _SingleEventMgr[EventDataType](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
        super().__init__(name=name)
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

    async def emit(self, event: Event[EventDataType]) -> None:
        """
        Emit an event, execute all handlers managed by this _SingleEventMgr.

        About Handlers:
            Handlers could be sync or async function.
            Sync function handlers will first be converted into async function using `ensure_asyncify()`,
            then all handlers will be gathered into a task group and executed.

            About sync-to-async conversion, check out `ensure_asyncify()` function.
        """

        _logger.info(f"Emit event: {self.name!r}")

        async with create_task_group() as task_group:
            for handler_model in self.handlers():
                task_group.soonify(ensure_asyncify(handler_model.handler))(event=event)
                _logger.debug(f"Handler added to task: {handler_model}")

        _logger.info(f"Event emit finished: {self.name!r}")

    def remove(
        self,
        registrant: RRSSEntityIdField,
        identifier: RRSSEntityIdField | None,
    ) -> EventHandler[EventDataType]:
        """
        Remove an existing handler by registrant and identifier

        Args:
            registrant:
                Registrant ID
            identifier:
                Identifier ID, if `None`, will try to remove all handlers registered by the `registrant`
        """
        # registrant not exists
        try:
            handler_list_of_registrant = self.handler_dict[registrant]
        except KeyError as e:
            raise event_errors.HandlerNotFound(
                registrant=registrant, identifier=identifier
            )

        # remove all
        if identifier is None:
            handler_list_of_registrant.clear()

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
    event_handler_mgr_dict: RRSSEntityIdKeyDict[_SingleEventMgr[Any]]
    """
    Store all _SingleEventMgr instance used by this manager.
    
    Key is the name of the event, should be a valid RRSS entity ID.
    Value is the corresponding single event manager.
    """

    def __init__(self):
        self.event_handler_mgr_dict = RRSSEntityIdKeyDict()

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
        single_event_mgr = self._try_get_single_mgr(event_name=event.event_name)
        await single_event_mgr.emit(event)

    @validate_call
    def add_event(self, event_name: RRSSEntityIdField):
        """
        Add a new event to this manager.

        Handlers could only be added to an event after this event been added using this method.

        Raises:
            ValidationError
        """
        self.event_handler_mgr_dict.setdefault(event_name, _SingleEventMgr(event_name))

    def has_event(self, event_name: str) -> bool:
        """
        Check if an event is added to this manager
        """
        return event_name in self.event_handler_mgr_dict

    @validate_call
    def add_handler(self, handler: EventHandler):
        """Add a new handler"""
        single_event_mgr = self._try_get_single_mgr(handler.event_name)
        single_event_mgr.add(handler=handler)

        _logger.debug(f"New handler added: {handler}")

    def has_handler(self, handler: EventHandler):
        pass

    @validate_call
    def remove_handler(self, handler: EventHandler):
        """
        Remove a single handler

        Note that it's not required to pass the identical `handler` object which used when adding,
        this method will use the attributes of received `handler` to find the handler that
        need to be remove.

        Example:

            handler: EventHandler
            mgr.add_event(handler.event_name)
            mgr.add_handler(handler=handler)
            mgr.remove_handler(
                handler=EventHandler(
                    event_name=handler.event_name,
                    registrant=handler.registrant,
                    identifier=registrant.identifier,
                )
            )
        """
        single_mgr = self._try_get_single_mgr(event_name=handler.event_name)
        single_mgr.remove(registrant=handler.registrant, identifier=handler.identifier)

    @validate_call
    def remove_all_by_registrant(self, registrant: RRSSEntityIdField):
        """Remove all handlers with specific registrant"""
        for single_mgr in self._single_managers():
            try:
                single_mgr.remove(registrant=registrant, identifier=None)
            except event_errors.HandlerNotFound:
                continue

    def _try_get_single_mgr(self, event_name: RRSSEntityIdField):
        """
        Check event existence and return corresponding `_SingleEventMgr` if exists
        """
        if not self.has_event(event_name=event_name):
            raise event_errors.EventNotRegistered(event_name=event_name)

        return self.event_handler_mgr_dict[event_name]

    def _single_managers(self):
        for mgr in self.event_handler_mgr_dict.values():
            yield mgr

    # TODO: Test needed


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
