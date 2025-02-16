from typing import Protocol, Iterable, ClassVar, runtime_checkable, override, TypedDict
from abc import abstractmethod

from pydantic import BaseModel, validate_call, computed_field, ConfigDict

from utils import types as util_types

from . import errors as regmgr_errs


class RegisterableData(BaseModel):
    """Base class of registerable data"""

    model_config = ConfigDict(from_attributes=True)

    __reg_mgr_type_name__: ClassVar[str] = "Registerable"
    """
    A human-readable name representing the type of this class, 
    typically **used in the `__repr__()` method for descriptive output**.

    This name is often **contextualized based on the specific system or framework utilizing the registry manager**. 
    For instance, the RRSS event system is built upon this `reg_mgr` package, in which, `EventHandler` 
    (which inherits from `RegisterableData`) define this as `__reg_mgr_type_name__ = "RRSSEventHandler"` 
    to reflect its role within that system.
    """

    registry_id: util_types.RID
    """
    The unique identifier for the registry within a registry group,
    indicating which registry this item belongs to.
    
    One usage of this field is for `RegistryGroupManager.add_data()` to know 
    which registry this registerable data belongs to.
    """

    registrant: util_types.RID
    identifier: util_types.RID

    def __repr__(self):
        return f"<{self.__reg_mgr_type_name__}[{self.registry_id}] reg={self.registrant} id={self.identifier}>"


class PriorityRegisterableData(RegisterableData):
    """Registerable data with priority"""

    priority: float = 0
    """
    Priority of this registerable data.
    Higher number represents higher priority.
    """


class RegistryManagerCustomErrorConfig(TypedDict):
    registry_not_found: type[regmgr_errs.RRSSRegistryNotFound]
    duplicated_registry: type[regmgr_errs.RRSSDuplicatedRegistry]
    registry_data_not_found: type[regmgr_errs.RRSSRegistryDataNotFound]
    duplicated_registry_data: type[regmgr_errs.RRSSDuplicatedRegistryData]


_default_reg_mgr_custom_error_config_dict: RegistryManagerCustomErrorConfig = {
    "registry_not_found": regmgr_errs.RRSSRegistryNotFound,
    "duplicated_registry": regmgr_errs.RRSSDuplicatedRegistry,
    "registry_data_not_found": regmgr_errs.RRSSRegistryDataNotFound,
    "duplicated_registry_data": regmgr_errs.RRSSDuplicatedRegistryData,
}


