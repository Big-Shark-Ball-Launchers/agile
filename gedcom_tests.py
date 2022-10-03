import io
import unittest
import unittest.mock

import sys
import tempfile

import gedcom_interp as gi

class gedcom_tests(unittest.TestCase):

    def run_gedcom_test(self, gedcom_file, expected_output, f):
        '''gedcom_file is a string containing the gedcom file to be tested.
            expected_output is a string containing the expected output.
            f is the assertion to be used (e.g. self.assertIn, self.assertNotIn, etc.)'''
        with tempfile.NamedTemporaryFile() as tmp:
            with unittest.mock.patch.object(sys, 'argv', ['prog', tmp.name]):
                with unittest.mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                    tmp.write(gedcom_file.encode('utf-8'))
                    tmp.seek(0)
                    gi.main()
                    f(expected_output, fake_out.getvalue())

    def testexample(self):
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
        expectedOutput = 'MARR'
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS04_1(self):
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 14 FEB 1970
        0 TRLR'''
        expectedOutput = "ERROR: US04: FAM @F1@: Divorce date 14 FEB 1970 occurs before marriage date 14 FEB 1980"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
        

if __name__ == '__main__':
    unittest.main()