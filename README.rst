================
Barracuda
================

.. image:: https://api.travis-ci.org/barracuda-project/barracuda.svg?branch=master
   :target: https://travis-ci.org/github/barracuda-project/barracuda/builds
.. image:: https://img.shields.io/codecov/c/github/barracuda-project/barracuda/master.svg
   :target: https://codecov.io/github/barracuda-project/barracuda?branch=master
   :alt: Coverage report
.. image:: https://img.shields.io/badge/license-%20MIT-blue.svg
   :target: ../master/LICENSE


Overview
===========

Show how to structure a Python project.

Requirements
============

* Python 3.5+
* Works on Linux, Windows, macOS, BSD

Install
=======

The quick way::

    pip install barracuda


Split your code into packages, modules, and functions
-----------------------------------------------------

- All code should be inside some function (except perhaps ``if __name__ == '__main__':``).
- Split long functions into smaller functions.
- If you need to scroll through a function over several screens, it is probably too long.
- Functions should do one thing and one thing only.
- Hide internals with underscores.
- Organize related functions into modules.
- If modules grow too large, split them.
- Import from other modules under ``somepackage/`` using ``from .somemodule import something``.
- Do file I/O on the "outside" of your code, not deep inside.


Classes vs. functions
---------------------

- Do not overuse classes.
- Prefer immutable data structures.
- Prefer pure functions.


Interfaces
----------

- In ``somepackage/__init__.py`` define what should be visible to the outside.
- Use https://semver.org.


Dependency management
---------------------

- Package dependencies for developers should be listed in ``requirements.txt``.
- Alternatively, consider using http://pipenv.readthedocs.io.
- Package dependencies for users of your code (who will probably install via pip) should be listed in ``setup.py``.


Type checking
-------------

- Consider using type hints: https://docs.python.org/3/library/typing.html
- Consider using http://mypy-lang.org.
- Consider verifying type annotations at runtime: https://github.com/RussBaz/enforce


