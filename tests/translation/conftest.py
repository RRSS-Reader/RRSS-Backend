from importlib import resources as iptlib_res

from pytest import fixture
from tests.fixtures.types import *

from translation import types as trans_types

Meta = trans_types.TransResourceMetaData


@fixture
def sample_resource_metadata(valid_lng_code, valid_snake_case_names):
    return [
        Meta(lng=lng, ns=ns, location=iptlib_res.files())
        for lng in valid_lng_code
        for ns in valid_snake_case_names
    ]
