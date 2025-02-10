from exceptions.general import RRSSBaseError


__all__ = ["RRSSRegistryNotFound"]


class RRSSRegMgrBaseError(RRSSBaseError):

    def register_info(
        self, registrant: str | None = None, identifier: str | None = None
    ):
        self.registrant = registrant
        self.identifier = identifier
        return self

    def registry_info(self, registry_id):
        self.registry_id = registry_id
        return self


class RRSSRegistryNotFound(RRSSRegMgrBaseError):
    """
    Raised when registry manager could not found corresponding data
    """

    def __init__(
        self,
        title="registry_not_found",
    ):
        super().__init__(title)


class RRSSDuplicatedRegistry(RRSSRegMgrBaseError):
    def __init__(self, title="registry_already_exists"):
        super().__init__(title)


class RRSSDuplicatedRegGroupName(RRSSRegMgrBaseError):
    def __init__(self, title="duplicated_reg_group_name"):
        super().__init__(title)
