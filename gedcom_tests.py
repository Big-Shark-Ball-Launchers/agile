import io
import unittest
import unittest.mock

import sys
import tempfile

import gedcom_interp as gi

class gedcom_tests(unittest.TestCase):
    def testexample(self):
        # If your test file could be used in multiple tests, you can create it outside the test definition.
        # Give it a descriptive name and place it below the testexample definition.
        testFile = '''0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
0 HEAD
0 @I1@ INDI
1 NAME Dick /Smith/
2 GIVN Dick
2 SURN Smith
1 SEX M
1 BIRT
2 DATE 13 FEB 1981
1 RESI
2 ADDR carnage_flaky0o@icloud.com
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I3@
1 WIFE @I2@
1 CHIL @I1@
1 CHIL @I4@
1 MARR
2 DATE 14 FEB 1980
1 _CURRENT Y
1 _PRIMARY Y
0 TRLR'''
        with tempfile.NamedTemporaryFile() as tmp:
            with unittest.mock.patch.object(sys, 'argv', ['prog', tmp.name]):
                with unittest.mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                    tmp.write(testFile.encode('utf-8'))
                    tmp.seek(0)
                    gi.main()
                    self.assertIn('MARR', fake_out.getvalue()) #replace MARR with string expected in output

if __name__ == '__main__':
    unittest.main()