import configparser
import contextlib
import json
import os
import sys
from functools import partial

__all__ = ["List", "add_syspath", "pretty_json"]

pretty_json = partial(json.dumps, indent=4)


class List(list):

    @classmethod
    def from_string(cls, s, sep=os.linesep):
        return cls([elem.strip() for elem in s.split(sep) if elem.strip()])


class Dict(dict):

    @classmethod
    def from_string(cls, s):
        pairs = [element.split("=", maxsplit=1) for element in List.from_string(s)]
        return {key.strip(): value.strip() for key, value in pairs}


@contextlib.contextmanager
def add_syspath(paths):
    for path in paths:
        sys.path.insert(0, path)

    yield

    for path in paths:
        sys.path.remove(path)


class TaikaConf(object):

    def __new__(cls):
        return configparser.ConfigParser(
            converters={"list": List.from_string, "dict": Dict.from_string}
        )
