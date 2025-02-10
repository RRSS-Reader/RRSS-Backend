from typing import Protocol, Iterable, runtime_checkable, override
from abc import abstractmethod

from pydantic import BaseModel, validate_call

from utils import types as util_types

from . import errors as regmgr_errs


@runtime_checkable
class RegisterableData(Protocol):
    """Protocol of registerable data"""

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

    Usually used by RegistryGroupManager
    """

    group_name: util_types.RID
    """Group name of this `RegistryManager`"""

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

    def has(self, registrant: util_types.RID, identifier: util_types.RID) -> bool:
        """
        Check if a certain `registrant` and `identifier` pair is exists
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
        self.group_name = group_name

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


class RegistryGroupManager(Protocol):
    reg_mgr_dict: dict[util_types.RID, ListRegistryManager]
