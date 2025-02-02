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
        "Capital",
        "has.Capital.letters",
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
        "1.number.is.also.ok",
    ]


@fixture
def valid_snake_case_names() -> list[str]:
    return ["some_snake_case", "ok", "1", "__ok", "__", "ok__"]


@fixture
def invalid_snake_case_names() -> list[str]:
    return ["some-name", "", "Not_ok", ".not_ok", ".", "this:not_ok", "with.dot"]


@fixture
def invalid_lng_code() -> list[str]:
    return ["eng", "EN", "english", "en_US", "123", "en-US-123", "en-usa"]


@fixture
def valid_lng_code() -> list[str]:
    return ["en", "fr", "es", "de", "zh", "en-US", "fr-CA", "es-MX", "de-CH", "zh-CN"]
