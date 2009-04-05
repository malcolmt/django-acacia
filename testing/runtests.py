#!/usr/bin/env python
"""
A script to run the Acacia tests in standalone mode, using an absolute minimal
configuration.

Uses SQLite as the database and assumes the django-treebeard application is
importable as "treebeard" (that is, assumes it is on the Python path somewhere).
"""

import os
import sys

import test_settings
from django.conf import settings
from django.core import management

def main(argv=None):
    """
    Does the equivalent of "django-admin.py test acacia" after doing some basic
    configuration.
    """
    if argv is None:
        argv = sys.argv

    # Ensure the local version of "acacia" is directly importable
    pkg_dir = os.path.join(os.path.dirname(__file__), "..")
    sys.path.insert(0, pkg_dir)

    options = {}
    for name in dir(test_settings):
        if name == name.upper():
            options[name] = getattr(test_settings, name)
    settings.configure(**options)

    controller = management.ManagementUtility([argv[0], "test", "acacia"])
    controller.execute()


if __name__ == "__main__":
    main()

