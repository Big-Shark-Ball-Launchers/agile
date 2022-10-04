import io
import unittest
import unittest.mock
import os

import sys
import tempfile

import gedcom_interp as gi

class gedcom_tests(unittest.TestCase):

    # Function to help with testing.
    # Automatically creates a temporary file with the given contents, 
    # passes the file to the main program, and runs the passeed assertion 
    # with the expected output.
    def run_gedcom_test(self, gedcom_file, expected_output, f):
        '''gedcom_file is a string containing the gedcom file to be tested.
            expected_output is a string containing the expected output.
            f is the assertion to be used (e.g. self.assertIn, self.assertNotIn, etc.)'''
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with unittest.mock.patch.object(sys, 'argv', ['prog', tmp.name]):
                with unittest.mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                    tmp.write(gedcom_file.encode('utf-8'))
                    tmp.seek(0)
                    gi.main()
                    f(expected_output, fake_out.getvalue())
                    tmp.close()
                    os.unlink(tmp.name)

    # Example test. Use as a template. Should always pass.
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

        #US02 tests (Marriage after birth)
    def testUS02_1(self):
        # Born after marriage
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 2000
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
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
        expectedOutput = "ANNOMALY: US02: INDI/FAM @I3@: Marriage date: 14 FEB 1980 occurs before the individual's birthdate 15 JUL 2000"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    #US02 tests (Marriage after birth)
    def testUS02_2(self):
        # Wife born after marriage
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1940
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1950
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "ANNOMALY: US02: INDI/FAM @I2@: Marriage date: 14 FEB 1950 occurs before the individual's birthdate 23 SEP 1960"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    #US02 tests (Marriage after birth)
    def testUS02_3(self):
        # Wife born after marriage
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1940
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "\nANNOMALY: US02: INDI/FAM @I3@: Marriage date: 14 FEB 1940 occurs before the individual's birthdate 15 JUL 1960\nANNOMALY: US02: INDI/FAM @I2@: Marriage date: 14 FEB 1940 occurs before the individual's birthdate 23 SEP 1960\n"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
        
    #US02 tests (Marriage after birth)
    def testUS02_4(self):
        # Marriage date and birthdate are the same (no error)
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 15 JUL 1960
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "US02"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    #US02 tests (Marriage after birth)
    def testUS02_5(self):
        # No error
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
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
        expectedOutput = "US02"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    #US03 tests (Birth before death)
    def testUS03_1(self):
        # No error
        testFile = '''
       0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
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
        expectedOutput = "US03"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    #US03 tests (Birth before death)
    def testUS03_2(self):
        # bDay after dDay
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 1955
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
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
        expectedOutput = "ERROR: US03: INDI/FAM @I3@: Death date: 31 DEC 1955 occurs before the individual's birthdate 15 JUL 1960"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    #US03 tests (Birth before death)
    def testUS03_3(self):
        # bDay and dDay same year (no error)
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 1960
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
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
        expectedOutput = "US03"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

        #US03 tests (Birth before death)
    def testUS03_4(self):
        # birthdate and death date on same day (no issue)
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1980
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
        expectedOutput = "US03"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

        #US03 tests (Birth before death)
    def testUS03_5(self):
        # dates far apart no issue
        testFile = '''
        0 NOTE https://github.com/Big-Shark-Ball-Launchers/agile
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE My Family
        1 DATE 25 SEP 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I1@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
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
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 JUN 1983
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1800
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "US03"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    

    #US04 tests (Marriage before divorce)
    def testUS04_1(self):
        # Normal situation where error should occur
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

    def testUS04_2(self):
        #Marriage and divorce on the same day is strange, but not impossible.
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
        2 DATE 14 FEB 1980
        0 TRLR'''
        expectedOutput = "US04"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS04_3(self):
        # Normal situation where error should not occur
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
        2 DATE 20 JUN 1990
        0 TRLR'''
        expectedOutput = "US04"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS04_4(self):
        # Divorce date missing. Should assume not divorced and not error.
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
        0 TRLR'''
        expectedOutput = "US04"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)
    
    def testUS04_5(self):
        # weird dates, error should occur
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
        2 DATE 14 JUN 2300
        1 DIV
        2 DATE 21 JAN 2200
        0 TRLR'''
        expectedOutput = "ERROR: US04: FAM @F1@: Divorce date 21 JAN 2200 occurs before marriage date 14 JUN 2300"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    #US05 Tests (marriage before death)
    def testUS05_1(self):
        # both members are alive. No error should occur.
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@

        0 @I1@ INDI
        1 NAME Mary /Smith/
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 JUN 2000
        0 TRLR'''
        expectedOutput = "US05"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS05_2(self):
        # both members are dead. Error should not occur.
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 13 MAR 2000
        1 FAMS @F1@

        0 @I1@ INDI
        1 NAME Mary /Smith/
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 20 FEB 1999
        1 FAMS @F1@
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 JUN 1998
        0 TRLR'''
        expectedOutput = "US05"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS05_3(self):
        # both members are dead. Error should occur.
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 13 MAR 2000
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary /Smith/
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 20 FEB 1999
        1 FAMS @F1@
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 JUN 2002
        0 TRLR'''
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of one or both spouses"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS05_4(self):
        # both members dead. Only one is erroneous. Error should occur.
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 13 MAR 2004
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary /Smith/
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 20 FEB 1999
        1 FAMS @F1@
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 JUN 2002
        0 TRLR'''
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of one or both spouses"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS05_5(self):
        # one member dead. Error should occur.
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 DEAT
        2 DATE 13 MAR 2000
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary /Smith/
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 JUN 2002
        0 TRLR'''
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of one or both spouses"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)


if __name__ == '__main__':
    unittest.main()