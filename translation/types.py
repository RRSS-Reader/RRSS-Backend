from typing import Annotated
from importlib.resources.abc import Traversable

from pydantic import BaseModel, ConfigDict, Field
from utils.types import SnakeCaseField

LngCodeField = Annotated[str, Field(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")]


class TranslationText(BaseModel):
    """
    Pydantic class used to define a translatable text in RRSS translation system.

    Always use this data model when need to pass a string that will be displayed in
    frontend user interface.
    """

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    ns: SnakeCaseField
    """Namespace of this translation key"""

    key: SnakeCaseField
    """i18next translation key"""

    t: bool = True
    """
    If the key should be translated using i18next, default to `True`
    
    When set to `False`, the `key` is expected to directly used as display text
    """


class TransResourceMetaData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    lng: LngCodeField
    ns: SnakeCaseField
    location: Traversable

    def __hash__(self):
        """
        Hash method override, ensure two metadata object has the same hash value
        if both their `lng` and `ns` is the same.
        """
        return hash((self.lng, self.ns))

    def __repr__(self):
        return f"<I18nResMeta lng={self.lng!r} ns={self.ns!r}>"
