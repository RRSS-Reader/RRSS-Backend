from typing import Set, Collection
from importlib import resources as iptlib_res
from importlib.abc import Traversable, TraversableResources

from pydantic import BaseModel, ValidationError, Field, validate_call
from loguru import logger as _logger

from utils import types as util_types
from . import types as trans_types
from . import errors as trans_errs


class _TransResourceMetaData(BaseModel):
    lng: trans_types.LngCodeField
    ns: util_types.SnakeCaseField
    location: Traversable

    def __hash__(self):
        """
        Hash method override, ensure two metadata object has the same hash value
        if both their `lng` and `ns` is the same.
        """
        return hash((self.lng, self.ns))


# TODO: test needed
class _TranslationResourceManager:
    resources: dict[
        trans_types.LngCodeField,
        dict[util_types.SnakeCaseField, _TransResourceMetaData],
    ]

    def __init__(self):
        self.resources = dict()

    def register(self, resource: _TransResourceMetaData) -> None:
        """
        Register a new translation resource
        """
        lng_res_dict = self.resources.setdefault(resource.lng, dict())
        if resource.ns in lng_res_dict:
            raise trans_errs.DuplicatedTranslationNamespace(resource=resource)
        lng_res_dict[resource.ns] = resource

    @validate_call
    def _get_resource_metadata(
        self,
        lng: trans_types.LngCodeField,
        ns: trans_types.SnakeCaseField,
    ) -> _TransResourceMetaData:
        try:
            return self.resources[lng][ns]
        except KeyError as e:
            raise trans_errs.TranslationResourceNotFound(lng=lng, ns=ns)

    def get_resource_json(
        self, lng: trans_types.LngCodeField, ns: trans_types.SnakeCaseField
    ) -> str:
        """
        Return JSON content from translation resource file if exists

        Raises:
            `TranslationResourceNotFound`
        """
        res = self._get_resource_metadata(lng=lng, ns=ns)
        return res.location.read_text()

    def discover(
        self,
        anchor: iptlib_res.Anchor,
        add_to_res: bool = True,
    ) -> list[_TransResourceMetaData]:
        """
        Use `importlib.resource` to discover new translation resources

        Args:
            anchor:
                Determine where to discover the new resources, could be module type or
                a string represents a package/module location.

                Note that the resources should be directly located in the anchor package

            add_to_res:
                If `add_to_res == True`, try add the newly discovered resources to
                this manager, if failed, ignore corresponding resource
        """

        _logger.debug(f"Start discover translation resources with anchor: {anchor}")

        # store newly discovered translation resources
        discovered_resources: list[_TransResourceMetaData] = list()

        def process_lng_dir(lng_code: trans_types.LngCodeField, dir: Traversable):
            nonlocal discovered_resources

            for t in dir.iterdir():

                # not file, skip
                if not t.is_file():
                    continue

                # not json file, skip
                if not t.name.endswith(".json"):
                    continue

                namespace = t.name[:-6]

                # create new resources
                discovered_resources.append(
                    _TransResourceMetaData(lng=lng_code, ns=namespace, location=t)
                )

        # traverse
        for dir in iptlib_res.files(anchor=anchor).iterdir():

            if not dir.is_dir():
                continue

            # if it's a language code directory
            try:
                util_types.SnakeCaseValidator.validate_python(dir.name)
            except ValidationError as e:
                continue

            process_lng_dir(lng_code=dir.name, dir=dir)

        if add_to_res:
            for res in discovered_resources:
                try:
                    self.register(res)
                except trans_errs.DuplicatedTranslationNamespace as e:
                    _logger.debug(
                        "Duplicated translation namespace found in discovery process, "
                        "automatically skipped."
                    )
                    continue

        # TODO
        return discovered_resources


instance = _TranslationResourceManager()
