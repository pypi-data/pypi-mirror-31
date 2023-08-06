"""
@file
@brief Helpers for CI

.. versionadded:: 1.3
"""


def is_travis_or_appveyor():
    """
    tells if is a travis environment or appveyor

    @return        ``'travis'``, ``'appveyor'`` or ``None``

    The function should rely more on environement variables
    ``CI``, ``TRAVIS``, ``APPVEYOR``.

    .. versionadded:: 1.3

    .. versionchanged:: 1.5
        Takes into account *circleci*.
    """
    import sys
    if "travis" in sys.executable:
        return "travis"
    import os
    if os.environ.get("USERNAME", os.environ.get("USER", None)) == "appveyor" or \
       os.environ.get("APPVEYOR", "").lower() in ("true", "1"):
        return "appveyor"
    if os.environ.get('CIRCLECI', "undefined") != "undefined":
        return "circleci"
    return None
