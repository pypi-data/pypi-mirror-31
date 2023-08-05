Taika
=====

.. image:: https://img.shields.io/pypi/v/taika.svg
    :target: https://pypi.python.org/pypi/taika

.. image:: https://readthedocs.org/projects/taika/badge/?version=latest
    :target: https://taika.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://gitlab.com/hectormartinez/taika/badges/master/pipeline.svg
    :target: https://gitlab.com/hectormartinez/taika/commits/master
    :alt: Pipeline Status


Another Static Site Generator


* Free software: MIT license
* Documentation: https://taika.readthedocs.io.


Features
--------

* INI configuration
* Simple
* Extensible
* Documents JSON representated

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


History
=======

:tag:`v0.5.0` (2018-04-16)
----------------

Added
~~~~~

* Extensions system.
* Two extensions: ``rst`` and ``layouts``.
* INI file configuration.
* Main ``Taika`` class to orchestrate managers and configuration.

Changed
~~~~~~~

* CLI parsing now is done by ``argparse``.

Fixed
~~~~~

* Documentation.


:tag:`v0.4.0` (2018-03-17)
---------------------------

Added
~~~~~

* CLI entry point via ``taika``.
* GitLab folder for issues and merge requests customization.
* Spell checker for the documentation.

Removed
~~~~~~~

* Certain folders that should be untracked.
* Unused badges on the README.


:tag:`v0.3.0` (2018-03-15)
--------------------------

Necessary BUMP to wrap my head around the schema.


:tag:`v0.2.1` (2018-03-15)
--------------------------

Added
~~~~~

* GitLab Continuous Integration.
* Configuration for pytest: now the working directory is the ``tests`` folder.

Removed
~~~~~~~

* Travis Continuous Integration.


:tag:`v0.2.0` (2018-03-15)
--------------------------

Added
~~~~~

* Added the skeleton for the project.
* Added the first functions and functionality via API.


0.1.X (YYYY-MM-DD)
------------------

This versions correspond to older taika versions that I've uploaded to PyPi.

.. _Unreleased: https://gitlab.com/hectormartinez/taika


