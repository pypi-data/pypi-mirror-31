from taika.events import EventManager
from taika.ext import rst
from taika.utils import TaikaConf


class FakeSite(object):

    def __init__(self):
        self.events = EventManager()
        self.config = TaikaConf()
        self.config.read_dict({"taika": {}})


def test_setup():
    site = FakeSite()
    rst.setup(site)


def test_defaults():
    site = FakeSite()
    document = {"path": "non_existent.rst", "content": "A simple phrase."}

    rst.parse_rst(site, document)

    assert document["path"].suffix == rst.OUT_SUFFIX
    assert "<p>" in document["content"]


def test_option_rst_suffix():
    site = FakeSite()
    site.config.read_dict({"taika": {"rst_suffix": rst.DEFAULT_SUFFIX}})
    document = {"path": "non_existent.rst", "content": "A simple phrase."}

    rst.parse_rst(site, document)

    assert document["path"].suffix == rst.OUT_SUFFIX
    assert "<p>" in document["content"]


def test_suffix_no_match():
    site = FakeSite()
    document = {"path": "non_existent.md", "content": "A simple phrase."}

    rst.parse_rst(site, document)

    assert document["path"].suffix != rst.OUT_SUFFIX
    assert "<p>" not in document["content"]


def test_options_rst_suffix_list():
    site = FakeSite()
    site.config.read_dict({"taika": {"rst_suffix": ".md\n.txt"}})
    document_A = {"path": "non_existent.md", "content": "A simple phrase."}
    document_B = {"path": "non_existent.txt", "content": "A simple phrase."}

    rst.parse_rst(site, document_A)
    rst.parse_rst(site, document_B)

    assert document_A["path"].suffix == rst.OUT_SUFFIX
    assert "<p>" in document_A["content"]
    assert document_B["path"].suffix == rst.OUT_SUFFIX
    assert "<p>" in document_B["content"]
