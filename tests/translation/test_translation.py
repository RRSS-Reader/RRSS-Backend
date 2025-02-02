import pytest
from importlib import resources as iptlib_res

from pydantic import ValidationError

from translation import types as trans_types
from translation import errors as trans_errs
from translation import manager

ins = manager.instance
Meta = trans_types.TransResourceMetaData


class TestTranslationMetaData:
    def test_invalid_snake_case_name(self, invalid_snake_case_names):
        for name in invalid_snake_case_names:
            with pytest.raises(ValidationError):
                Meta(lng="en-US", ns=name, location=iptlib_res.files())

    def test_valid_snake_case_name(self, valid_snake_case_names):
        for name in valid_snake_case_names:
            Meta(lng="en-US", ns=name, location=iptlib_res.files())

    def test_invalid_lng_code(self, invalid_lng_code):
        for lng in invalid_lng_code:
            with pytest.raises(ValidationError):
                Meta(lng=lng, ns="valid_namespace", location=iptlib_res.files())

    def test_valid_lng_code(self, valid_lng_code):
        for lng in valid_lng_code:
            Meta(lng=lng, ns="valid_namespace", location=iptlib_res.files())


class TestTranslationManager:

    def test_resource_add_and_get(self, valid_lng_code, valid_snake_case_names):
        """Test adding and retrieving a translation resource."""

        mgr = manager._TranslationResourceManager()

        for lng in valid_lng_code:
            for ns in valid_snake_case_names:
                resource = Meta(lng=lng, ns=ns, location=iptlib_res.files())
                mgr.register(resource)

                retrieved = mgr._get_resource_metadata(lng, ns)

    def test_duplicated_resources(self, valid_lng_code, valid_snake_case_names):
        """Test that adding a duplicated resource raises an error."""

        mgr = manager._TranslationResourceManager()

        lng, ns = valid_lng_code[0], valid_snake_case_names[0]
        resource = Meta(lng=lng, ns=ns, location=iptlib_res.files())

        mgr.register(resource)

        with pytest.raises(trans_errs.DuplicatedTranslationNamespace):
            mgr.register(resource)
