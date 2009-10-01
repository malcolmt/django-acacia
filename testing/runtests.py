#!/usr/bin/env python
"""
A script to run the Acacia tests in standalone mode, using an absolute minimal
configuration.

Uses SQLite as the database and assumes the django-mptt application is
importable as "mptt" (that is, assumes it is on the Python path somewhere).
"""

import os
import sys

from django.conf import settings
from django.core import management

import test_settings

def main(argv=None):
    """
    Does the equivalent of "django-admin.py test acacia" after doing some basic
    configuration. Caller can also pass in the names of particular TestCase or
    test method to run, as per the normal unittest calling style. In that case,
    those tests are run, instead of the full suite.
    """
    if argv is None:
        argv = sys.argv
    if len(argv) == 1:
        # No particular tests requested. Run the whole suite.
        args = [argv[0], "test", "acacia"]
    else:
        args = [argv[0], "test"] + argv[1:]

    # Ensure the local version of "acacia" is directly importable
    pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, pkg_dir)

    options = {}
    for name in dir(test_settings):
        if name == name.upper():
            options[name] = getattr(test_settings, name)
    settings.configure(**options)

    controller = management.ManagementUtility(args)
    controller.execute()


if __name__ == "__main__":
    main()

