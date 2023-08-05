#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taika` package."""

from pathlib import Path

import pytest

from taika import frontmatter
from taika import taika


def test_Taika(tmpdir):
    """Tests the function run in the taika module."""
    source = Path("source")
    dest = Path(tmpdir)

    site = taika.Taika(source, dest)
    site.process()

    assert dest.is_dir()


def test_frontmatter_complex_ok():
    """Test that the frontmatter is correctly handled."""

    expected_fm = {
        'name': "Martin D'vloper",
        'job': 'Developer',
        'skill': 'Elite',
        'employed': True,
        'foods': ['Apple', 'Orange', 'Strawberry', 'Mango'],
        'languages': {'perl': 'Elite', 'python': 'Elite', 'pascal': 'Lame'},
        'education': '4 GCSEs\n3 A-Levels\nBSc in the Internet of Things',
    }
    expected_body = 'Some title\n==========\n\nAnd subtitles too\n-----------------\n\nAnd text.'
    with open("source/fm-complex-ok.rst") as fd:
        content = fd.read()

    fm, body = frontmatter.parse(content)

    assert fm == expected_fm
    assert body == expected_body


def test_frontmatter_no_closing_tag():
    expected_fm = {}
    with open("source/fm-no-closing-tag.rst") as fd:
        content = fd.read()
    expected_body = content

    fm, body = frontmatter.parse(content)

    assert fm == expected_fm
    assert body == expected_body.strip('\n')


def test_read_file():
    path = "source/fm-simple.rst"
    expected_content = "This document will have normal frontmatter."
    expected_path = "fm-simple.rst"

    document = taika.read_file(path)

    assert document
    assert document["layout"] is None
    assert document["permalink"] is None
    assert document["content"] == expected_content
    assert str(document["path"]) == expected_path


def test_write_file(tmpdir):
    document = {
        "content": "<html>Hey!</html>",
        "path": "this-is-an-invented-document.html"
    }

    taika.write_file(document, tmpdir)


def test_unexistent_conf_path(tmpdir):
    source = "source"
    with pytest.raises(SystemExit):
        taika.Taika(source, tmpdir, "I-dont't-exist.ini")


def test_empty_conf_path(tmpdir):
    source = "source"
    with pytest.raises(SystemExit):
        taika.Taika(source, tmpdir, conf_path="source/taika_empty.ini")
