import sys

from taika import utils


def test_add_syspath():
    paths = ["A", "B", "C"]
    prev_path = sys.path[:]

    with utils.add_syspath(paths):
        context_path = sys.path[:]

    assert prev_path != context_path
    assert prev_path == sys.path
    assert all([path in context_path for path in paths])
    assert not any([path in prev_path for path in paths])


def test_List():
    to_parse = "this\nis\na\nlist."

    parsed = utils.List.from_string(to_parse)

    assert isinstance(parsed, list)
    assert len(parsed) == 4


def test_dict():
    to_parse = "this=is\na multiple = key thing\nkey = value = sign"

    parsed = utils.Dict.from_string(to_parse)

    for key, value in parsed.items():
        assert not key.startswith(" ") and not key.endswith(" ")
        assert not value.startswith(" ") and not value.endswith(" ")

    assert "=" in parsed["key"]
