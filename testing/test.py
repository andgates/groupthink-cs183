import unittest

from gluon.globals import Request

execfile("applications/groupthink/controllers/default.py", globals())

class TestFunctions(unittest.TestCase):
        def setUp(self):
            return
        #tests userfromemail to see if it works
        def testUserfromEmail(self):
            #Should pass
            self.assertEquals("Richard Julig", get_user_name_from_email("rjulig@ucsc.edu"))
            #Should fail
            self.assertEquals("Richy lig", get_user_name_from_email("rjulig@ucsc.edu"))
            #Should fail
            self.assertEquals("Richard Julig", get_user_name_from_email("theprofessor@ucsc..edu"))


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestFunctions))
unittest.TextTestRunner(verbosity=2).run(suite)
