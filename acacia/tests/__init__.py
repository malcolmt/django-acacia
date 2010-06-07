import unittest

from acacia.tests import test_models

def suite():
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_models)
    return suite

