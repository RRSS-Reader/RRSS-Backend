from typing import Protocol, Iterable, runtime_checkable, override
from abc import abstractmethod

from pydantic import BaseModel, validate_call

from utils import types as util_types

from . import errors as regmgr_errs


@runtime_checkable
class RegisterableData(Protocol):
    """Protocol of registerable data"""

    registry_id: util_types.RID
    """
    ID of the registry in the registry group, which registry this item belongs to.
    
    E.g.:
        In event system, `registry_id` could be considered the name of the event.
    """

    registrant: util_types.RID
    identifier: util_types.RID


class PriorityRegisterableData(RegisterableData, Protocol):
    """Registerable data with priority"""

    priority: float = 0
    """
    Priority of this registerable data.
    Higher number represents higher priority.
    """


class RegistryManager[DType: RegisterableData](Protocol):
    """
    Protocol of RegistryManager classes

    RegistryManager is responsible for managing a collection of `RegisterableData`
    and provide the corresponding methods to manage these data items.

    Used by `RegistryGroupManager`
    """

    @validate_call
    def __init__(self, registry_id: util_types.RID):
        self.registry_id = registry_id

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
        raise regmgr_errs.RRSSRegistryNotFound

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
    def __init__(self, group_name: util_types.RRSSEntityIdField):
        self.registry_id = group_name

    @override
    def add(self, data):
        if self.has(data.registrant, data.identifier):
            raise regmgr_errs.RRSSDuplicatedRegistry
        self.registries.append(data)

    @override
    def remove(self, registrant, identifier):
        for i in range(len(self.registries)):
            cur_reg = self.registries[i]

            # match registrant
            if cur_reg.registrant == registrant:
                # no identifier specified, remove
                if identifier is None:
                    self.registries.pop(i)
                    i -= 1
                # identifier matched, remove
                elif cur_reg.identifier == identifier:
                    self.registries.pop(i)
                    i -= 1

        raise regmgr_errs.RRSSRegistryNotFound

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


class RegistryGroupManager[T_RegMgr: RegistryManager](Protocol):
    group_manager_dict: dict[util_types.RID, RegistryManager]
    """
    Dict to store a group of registry manager
    
    - Key: Name of the registry
    - Val: A `RegistryManager` instance
    """
    reg_mgr_cls: type[RegistryManager]

    def __init__(self, reg_mgr_cls: type[RegistryManager]):
        super().__init__()
        self.reg_mgr_cls = reg_mgr_cls

    def add_registry(self, registry_id: util_types.RID):
        if registry_id in self.group_manager_dict:
            raise regmgr_errs.RRSSDuplicatedRegGroupName

        self.group_manager_dict[registry_id] = self.reg_mgr_cls(registry_id=registry_id)

    def has_registry(self, registry_id: util_types.RID):
        try:
            self._try_get_registry(registry_id=registry_id)
            return True
        except regmgr_errs.RRSSRegistryNotFound:
            return False

    def remove_registry(self, registry_id: util_types.RID):
        """
        Remove a registry from this registry group.

        Note that this method will NOT check if there's still items in the registry
        before removing it.
        """
        self._try_get_registry(registry_id=registry_id)
        self.group_manager_dict.pop(registry_id)

    def _try_get_registry(self, registry_id: util_types.RID):
        try:
            return self.group_manager_dict[registry_id]
        except KeyError:
            raise regmgr_errs.RRSSRegistryNotFound().registry_info(
                registry_id=registry_id
            )

    def add_data(self, data: RegisterableData):
        reg = self._try_get_registry(data.registry_id)
        reg.add(data=data)

    def remove_data(self, data: RegisterableData):
        reg = self._try_get_registry(data.registry_id)
        reg.remove(data.registrant, data.identifier)

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
        for reg in self.group_manager_dict.values():
            yield from reg.list()
