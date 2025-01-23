from pytest import fixture


@fixture
def invalid_dsk_names() -> list[str]:
    """Return a sequence of invalid dot-separated snake-case string"""
    return [
        "invalid-with-dash.some.name",
        "some.names.with.extra.dots.",
        "",
        ".dot.at.begining",
        "some.other&.invalid.charater",
        "invalid:char",
        "..",
    ]


@fixture
def valid_dsk_names() -> list[str]:
    """Return a sequence of valid dot-separated snake-case string"""
    return [
        "valid.test.name",
        "valid_name",
        "alsovalid",
        "some_other.valid_.name",
        "v.a.l.i.d.n.a.n.e",
        "_.this.is__.also.valid",
    ]
