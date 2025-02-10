from typing import Awaitable

from pydantic import BaseModel
from loguru import logger as _logger

from utils import types as util_types


class PipelineNode[DataType](BaseModel):
    pipeline: util_types.RRSSEntityIdField
    """Name of the pipeline that this node should belong to"""

    registrant: util_types.RRSSEntityIdField
    """Registrant of this pipeline node"""

    identifier: util_types.RRSSEntityIdField
    "Unique identifier of this pipeline node"

    def process(self, data: DataType) -> DataType | Awaitable[DataType]:
        _logger.warning(
            "Default pipeline process() function has been called, "
            "make sure all process() methods of pipeline node "
            "has been properly overriden"
        )
        return data
