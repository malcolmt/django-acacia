import unittest

from acacia.tests import test_models, test_templatetags

def suite():
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_models)
    suite.addTests(unittest.defaultTestLoader. \
            loadTestsFromModule(test_templatetags))
    return suite

