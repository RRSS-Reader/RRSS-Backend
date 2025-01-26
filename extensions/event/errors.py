from pydantic import BaseModel

from exceptions.general import RRSSBaseError
from extensions.event.types import EventHandler


class RRSSEventSystemError(RRSSBaseError):
    pass


class HandlerNotFound(RRSSEventSystemError):
    registrant: str | None = None
    identifier: str | None = None

    def __init__(
        self,
        title="handler_not_found",
        registrant: str | None = None,
        identifier: str | None = None,
    ):
        super().__init__(title)
        self.registrant = registrant
        self.identifier = identifier


class DuplicatedHandlerID(RRSSEventSystemError):
    duplicated_identifier: str | None = None

    def __init__(
        self,
        title="duplicated_handler_identifier",
        duplicated_identifier: str | None = None,
    ):
        super().__init__(title)
        self.duplicated_identifier = duplicated_identifier
