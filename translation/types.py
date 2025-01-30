from pydantic import BaseModel, ConfigDict

from utils.types import SnakeCaseField


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