class RegistryManager[DType: RegisterableData](Protocol):
    """
    Protocol of RegistryManager classes, all registry manager should implement this protocol
    in order to be used by `RegistryGroupManager`

    RegistryManager is responsible for managing a collection of `RegisterableData`
    and provide the corresponding methods to manage these data items.

    Used by `RegistryGroupManager`
    """

    __reg_mgr_custom_exceptions__: RegistryManagerCustomErrorConfig
    """
    Store the custom exceptions type info that will be raised when registry-related error occurred
    
    Default exceptions are in `.errors` module
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        registry_id: util_types.RID,
        custom_exceptions: RegistryManagerCustomErrorConfig | None = None,
    ):
        self.registry_id = registry_id

        # init custom exception config
        try:
            self.__reg_mgr_custom_exceptions__
        except:
            self.__reg_mgr_custom_exceptions__ = (
                _default_reg_mgr_custom_error_config_dict
            )
        if custom_exceptions is not None:
            self.__reg_mgr_custom_exceptions__ = custom_exceptions

    registry_id: util_types.RID
    """ID of this registry manager, usually used by `RegistryGroupManager`"""

    @abstractmethod
    def add(self, data: DType) -> None:
        """
        Add a new item to this registry

        Raises:
            `RRSSDuplicatedRegistry`
        """
        ...

    @abstractmethod
    def remove(
        self,
        registrant: util_types.RID,
        identifier: util_types.RID | None,
    ) -> None:
        """
        Remove an item from this registry.

        If `identifier` is `None`, remove all items with certain `registrant`

        Raises:
            `RRSSRegistryNotFound`
        """
        ...

    @abstractmethod
    def list(self) -> Iterable[DType]:
        """
        Returns an `Iterable` of all items of this registry
        """
        ...

    def get(self, registrant: util_types.RID, identifier: util_types.RID) -> DType:
        """
        Get an item from this registry by `registrant` and `identifier`
        """
        for reg in self:
            if reg.registrant == registrant and reg.identifier == identifier:
                return reg
        raise regmgr_errs.RRSSRegistryDataNotFound().register_info(
            registrant=registrant, identifier=identifier
        )

    def has(
        self, registrant: util_types.RID, identifier: util_types.RID | None
    ) -> bool:
        """
        Check if a certain `registrant` and `identifier` pair is exists.

        If `identifier` is `None`, check if there's any item with specified `registrant`
        """
        for reg in self:
            if not reg.registrant == registrant:
                continue
            if identifier is None:
                return True
            if reg.identifier == identifier:
                return True

        return False

    def __iter__(self):
        return iter(self.list())

    def __len__(self) -> int:
        return len(self)


class ListRegistryManager[DType: RegisterableData](RegistryManager[DType]):

    registries: list[DType]

    @validate_call
    def __init__(self, registry_id, custom_exceptions=None):
        super().__init__(registry_id=registry_id, custom_exceptions=custom_exceptions)
        self.registries = list()

    @override
    def add(self, data):
        if self.has(data.registrant, data.identifier):
            raise self.__reg_mgr_custom_exceptions__[
                "duplicated_registry_data"
            ]().register_info(registrant=data.registrant, identifier=data.identifier)
        self.registries.append(data)

    @override
    def remove(self, registrant, identifier):

        removed = False

        cur_idx = 0
        while cur_idx < len(self.registries):
            cur_reg = self.registries[cur_idx]

            # match registrant
            if cur_reg.registrant == registrant:
                # no identifier specified, remove
                if identifier is None:
                    self.registries.pop(cur_idx)
                    removed = True
                # identifier matched, remove
                elif cur_reg.identifier == identifier:
                    self.registries.pop(cur_idx)
                    removed = True
                else:
                    cur_idx += 1
            else:
                cur_idx += 1

        if not removed:
            raise self.__reg_mgr_custom_exceptions__[
                "registry_data_not_found"
            ]().register_info(registrant=registrant, identifier=identifier)

    @override
    def list(self):
        return self.registries


class PriorityListRegistryManager[DType: PriorityRegisterableData](
    ListRegistryManager[DType]
):
    @override
    def add(self, data: DType):
        super().add(data=data)

        # sort by priority
        self.registries.sort(key=lambda x: x.priority, reverse=True)


class RegistryGroupManager[T_RegMgr: RegistryManager]:
    registries_dict: dict[util_types.RID, T_RegMgr]
    """
    Dict to store a group of registry manager
    
    - Key: Name of the registry
    - Val: A `RegistryManager` instance
    """

    _reg_mgr_cls: type[T_RegMgr]
    """
    Class type object used to create new `RegistryManager` instance
    when `add_registry()` get called.
    
    Different types of `RegistryManager` in one group manager is 
    currently not supported.
    """

    __reg_mgr_custom_exceptions__: RegistryManagerCustomErrorConfig
    """
    Store the custom exceptions type info that will be raised when registry-related error occurred
    
    Default exceptions are in `.errors` module
    """

    def __init__(
        self,
        reg_mgr_cls: type[T_RegMgr],
        custom_exceptions: RegistryManagerCustomErrorConfig | None = None,
    ):
        super().__init__()
        self._reg_mgr_cls = reg_mgr_cls
        self.registries_dict = dict()

        # init custom error config
        try:
            self.__reg_mgr_custom_exceptions__
        except:
            self.__reg_mgr_custom_exceptions__ = (
                _default_reg_mgr_custom_error_config_dict
            )
        if custom_exceptions is not None:
            self.__reg_mgr_custom_exceptions__ = custom_exceptions

    @validate_call
    def add_registry(self, registry_id: util_types.RID):
        """
        Add a new registry with specified registry id.
        Instance is auto-generated using the specified `reg_mgr_cls` class type.

        Note:
            The custom exceptions config will be passed to the newly created registry.

        Raises:
            `RRSSDuplicatedRegistry`
        """
        if self.has_registry(registry_id=registry_id):
            raise self.__reg_mgr_custom_exceptions__[
                "duplicated_registry"
            ]().registry_info(registry_id=registry_id)

        self.registries_dict[registry_id] = self._reg_mgr_cls(
            registry_id=registry_id,
            custom_exceptions=self.__reg_mgr_custom_exceptions__,
        )

    def add_registry_instance(self, registry: T_RegMgr) -> None:
        """
        Directly add an registry manager instance to this group manager.
        """
        if self.has_registry(registry_id=registry.registry_id):
            raise self.__reg_mgr_custom_exceptions__[
                "duplicated_registry"
            ]().registry_info(registry_id=registry.registry_id)

        self.registries_dict[registry.registry_id] = registry

    def has_registry(self, registry_id: util_types.RID):
        try:
            self._try_get_registry(registry_id=registry_id)
            return True
        except regmgr_errs.RRSSRegistryNotFound:
            return False

    @validate_call
    def remove_registry(self, registry_id: util_types.RID):
        """
        Remove a registry from this registry group.

        Note that this method will NOT check if there's still items in the registry
        before removing it.
        """
        self._try_get_registry(registry_id=registry_id)
        self.registries_dict.pop(registry_id)

    def _try_get_registry(self, registry_id: util_types.RID):
        try:
            return self.registries_dict[registry_id]
        except KeyError:
            raise self.__reg_mgr_custom_exceptions__[
                "registry_not_found"
            ]().registry_info(registry_id=registry_id)

    def registries(self):
        """Iterate over all registries managed by this group manager"""
        yield from self.registries_dict.values()

    def add_data(self, data: RegisterableData):
        """
        Add new data to one of the registry in this group manager.
        """
        reg = self._try_get_registry(data.registry_id)
        reg.add(data=data)

    def remove_data(
        self,
        registrant: util_types.RID,
        identifier: util_types.RID | None,
    ):
        for registry_mgr in self.registries():
            try:
                registry_mgr.remove(registrant=registrant, identifier=identifier)
            except regmgr_errs.RRSSRegistryDataNotFound:
                pass

    def get_data(self, data: RegisterableData):
        reg = self._try_get_registry(data.registry_id)
        return reg.get(data.registrant, data.identifier)

    def has_data(self, data: RegisterableData):
        reg = self._try_get_registry(data.registry_id)
        return reg.has(data.registrant, data.identifier)

    def list_data(self, registry_id: util_types.RID):
        reg = self._try_get_registry(registry_id)
        return reg.list()

    def list_all_data(self):
        for reg in self.registries_dict.values():
            yield from reg.list()
