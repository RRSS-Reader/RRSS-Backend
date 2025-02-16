from exceptions.general import RRSSBaseError


class RRSSRegMgrBaseError(RRSSBaseError):

    def register_info(
        self, registrant: str | None = None, identifier: str | None = None
    ):
        """
        Add info about registerable data, like `registrant` and `identifier`.
        """
        self.registrant = registrant
        self.identifier = identifier
        return self

    def registry_info(self, registry_id):
        """
        Add info about registry, like `registry_id`
        """
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


class RRSSRegistryDataNotFound(RRSSRegMgrBaseError):
    def __init__(self, title="registry_data_not_found"):
        super().__init__(title)


class RRSSDuplicatedRegistry(RRSSRegMgrBaseError):
    def __init__(self, title="duplicated_registry"):
        super().__init__(title)


class RRSSDuplicatedRegistryData(RRSSRegMgrBaseError):
    """
    Raise when trying to add two registries with same `registry_id`
    in a registry group manager.
    """

    def __init__(self, title="duplicated_registry_data"):
        super().__init__(title)
