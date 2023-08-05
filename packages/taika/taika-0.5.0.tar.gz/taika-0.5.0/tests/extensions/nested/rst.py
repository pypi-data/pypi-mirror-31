"""
:mod:`taika.ext.rst` -- ReStructuredText
========================================

This extension parses the content of the documents into HTML using ReStructuredText specifications.

Trigger
-------

This extension is subscribed to the "doc-post-read" event.

Frontmatter
-----------

None.

Process
-------

#. Reads the suffix of the path and if it matches, process the document.
#. Modifies the suffix of the path to ".html".
#. Process the content with :func:`docutils.publish_parts` and replaces it with the "body" part.
#. Done!

Configuration
-------------

.. data:: rst_suffix (dangling-list)

    Default: **[.rst]**

    Tells the parser to ONLY modify docs with that suffix. Otherwise the document is ignored.

Functions
---------
"""
from pathlib import Path

from docutils.core import publish_parts

RST_OPTIONS = {"stylesheet_path": ""}
DEFAULT_SUFFIX = ".rst"
OUT_SUFFIX = ".html"


def parse_rst(site, document):
    """Parse ``content`` and modify ``path`` keys of `document`.

    Parameters
    ----------
    site : :class:`taika.taika.Taika`
        The Taika site.
    document : dict
        The document to be parsed.
    """
    suffixes = site.config["taika"].getlist("rst_suffix", fallback=DEFAULT_SUFFIX)
    print(suffixes)

    document["path"] = Path(document["path"])
    if document["path"].suffix not in suffixes:
        return

    document["path"] = document["path"].with_suffix(OUT_SUFFIX)

    html = publish_parts(
        document["content"],
        writer_name="html5",
        settings_overrides=RST_OPTIONS
    )["body"]

    document["content"] = html


def setup(site):
    site.events.register("doc-post-read", parse_rst)
