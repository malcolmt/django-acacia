import unittest

from acacia.tests import test_models, test_templatetags

def suite():
    test_suite = unittest.defaultTestLoader.loadTestsFromModule(test_models)
    test_suite.addTests(unittest.defaultTestLoader. \
            loadTestsFromModule(test_templatetags))
    return test_suite

