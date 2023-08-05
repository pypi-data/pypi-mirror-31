import re

from taika.events import EventManager
from taika.ext import layouts
from taika.utils import TaikaConf


class FakeSite(object):

    def __init__(self):
        self.events = EventManager()
        self.config = TaikaConf()
        self.config.read_dict({"taika": {"layouts_path": "source/templates"}})


def test_setup():
    site = FakeSite()
    layouts.setup(site)


def test_correct():
    site = FakeSite()
    renderer = layouts.JinjaRenderer(site.config)
    document = {"path": "non_existent.rst", "content": "A simple phrase.", "title": "Awesome!"}

    renderer.render_content(site, document)

    assert "<title>Awesome!</title>" in document["content"]
    assert re.search("<body>.*A simple phrase\..*</body>", document["content"], re.DOTALL)


def test_body_rendering():
    site = FakeSite()
    renderer = layouts.JinjaRenderer(site.config)
    document = {
        "path": "non_existent.rst",
        "title": "Awesome!",
        "content": "{{ title }}"
    }

    renderer.render_content(site, document)

    assert "<title>Awesome!</title>" in document["content"]
    assert re.search("<body>.*Awesome!.*</body>", document["content"], re.DOTALL)


def test_option_layouts_pattern():
    site = FakeSite()
    site.config["taika"]["layouts_pattern"] = "**/*.txt"
    renderer = layouts.JinjaRenderer(site.config)
    document = {"path": "non_existent.rst", "content": "A simple phrase.", "title": "Awesome!"}

    renderer.render_content(site, document)

    assert "<title>Awesome!</title>" not in document["content"]
    assert not re.search("<body>.*A simple phrase\..*</body>", document["content"], re.DOTALL)


def test_option_layouts_default():
    site = FakeSite()
    site.config["taika"]["layouts_default"] = "empty.html"
    renderer = layouts.JinjaRenderer(site.config)
    document = {"path": "non_existent.rst", "content": "A simple phrase.", "title": "Awesome!"}

    renderer.render_content(site, document)

    assert document["content"] == ""


def test_frontmatter_layout():
    site = FakeSite()
    renderer = layouts.JinjaRenderer(site.config)
    document = {
        "layout": "empty.html",
        "path": "non_existent.rst",
        "content": "A simple phrase.",
        "title": "Awesome!"
    }

    renderer.render_content(site, document)

    assert document["content"] == ""


def test_frontmatter_layout_None():
    site = FakeSite()
    renderer = layouts.JinjaRenderer(site.config)
    document = {
        "layout": None,
        "path": "non_existent.rst",
        "content": "A simple phrase.",
        "title": "Awesome!"
    }
    prev_content = document["content"]

    renderer.render_content(site, document)

    assert document["content"] == prev_content


def test_option_layouts_options():
    site = FakeSite()
    site.config["taika"]["layouts_options"] = "autoescape=True"
    renderer = layouts.JinjaRenderer(site.config)
    document = {
        "path": "non_existent.rst",
        "content": "<p>A simple phrase.</p>",
        "title": "Awesome!"
    }

    renderer.render_content(site, document)

    assert "&lt;p&gt;" in document["content"]
