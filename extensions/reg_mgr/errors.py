from exceptions.general import RRSSBaseError


__all__ = ["RRSSRegistryNotFound"]


class RRSSRegMgrBaseError(RRSSBaseError):
    pass


class RRSSRegistryNotFound(RRSSRegMgrBaseError):
    """
    Raised when registry manager could not found corresponding data
    """

    def __init__(self, title="registry_not_found"):
        super().__init__(title)


class RRSSDuplicatedRegistry(RRSSRegMgrBaseError):
    def __init__(self, title="registry_already_exists"):
        super().__init__(title)
