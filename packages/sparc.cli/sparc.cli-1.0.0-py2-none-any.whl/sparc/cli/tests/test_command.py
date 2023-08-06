import os
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sparc.cli.testing import SPARC_CLI_INTEGRATION_LAYER

class test_suite(test_suite_mixin):
    layer = SPARC_CLI_INTEGRATION_LAYER
    package = 'sparc.cli'
    module = 'command'


if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])