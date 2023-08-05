"""Frontmatter module."""
import re

import yaml

MARKUPS = {
    "YAML": re.compile(r'(?:^---\s*\n)([\s\S]+?)(?:^(?:---|\.\.\.)\s*\n)', re.MULTILINE),
}

PARSERS = {
    "YAML": yaml.load,
}


def parse(body):
    text = body.strip("\n")
    lang = None

    lang = select_language(text)
    if lang is None:
        return {}, text

    __, frontmatter, body = MARKUPS[lang].split(text, 2)
    frontmatter = frontmatter.strip("\n")
    body = body.strip("\n")

    frontmatter = PARSERS[lang](frontmatter)

    return frontmatter, body


def select_language(text):
    for lang, regex in MARKUPS.items():
        if regex.match(text):
            return lang
