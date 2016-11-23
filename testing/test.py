import unittest

from gluon.globals import Request

execfile("applications/groupthink/controllers/default.py", globals())

class TestFunctions(unittest.TestCase):
        def setUp(self):
            request = Request()

        def testUserfromEmail(self):
            self.assertEquals("Richard Julig", get_user_name_from_email("rjulig@ucsc.edu"))