import unittest

from gluon.globals import Request

execfile("applications/groupthink/controllers/default.py", globals())

class TestFunctions(unittest.TestCase):
        def setUp(self):
            return

        def testUserfromEmail(self):
            self.assertEquals("Richard Julig", get_user_name_from_email("rjulig@ucsc.edu"))


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestFunctions))
unittest.TextTestRunner(verbosity=2).run(suite)
