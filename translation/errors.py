from exceptions.general import RRSSBaseError

from . import types as trans_type
from .manager import _TransResourceMetaData


class TranslationSystemError(RRSSBaseError):
    pass


class DuplicatedTranslationNamespace(TranslationSystemError):
    def __init__(
        self,
        title="duplicated_translation_namespace",
        resource: _TransResourceMetaData | None = None,
    ):
        super().__init__(title)

        if resource is not None:
            self.resource = resource


class TranslationResourceNotFound(TranslationSystemError):
    def __init__(
        self,
        title="translation_resource_not_found",
        lng: str | None = None,
        ns: str | None = None,
    ):
        super().__init__(title)
        self.lng = lng
        self.ns = ns
