# -*- coding: utf-8 -*-

"""
:mod:`taika.taika`
==================
"""
import logging
import sys
from importlib import import_module
from pathlib import Path

from taika import frontmatter
from taika.events import EventManager
from taika.utils import List
from taika.utils import TaikaConf
from taika.utils import add_syspath
from taika.utils import pretty_json

__all__ = ["read_conf", "write_file", "read_file"]

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("taika")

TAIKA_CONF = "{source}/taika.ini"

DEFAULT_EXTENSIONS = ""
DEFAULT_EXTENSIONS_PATH = ""


class Taika(object):
    """Taika main class.

    Attributes
    ----------
    source : :class:`pathlib.Path`
    destination : :class:`pathlib.Path`
    events : :class:`taika.events.EventManager`
    config : :class:`configparser.ConfigParser`
    """

    def __init__(self, source, destination, conf_path=None):
        """Read all RST files from `source`, parse them and write them back as HTML in `dest`.

        Parameters
        ----------
        source : str
            The path to the source directory.
        dest : str
            The path where the parsed files will be writed.

        Notes
        -----
        By default, this functions maintains the `source` structure in `dest`.
        """
        self.events = EventManager()

        if conf_path is None:
            conf_path = TAIKA_CONF

        conf_path = conf_path.replace("{source}", str(source))
        self.config = read_conf(conf_path)

        self.import_extensions()
        self.source = Path(source)
        self.destination = Path(destination)

    def import_extensions(self):
        """Load the configuration and extensions."""
        extension_paths = List.from_string(
            self.config["taika"].get("extension_paths", DEFAULT_EXTENSIONS_PATH)
        )
        LOGGER.debug(f"extension_paths: {extension_paths}")
        extensions = List.from_string(self.config["taika"].get("extensions", DEFAULT_EXTENSIONS))
        LOGGER.debug(f"extensions: {extensions}")

        # Don't create byte-code, we want the extensions folders be clean.
        sys.dont_write_bytecode = True
        with add_syspath(extension_paths):
            for ext in extensions:
                import_module(ext).setup(self)
        sys.dont_write_bytecode = False

    def process(self):
        """Run :meth:`Taika.read` and :meth:`Taika.write`."""
        documents = self.read(self.source)
        self.write(documents, self.destination)

    def read(self, source):
        """Read all the files *recursively* from a `source` directory and load them as dictionaries.

        Parameters
        ----------
        source : :class:`pathlib.Path`
            The source directory where the documents are read from.

        Returns
        -------
        documents : list
            A list of dictionaries that represent documents.
        """
        documents = []
        for path in source.glob("**/*.*"):
            document = read_file(path)
            self.events.call("doc-post-read", self, document)
            documents.append(document)
        return documents

    def write(self, documents, destination):
        """Call `taika.taika.write_file` for each document on `documents` with `destination`.

        Parameters
        ----------
        documents : list
            A list of dictionaries that represent documents.
        destination : str or :class:`pathlib.Path`
            The destination directory.
        """
        for document in documents:
            write_file(document, destination)


def read_conf(conf_path):
    """Read the configuration file `conf_path`. It should be an INI style configuration.

    Parameters
    ----------
    conf_path : str
        The path to the configuration file to be readed.

    Returns
    -------
    conf : `configparser.ConfigParser`
        An instance of a ConfigParser which holds the configuration.

    Raises
    ------
    SystemExit
        If `conf_path` is not a file.
    """
    conf = TaikaConf()
    conf_path = Path(conf_path)
    if not conf_path.is_file():
        LOGGER.critical(f"The configuration file {conf_path} is not a file. Exiting...")
        exit(1)
    else:
        conf.read([conf_path])

    if "taika" not in conf.sections():
        LOGGER.critical(
            f"The configuration file {conf_path} does not have 'taika' section. Exiting...")
        exit(1)

    LOGGER.debug(
        pretty_json({section: dict(conf[section]) for section in conf.sections()})
    )

    return conf


def read_file(path):
    """Read `path` and return the document as a dictionary.

    Parameters
    ----------
    path : str or :class:`pathlib.Path`
        A path to a file to be read.

    Returns
    -------
    document : dict
        A dictionary that holds the information of the document read from `path`.
    """
    path = Path(path)

    LOGGER.debug("Reading: %s", path)

    raw_content = path.read_text()
    metadata, content = frontmatter.parse(raw_content)
    document = {
        "path": path.relative_to(path.parts[0]),  # the first part is the source directory
        "content": content,
        "raw_content": raw_content
    }

    document.update(metadata)

    return document


def write_file(document, destination):
    """Given a `document` and a destionation, write `document.content` in the destination.

    Parameters
    ----------
    document : dict
        A dictionary representing a document. Should have ``content`` and ``path``.
    destination : str or :class:`pathlib.Path`
        The destination directory where the document will be written.

    Raises
    ------
    KeyError
        If the document doesn't have ``content`` or ``path``.
    """
    destination = Path(destination)

    path = document["path"]
    content = document["content"]

    path = destination.joinpath(path)

    LOGGER.debug("Writing: %s", path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    path.write_text(content)
