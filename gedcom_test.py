import datetime
import gedcom_interp as gi
import io
import os
import sys
import tempfile
import unittest
import unittest.mock

from gedcom_interp import datetimeToString

# Function to help with testing.
# Automatically creates a temporary file with the given contents,
# passes the file to the main program, and runs the passeed assertion
# with the expected output.
def run_test(self, gedcom_file, expected_output, f):
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

class test_example(unittest.TestCase):
    run_gedcom_test = run_test
    def test_example(self):
        # Example test. Use as a template. Should always pass.
        testFile = '''
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
        0 TRLR
        '''
        expectedOutput = 'MARR'
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US01_tests(unittest.TestCase):
    run_gedcom_test = run_test

    # US01 tests (Dates before current date)
    def testUS01_1(self):
        # Normal - no errors
        testFile = '''
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
        expectedOutput = "US01"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS01_2(self):
        # individual born after current date
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 2023
        0 @F1@ FAM
        0 TRLR'''
        currDateString = datetimeToString(datetime.datetime.now())
        expectedOutput = "ERROR: US01: INDI/FAM @I1@: Date BIRT 13 FEB 2023 occurs after current date " + currDateString
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS01_3(self):
        # individual died after current date
        testFile = '''
        0 HEAD
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 DEAT Y
        2 DATE 31 DEC 2022
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        0 TRLR'''
        currDateString = datetimeToString(datetime.datetime.now())
        expectedOutput = "ERROR: US01: INDI/FAM @I3@: Date DEAT 31 DEC 2022 occurs after current date " + currDateString
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS01_4(self):
        # family married after current date
        testFile = '''
        0 HEAD
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2023
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        currDateString = datetimeToString(datetime.datetime.now())
        expectedOutput = "ERROR: US01: INDI/FAM @F1@: Date MARR 14 FEB 2023 occurs after current date " + currDateString
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS01_5(self):
        # family divorced after current date
        testFile = '''
        0 HEAD
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
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 20 APR 2024
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        currDateString = datetimeToString(datetime.datetime.now())
        expectedOutput = "ERROR: US01: INDI/FAM @F1@: Date DIV 20 APR 2024 occurs after current date " + currDateString
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US02_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US02 tests (Birth before marriage)
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
        expectedOutput = "ERROR: US02: INDI/FAM @I3@: Marriage date: 14 FEB 1980 occurs before the individual's birthdate 15 JUL 2000"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    # US02 tests (Marriage after birth)
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
        expectedOutput = "ERROR: US02: INDI/FAM @I2@: Marriage date: 14 FEB 1950 occurs before the individual's birthdate 23 SEP 1960"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    # US02 tests (Marriage after birth)
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
        expectedOutput = "\nERROR: US02: INDI/FAM @I3@: Marriage date: 14 FEB 1940 occurs before the individual's birthdate 15 JUL 1960\nERROR: US02: INDI/FAM @I2@: Marriage date: 14 FEB 1940 occurs before the individual's birthdate 23 SEP 1960\n"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    # US02 tests (Marriage after birth)
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

    # US02 tests (Marriage after birth)
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

class US03_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US03 tests (Birth before death)
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

    # US03 tests (Birth before death)
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

    # US03 tests (Birth before death)
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

        # US03 tests (Birth before death)
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

        # US03 tests (Birth before death)
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

class US04_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US04 tests (Marriage before divorce)
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

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 14 FEB 1970
        0 TRLR'''
        expectedOutput = "ERROR: US04: FAM @F1@: Divorce date 14 FEB 1970 occurs before marriage date 14 FEB 1980"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS04_2(self):
        # Marriage and divorce on the same day is strange, but not impossible.
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

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
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

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
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

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        
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

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 JUN 2300
        1 DIV
        2 DATE 21 JAN 2200
        0 TRLR'''
        expectedOutput = "ERROR: US04: FAM @F1@: Divorce date 21 JAN 2200 occurs before marriage date 14 JUN 2300"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US05_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US05 Tests (Marriage before death)
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
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of INDI @I1@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of INDI @I2@"
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
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of INDI @I2@"
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
        expectedOutput = "ERROR: US05: FAM @F1@: Marriage date 14 JUN 2002 occurs after death of INDI @I1@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US06_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US06 Tests (Divorce before death)
    def testUS06_1(self):
        # both members are alive. No error should occur.
        testFile = '''
        0 HEAD
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
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 MAY 2006
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "US06"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS06_2(self):
        # Divorce after husband's death
        testFile = '''
        0 HEAD
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 8 MAR 2016
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "ERROR: US06: FAM @F1@: Divorce date 8 MAR 2016 occurs before death of one or both spouses"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS06_3(self):
        # divorce after wife's death
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 DEAT Y
        2 DATE 26 AUG 2016
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1960
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 27 JUN 2019
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "ERROR: US06: FAM @F1@: Divorce date 27 JUN 2019 occurs before death of one or both spouses"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS06_4(self):
        # divorce after both deaths
        testFile = '''
                0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 DEAT Y
        2 DATE 26 AUG 2016
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 8 MAR 2019
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "ERROR: US06: FAM @F1@: Divorce date 8 MAR 2019 occurs before death of one or both spouses"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS06_5(self):
        # divorce same day as husband's death. no error should occur.
        testFile = '''
        0 HEAD
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 31 DEC 2013
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR'''
        expectedOutput = "US06"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS06_6(self):
        # both spouses are dead, but divorce date is before death date. No error should occur.
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1960
        1 DEAT Y
        2 DATE 26 AUG 2016
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 NOV 2001
        0 TRLR'''
        expectedOutput = "US06"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US07_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US07 tests (Less than 150 years old)
    def testUS07_1(self):
        # individual is older than 150
        testFile = '''
        0 HEAD
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1800
        1 DEAT Y
        2 DATE 31 DEC 2022
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        0 TRLR'''
        expectedOutput = "ANOMALY: US07: INDI @I3@: Age over 150 years old: 222"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS07_2(self):
        # individual is exactly 150
        testFile = '''
        0 HEAD
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1872
        1 DEAT Y
        2 DATE 31 DEC 2022
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        0 TRLR'''
        expectedOutput = "US07"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS07_3(self):
        # individual younger than 150
        testFile = '''
        0 HEAD
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1900
        1 DEAT Y
        2 DATE 31 DEC 2022
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        0 TRLR'''
        expectedOutput = "US07"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS07_4(self):
        # individual is MUCH older than 150
        testFile = '''
        0 HEAD
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1000
        1 DEAT Y
        2 DATE 31 DEC 2022
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        0 TRLR'''
        expectedOutput = "ANOMALY: US07: INDI @I3@: Age over 150 years old: 1022"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS07_5(self):
        # individual died at 151
        testFile = '''
        0 HEAD
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1871
        1 DEAT Y
        2 DATE 31 DEC 2022
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        0 TRLR'''
        expectedOutput = "ANOMALY: US07: INDI @I3@: Age over 150 years old: 151"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US08_tests(unittest.TestCase):
    run_gedcom_test = run_test
        # US08 Tests (Birth before marriage of parents or after 9 months after their divorce)
    def testUS08_1(self):
        # Birth after marriage - no error should occur
        testFile = '''
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
        expectedOutput = "US08"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS08_2(self):
        # Birth before marriage - error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1980
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
        expectedOutput = "ANOMALY: US08: INDI @I1@: Birth date 12 FEB 1980 occurs before parents' marriage date 14 FEB 1980 or more than 9 months after parents' divorce date NA in FAM @F1@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS08_3(self):
        # Birth more than 9 months after divorce - error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1981
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
        2 DATE 2 JUN 1997
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 13 JUL 1996
        0 TRLR'''
        expectedOutput = "ANOMALY: US08: INDI @I4@: Birth date 2 JUN 1997 occurs before parents' marriage date 14 FEB 1980 or more than 9 months after parents' divorce date 13 JUL 1996 in FAM @F1@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS08_4(self):
        # Birth within 9 months of divorce - no error should occur
        testFile = '''
                        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1981
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
        2 DATE 2 OCT 1996
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 13 JUL 1996
        0 TRLR'''
        expectedOutput = "US08"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS08_5(self):
        # Birth same day as marriage - no error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 14 FEB 1980
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
        expectedOutput = "US08"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US09_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US09 Tests (Birth before death of parents)
    def testUS09_1(self):
        # child born before death of both parents - no error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1981
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
        2 DATE 2 OCT 1996
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        0 TRLR'''
        expectedOutput = "US09"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS09_2(self):
        # born after death of mother - error should occur
        testFile = '''
                         0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1991
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
        1 DEAT Y
        2 DATE 4 SEP 1987
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
        2 DATE 2 OCT 1996
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 13 JUL 1996
        0 TRLR'''
        expectedOutput1 = "ANOMALY: US09: INDI @I1@: Birth date 12 FEB 1991 occurs after mother's death 4 SEP 1987 or more than 9 months after father's death 31 DEC 2013"
        self.run_gedcom_test(testFile, expectedOutput1, self.assertIn)
        expectedOutput2 = "ANOMALY: US09: INDI @I4@: Birth date 2 OCT 1996 occurs after mother's death 4 SEP 1987 or more than 9 months after father's death 31 DEC 2013"
        self.run_gedcom_test(testFile, expectedOutput2, self.assertIn)

    def testUS09_3(self):
        # Born after father has been dead for 9 months - error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1991
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
        2 DATE 31 DEC 1987
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 OCT 1996
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 13 JUL 1996
        0 TRLR'''
        expectedOutput1 = "ANOMALY: US09: INDI @I1@: Birth date 12 FEB 1991 occurs after mother's death NA or more than 9 months after father's death 31 DEC 1987"
        self.run_gedcom_test(testFile, expectedOutput1, self.assertIn)
        expectedOutput2 = "ANOMALY: US09: INDI @I4@: Birth date 2 OCT 1996 occurs after mother's death NA or more than 9 months after father's death 31 DEC 1987"
        self.run_gedcom_test(testFile, expectedOutput2, self.assertIn)

    def testUS09_4(self):
        # born after both parents are dead
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1981
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
        1 DEAT Y
        2 DATE 4 SEP 1995
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
        2 DATE 31 DEC 1997
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 2 OCT 2000
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        0 TRLR'''
        expectedOutput = "ANOMALY: US09: INDI @I4@: Birth date 2 OCT 2000 occurs after mother's death 4 SEP 1995 or more than 9 months after father's death 31 DEC 1997"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS09_5(self):
        # born within 9 months of father's death - no error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Dick /Smith/
        2 GIVN Dick
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 1981
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
        2 DATE 31 DEC 1996
        1 FAMS @F1@
        0 @I4@ INDI
        1 NAME Jane /Smith/
        2 GIVN Jane
        2 SURN Smith
        1 SEX F
        1 BIRT
        2 DATE 5 APR 1997
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 CHIL @I1@
        1 CHIL @I4@
        1 MARR
        2 DATE 14 FEB 1980
        0 TRLR'''
        expectedOutput = "US09"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US10_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US10 Tests (Marriage after 14)
    def testUS10_1(self):
        # marriage before 14
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1978
        1 DEAT Y
        2 DATE 26 AUG 2016
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 NOV 2001
        0 TRLR'''
        expectedOutput = "ANOMALY: US10: INDI @I2@: Marriage date: 14 FEB 1980 occurs before age of 14"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS10_2(self):
        # marriage after 14 (no error)
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1940
        1 DEAT Y
        2 DATE 26 AUG 2016
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 NOV 2001
        0 TRLR'''
        expectedOutput = "US10"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS10_3(self):
        # marriage at 14
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1966
        1 DEAT Y
        2 DATE 26 AUG 2016
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
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 NOV 2001
        0 TRLR'''
        expectedOutput = "ANOMALY: US10: INDI @I2@: Marriage date: 14 FEB 1980 occurs before age of 14"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS10_4(self):
        # both under 14
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1970
        1 DEAT Y
        2 DATE 26 AUG 2016
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1970
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 NOV 2001
        0 TRLR'''
        expectedOutput = "ANOMALY: US10: INDI @I2@: Marriage date: 14 FEB 1980 occurs before age of 14"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS10_5(self):
        # both exactly 14
        testFile = '''
        0 HEAD
        0 @I2@ INDI
        1 NAME Jennifer /Smith/
        2 GIVN Jennifer
        2 SURN Smith
        2 _MARNM Smith
        1 SEX F
        1 BIRT
        2 DATE 23 SEP 1965
        1 DEAT Y
        2 DATE 26 AUG 2016
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joe /Smith/
        2 GIVN Joe
        2 SURN Smith
        2 _MARNM Smith
        1 SEX M
        1 BIRT
        2 DATE 15 JUL 1965
        1 DEAT Y
        2 DATE 31 DEC 2013
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 18 NOV 2001
        0 TRLR'''
        expectedOutput = "US10"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US11_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US11 Tests (No Bigamy)
    def testUS11_1(self):
        # Normal simple family, no errors expected
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1978
        1 FAMS @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2003
        0 TRLR
        '''
        expectedOutput = "US11"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS11_2(self):
        # Simple family with bigamy, error expected
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@
        1 FAMS @F2@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1977
        1 FAMS @F2@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2003

        0 @F2@ FAM
        1 HUSB @I1@
        1 WIFE @I3@
        1 MARR
        2 DATE 14 FEB 2005

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US11: INDI @I1@ is an active spouse in muliple families. FAMS: ['@F1@', '@F2@']"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS11_3(self):
        # Simple family with divorce, no errors expected
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@
        1 FAMS @F2@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1977
        1 FAMS @F2@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2003
        1 DIV
        2 DATE 14 FEB 2004

        0 @F2@ FAM
        1 HUSB @I1@
        1 WIFE @I3@
        1 MARR
        2 DATE 14 FEB 2005

        0 TRLR
        '''
        expectedOutput = "US11"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS11_4(self):
        # Marriage within another marraige (with divorce), error expected
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@
        1 FAMS @F2@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1977
        1 FAMS @F2@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2003
        1 DIV
        2 DATE 14 FEB 2010

        0 @F2@ FAM
        1 HUSB @I1@
        1 WIFE @I3@
        1 MARR
        2 DATE 14 FEB 2005
        1 DIV
        2 DATE 14 FEB 2007

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US11: INDI @I1@ is an active spouse in muliple families. FAMS: ['@F1@', '@F2@']"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS11_5(self):
        # Marriage within another marraige (with death), error expected
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMS @F1@
        1 FAMS @F2@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1978
        1 FAMS @F1@
        1 DEAT Y
        2 DATE 14 FEB 2010

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1977
        1 FAMS @F2@
        1 DEAT Y
        2 DATE 14 FEB 2007

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2003

        0 @F2@ FAM
        1 HUSB @I1@
        1 WIFE @I3@
        1 MARR
        2 DATE 14 FEB 2005

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US11: INDI @I1@ is an active spouse in muliple families. FAMS: ['@F1@', '@F2@']"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
class US12_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US12 Tests (Parents not too old)
    def testUS12_1(self):
        # Normal family, no errors expected
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@

        0 TRLR
        '''
        expectedOutput = "US12"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS12_2(self):
        #Old Dad
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1910
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US12: INDI @I3@: Birthdate 13 FEB 2010 occurs more than 80 years after father's birthday: 13 FEB 1910"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS12_3(self):
        #Old Mom
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1940
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US12: INDI @I3@: Birthdate 13 FEB 2010 occurs more than 60 years after mother's birthday: 14 FEB 1940"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS12_4(self):
        #Both old
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1910
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1940
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US12: INDI @I3@: Birthdate 13 FEB 2010 occurs more than 60 years after mother's birthday: 14 FEB 1940"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
        expectedOutput = "ANOMALY: US12: INDI @I3@: Birthdate 13 FEB 2010 occurs more than 80 years after father's birthday: 13 FEB 1910"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS12_5(self):
        #Mom barely too old
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1950
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US12: INDI @I3@: Birthdate 13 FEB 2010 occurs more than 60 years after mother's birthday: 13 FEB 1950"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS12_6(self):
        #Mom barely young enough
        testFile = '''
        0 @I1@ INDI
        1 NAME` Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1950
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@

        0 TRLR
        '''
        expectedOutput = "US12"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US13_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US13 Tests (Siblings spacing)
    def testUS13_1(self):
        # Normal family (multiple siblings with spaced out birthdays) no errors should occur
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 18 JUN 2012
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "US13"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS13_2(self):
        # Twins born on same day - no errors should occur
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "US13"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS13_3(self):
        # Twins born 1 day apart - no error should occur
        testFile = '''
                0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 14 FEB 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "US13"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)
    
    def testUS13_4(self):
        # Same as test 3, but order of sibling births is switched
        testFile = '''
                0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "US13"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)
    
    def testUS13_5(self):
        # Children born 2 days apart - error should occur
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 15 FEB 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "ANOMALY: US13: INDI @I3@: Birthdate 13 FEB 2010 occurs within 2 days to 8 months of sibling @I4@: 15 FEB 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

        # expectedOutput = "ANOMALY: US13: INDI @I4@: Birthdate 15 FEB 2010 occurs within 2 days to 8 months of sibling @I3@: 13 FEB 2010"
        # self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS13_6(self):
        # Same as test 5, but order of sibling births is switched
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 11 FEB 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "ANOMALY: US13: INDI @I4@: Birthdate 11 FEB 2010 occurs within 2 days to 8 months of sibling @I3@: 13 FEB 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS13_7(self):
        # Children born 8 months apart - no error should occur
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 14 OCT 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "US13"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS13_8(self):
        #  Children born within 8 months of each other - error should occur
        testFile = '''
                0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 22 JUL 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 OCT 2019

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@

        0 TRLR
        '''

        expectedOutput = "ANOMALY: US13: INDI @I3@: Birthdate 13 FEB 2010 occurs within 2 days to 8 months of sibling @I4@: 22 JUL 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS13_9(self):
        # Multiple siblings born within 8 months of each other - errors should occur
        testFile = '''
        0 @I1@ INDI
        1 NAME Dick
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1980
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 14 FEB 1978
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Cathy
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 2010
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Jerry
        1 SEX M
        1 BIRT
        2 DATE 12 FEB 2010
        1 FAMC @F1@

        0 @I5@ INDI
        1 NAME John
        1 SEX M
        1 BIRT
        2 DATE 1 MAY 2010
        1 FAMC @F1@

        0 @I6@ INDI
        1 NAME Polly
        1 SEX F
        1 BIRT
        2 DATE 12 OCT 2010
        1 FAMC @F1@

        0 @I7@ INDI
        1 NAME Elizabeth
        1 SEX F
        1 BIRT
        2 DATE 8 JAN 2011
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 2005
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@

        0 TRLR
        '''

        expectedOutput = "ANOMALY: US13: INDI @I3@: Birthdate 13 FEB 2010 occurs within 2 days to 8 months of sibling @I5@: 1 MAY 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

        expectedOutput = "ANOMALY: US13: INDI @I3@: Birthdate 13 FEB 2010 occurs within 2 days to 8 months of sibling @I6@: 12 OCT 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

        expectedOutput = "ANOMALY: US13: INDI @I4@: Birthdate 12 FEB 2010 occurs within 2 days to 8 months of sibling @I5@: 1 MAY 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

        expectedOutput = "ANOMALY: US13: INDI @I4@: Birthdate 12 FEB 2010 occurs within 2 days to 8 months of sibling @I6@: 12 OCT 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

        expectedOutput = "ANOMALY: US13: INDI @I5@: Birthdate 1 MAY 2010 occurs within 2 days to 8 months of sibling @I6@: 12 OCT 2010"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

        expectedOutput = "ANOMALY: US13: INDI @I6@: Birthdate 12 OCT 2010 occurs within 2 days to 8 months of sibling @I7@: 8 JAN 2011"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US14_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US14 Tests (Multiple births <= 5)
    def testUS14_1(self):
        # 6 children born on same day. Error should occur
        testFile = '''
        0 HEAD

        0 @I1@ INDI
        1 NAME husband
        1 SEX M
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1991

        0 @I2@ INDI
        1 NAME wife
        1 SEX F
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1990
        
        0 @I3@ INDI
        1 NAME child1
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I4@ INDI
        1 NAME child2
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I5@ INDI
        1 NAME child3
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I6@ INDI
        1 NAME child4
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I7@ INDI
        1 NAME child5
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I8@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US14: FAM @F1@: More than 5 children born at the same time: ['@I3@', '@I4@', '@I5@', '@I6@', '@I7@', '@I8@']"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS14_2(self):
        # 5 children born on same day. No error should occur
        testFile = '''
        0 HEAD

        0 @I1@ INDI
        1 NAME husband
        1 SEX M
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1991

        0 @I2@ INDI
        1 NAME wife
        1 SEX F
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1990
        
        0 @I3@ INDI
        1 NAME child1
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I4@ INDI
        1 NAME child2
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I5@ INDI
        1 NAME child3
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I6@ INDI
        1 NAME child4
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I7@ INDI
        1 NAME child5
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I8@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@

        0 TRLR
        '''
        expectedOutput = "US14"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS14_3(self):
        # 6 children born with 1 day difference. Error should occur.
        testFile = '''
        0 HEAD

        0 @I1@ INDI
        1 NAME husband
        1 SEX M
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1991

        0 @I2@ INDI
        1 NAME wife
        1 SEX F
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1990
        
        0 @I3@ INDI
        1 NAME child1
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I4@ INDI
        1 NAME child2
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 9 JAN 2011

        0 @I5@ INDI
        1 NAME child3
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I6@ INDI
        1 NAME child4
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 9 JAN 2011

        0 @I7@ INDI
        1 NAME child5
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011

        0 @I8@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 9 JAN 2011
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US14: FAM @F1@: More than 5 children born at the same time: ['@I3@', '@I4@', '@I5@', '@I6@', '@I7@', '@I8@']"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    
    def testUS14_4(self):
        # 7 children. 4 born close to eachother. No error should occur.
        testFile = '''
        0 HEAD

        0 @I1@ INDI
        1 NAME husband
        1 SEX M
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1991

        0 @I2@ INDI
        1 NAME wife
        1 SEX F
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1990
        
        0 @I3@ INDI
        1 NAME child1
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I4@ INDI
        1 NAME child2
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I5@ INDI
        1 NAME child3
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I6@ INDI
        1 NAME child4
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I7@ INDI
        1 NAME child5
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2013

        0 @I8@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2012

        0 @I9@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@
        1 CHIL @I9@
        

        0 TRLR
        '''
        expectedOutput = "US14"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS14_5(self):
        # 7 children. 6 born close to eachother. Error should occur.
        testFile = '''
        0 HEAD

        0 @I1@ INDI
        1 NAME husband
        1 SEX M
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1991

        0 @I2@ INDI
        1 NAME wife
        1 SEX F
        1 FAMS @F1@
        1 BIRT
        2 DATE 8 JAN 1990
        
        0 @I3@ INDI
        1 NAME child1
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I4@ INDI
        1 NAME child2
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I5@ INDI
        1 NAME child3
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I6@ INDI
        1 NAME child4
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I7@ INDI
        1 NAME child5
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I8@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2017

        0 @I9@ INDI
        1 NAME child6
        1 SEX F
        1 FAMC @F1@
        1 BIRT
        2 DATE 8 JAN 2011
        
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@
        1 CHIL @I9@
        

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US14: FAM @F1@: More than 5 children born at the same time: ['@I3@', '@I4@', '@I5@', '@I6@', '@I7@', '@I8@']"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

class US15_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US15 Tests (Fewer than 15 siblings)
    def testUS15_1(self):
        #exactly 15 siblings
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 2
        1 DATE 27 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME 1
        2 GIVN 1
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME 2
        2 GIVN 2
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME 3
        2 GIVN 3
        1 FAMC @F1@
        0 @I7@ INDI
        1 NAME 4
        2 GIVN 4
        1 FAMC @F1@
        0 @I8@ INDI
        1 NAME 5
        2 GIVN 5
        1 FAMC @F1@
        0 @I9@ INDI
        1 NAME 6
        2 GIVN 6
        1 FAMC @F1@
        0 @I10@ INDI
        1 NAME 7
        2 GIVN 7
        1 FAMC @F1@
        0 @I11@ INDI
        1 NAME 8
        2 GIVN 8
        1 FAMC @F1@
        0 @I12@ INDI
        1 NAME 9
        2 GIVN 9
        1 FAMC @F1@
        0 @I13@ INDI
        1 NAME 0
        2 GIVN 0
        1 FAMC @F1@
        0 @I14@ INDI
        1 NAME 10
        2 GIVN 10
        1 FAMC @F1@
        0 @I15@ INDI
        1 NAME 11
        2 GIVN 11
        1 FAMC @F1@
        0 @I16@ INDI
        1 NAME 12
        2 GIVN 12
        1 FAMC @F1@
        0 @I17@ INDI
        1 NAME 13
        2 GIVN 13
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@
        1 CHIL @I9@
        1 CHIL @I10@
        1 CHIL @I11@
        1 CHIL @I12@
        1 CHIL @I13@
        1 CHIL @I14@
        1 CHIL @I15@
        1 CHIL @I16@
        1 CHIL @I17@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US15: FAM @F1@: Family contains 15 or more siblings"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS15_2(self):
        #exactly 15 siblings
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 2
        1 DATE 27 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME 1
        2 GIVN 1
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME 2
        2 GIVN 2
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME 3
        2 GIVN 3
        1 FAMC @F1@
        0 @I7@ INDI
        1 NAME 4
        2 GIVN 4
        1 FAMC @F1@
        0 @I8@ INDI
        1 NAME 5
        2 GIVN 5
        1 FAMC @F1@
        0 @I9@ INDI
        1 NAME 6
        2 GIVN 6
        1 FAMC @F1@
        0 @I10@ INDI
        1 NAME 7
        2 GIVN 7
        1 FAMC @F1@
        0 @I11@ INDI
        1 NAME 8
        2 GIVN 8
        1 FAMC @F1@
        0 @I12@ INDI
        1 NAME 9
        2 GIVN 9
        1 FAMC @F1@
        0 @I13@ INDI
        1 NAME 0
        2 GIVN 0
        1 FAMC @F1@
        0 @I14@ INDI
        1 NAME 10
        2 GIVN 10
        1 FAMC @F1@
        0 @I15@ INDI
        1 NAME 11
        2 GIVN 11
        1 FAMC @F1@
        0 @I16@ INDI
        1 NAME 12
        2 GIVN 12
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@
        1 CHIL @I9@
        1 CHIL @I10@
        1 CHIL @I11@
        1 CHIL @I12@
        1 CHIL @I13@
        1 CHIL @I14@
        1 CHIL @I15@
        1 CHIL @I16@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US15"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS15_3(self):
        #more than 15
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 2
        1 DATE 27 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME 1
        2 GIVN 1
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME 2
        2 GIVN 2
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME 3
        2 GIVN 3
        1 FAMC @F1@
        0 @I7@ INDI
        1 NAME 4
        2 GIVN 4
        1 FAMC @F1@
        0 @I8@ INDI
        1 NAME 5
        2 GIVN 5
        1 FAMC @F1@
        0 @I9@ INDI
        1 NAME 6
        2 GIVN 6
        1 FAMC @F1@
        0 @I10@ INDI
        1 NAME 7
        2 GIVN 7
        1 FAMC @F1@
        0 @I11@ INDI
        1 NAME 8
        2 GIVN 8
        1 FAMC @F1@
        0 @I12@ INDI
        1 NAME 9
        2 GIVN 9
        1 FAMC @F1@
        0 @I13@ INDI
        1 NAME 0
        2 GIVN 0
        1 FAMC @F1@
        0 @I14@ INDI
        1 NAME 10
        2 GIVN 10
        1 FAMC @F1@
        0 @I15@ INDI
        1 NAME 11
        2 GIVN 11
        1 FAMC @F1@
        0 @I16@ INDI
        1 NAME 12
        2 GIVN 12
        1 FAMC @F1@
        0 @I17@ INDI
        1 NAME 13
        2 GIVN 13
        1 FAMC @F1@
        0 @I18@ INDI
        1 NAME 14
        2 GIVN 14
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@
        1 CHIL @I9@
        1 CHIL @I10@
        1 CHIL @I11@
        1 CHIL @I12@
        1 CHIL @I13@
        1 CHIL @I14@
        1 CHIL @I15@
        1 CHIL @I16@
        1 CHIL @I17@
        1 CHIL @I18@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US15: FAM @F1@: Family contains 15 or more siblings"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS15_4(self):
        #more than 15
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 2
        1 DATE 27 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME 1
        2 GIVN 1
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME 2
        2 GIVN 2
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME 3
        2 GIVN 3
        1 FAMC @F1@
        0 @I7@ INDI
        1 NAME 4
        2 GIVN 4
        1 FAMC @F1@
        0 @I8@ INDI
        1 NAME 5
        2 GIVN 5
        1 FAMC @F1@
        0 @I9@ INDI
        1 NAME 6
        2 GIVN 6
        1 FAMC @F1@
        0 @I10@ INDI
        1 NAME 7
        2 GIVN 7
        1 FAMC @F1@
        0 @I11@ INDI
        1 NAME 8
        2 GIVN 8
        1 FAMC @F1@
        0 @I12@ INDI
        1 NAME 9
        2 GIVN 9
        1 FAMC @F1@
        0 @I13@ INDI
        1 NAME 0
        2 GIVN 0
        1 FAMC @F1@
        0 @I14@ INDI
        1 NAME 10
        2 GIVN 10
        1 FAMC @F1@
        0 @I15@ INDI
        1 NAME 11
        2 GIVN 11
        1 FAMC @F1@
        0 @I16@ INDI
        1 NAME 12
        2 GIVN 12
        1 FAMC @F1@
        0 @I17@ INDI
        1 NAME 13
        2 GIVN 13
        1 FAMC @F1@
        0 @I18@ INDI
        1 NAME 14
        2 GIVN 14
        1 FAMC @F1@
        0 @I19@ INDI
        1 NAME 14
        2 GIVN 14
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 CHIL @I7@
        1 CHIL @I8@
        1 CHIL @I9@
        1 CHIL @I10@
        1 CHIL @I11@
        1 CHIL @I12@
        1 CHIL @I13@
        1 CHIL @I14@
        1 CHIL @I15@
        1 CHIL @I16@
        1 CHIL @I17@
        1 CHIL @I18@
        1 CHIL @I19@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US15: FAM @F1@: Family contains 15 or more siblings"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS15_5(self):
        #more than 15
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 2
        1 DATE 27 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@

        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US15"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    

class US16_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US16 Tests (Male last names)
    def testUS16_1(self):
        #no problem
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 2
        1 DATE 27 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@

        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US16"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS16_2(self):
        #son different last name
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 4
        1 DATE 29 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Joe /Bill/
        2 GIVN Joe
        2 SURN Bill
        2 _MARNM Bill
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Marie /Bill/
        2 GIVN Marie
        2 SURN Bill
        2 _MARNM Bill
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joey /Ball/
        2 GIVN Joey
        2 SURN Ball
        2 _MARNM Ball
        1 SEX M
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US16: FAM @F1@: Individual Joey /Ball/ has a different last name from his family /Bill/"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS16_3(self):
        #daughter different last name
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 4
        1 DATE 29 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Joe /Bill/
        2 GIVN Joe
        2 SURN Bill
        2 _MARNM Bill
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Marie /Bill/
        2 GIVN Marie
        2 SURN Bill
        2 _MARNM Bill
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joey /Ball/
        2 GIVN Joey
        2 SURN Ball
        2 _MARNM Ball
        1 SEX F
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US16"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS16_4(self):
        #son different last name and daughter different last name
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 4
        1 DATE 29 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Joe /Bill/
        2 GIVN Joe
        2 SURN Bill
        2 _MARNM Bill
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Marie /Bill/
        2 GIVN Marie
        2 SURN Bill
        2 _MARNM Bill
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joey /Ball/
        2 GIVN Joey
        2 SURN Ball
        2 _MARNM Ball
        1 SEX M
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Jill /Ball/
        2 GIVN Jill
        2 SURN Ball
        2 _MARNM Ball
        1 SEX F
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US16: FAM @F1@: Individual Joey /Ball/ has a different last name from his family /Bill/"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS16_5(self):
        #two daughters diff last name
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 4
        1 DATE 29 OCT 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Joe /Bill/
        2 GIVN Joe
        2 SURN Bill
        2 _MARNM Bill
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Marie /Bill/
        2 GIVN Marie
        2 SURN Bill
        2 _MARNM Bill
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Joey /Ball/
        2 GIVN Joey
        2 SURN Ball
        2 _MARNM Ball
        1 SEX F
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Jill /Ball/
        2 GIVN Jill
        2 SURN Ball
        2 _MARNM Ball
        1 SEX F
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US16"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US17_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US17 Tests (No marriages to descendants)
    def testUS17_1(self):
        # Normal family, no errors should occur
        # need to add more children/families
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME John
        2 GIVN John
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Jane
        2 GIVN Jane
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Barry
        2 GIVN Barry
        1 SEX M
        1 FAMS @F3@
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Beth
        2 GIVN Beth
        1 SEX F
        1 DEAT Y
        1 FAMS @F4@
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Bob
        2 GIVN Bob
        1 SEX M
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME Brandi
        2 GIVN Brandi
        1 SEX F
        1 FAMS @F3@
        0 @I7@ INDI
        1 NAME Braxton
        2 GIVN Braxton
        1 SEX M
        1 FAMS @F4@
        1 FAMS @F5@
        0 @I8@ INDI
        1 NAME Marty
        2 GIVN Marty
        1 SEX M
        1 FAMC @F3@
        0 @I9@ INDI
        1 NAME Mary
        2 GIVN Mary
        1 SEX F
        1 FAMS @F7@
        1 FAMC @F3@
        0 @I10@ INDI
        1 NAME Mandy
        2 GIVN Mandy
        1 SEX F
        1 FAMC @F4@
        0 @I11@ INDI
        1 NAME Mike
        2 GIVN Mike
        1 SEX M
        1 FAMS @F6@
        1 FAMC @F4@
        0 @I12@ INDI
        1 NAME Bwanda
        2 GIVN Bwanda
        1 SEX F
        1 FAMS @F5@
        0 @I13@ INDI
        1 NAME Mitchell
        2 GIVN Mitchell
        1 SEX M
        1 FAMC @F5@
        0 @I14@ INDI
        1 NAME Michelle
        2 GIVN Michelle
        1 SEX F
        1 FAMS @F6@
        0 @I15@ INDI
        1 NAME Frank
        2 GIVN Frank
        1 SEX M
        1 FAMC @F6@
        0 @I16@ INDI
        1 NAME Francine
        2 GIVN Francine
        1 SEX F
        1 FAMC @F7@
        0 @I17@ INDI
        1 NAME Mark
        2 GIVN Mark
        1 SEX M
        1 FAMS @F7@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F3@ FAM
        1 HUSB @I3@
        1 WIFE @I6@
        1 CHIL @I8@
        1 CHIL @I9@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F4@ FAM
        1 HUSB @I7@
        1 WIFE @I4@
        1 CHIL @I10@
        1 CHIL @I11@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F5@ FAM
        1 HUSB @I7@
        1 WIFE @I12@
        1 CHIL @I13@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F6@ FAM
        1 HUSB @I11@
        1 WIFE @I14@
        1 CHIL @I15@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F7@ FAM
        1 HUSB @I17@
        1 WIFE @I9@
        1 CHIL @I16@
        1 _CURRENT N
        1 _PRIMARY N
        0 TRLR
        '''
        expectedOutput = "US17"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS17_2(self):
        # wife marrying a living child, error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME John
        2 GIVN John
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Jane
        2 GIVN Jane
        1 SEX F
        1 FAMS @F1@
        1 FAMS @F3@
        0 @I3@ INDI
        1 NAME Barry
        2 GIVN Barry
        1 SEX M
        1 FAMS @F3@
        1 FAMS @F4@
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Beth
        2 GIVN Beth
        1 SEX F
        1 DEAT Y
        1 FAMS @F5@
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Bob
        2 GIVN Bob
        1 SEX M
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME Brandi
        2 GIVN Brandi
        1 SEX F
        1 FAMS @F4@
        0 @I7@ INDI
        1 NAME Braxton
        2 GIVN Braxton
        1 SEX M
        1 FAMS @F5@
        1 FAMS @F6@
        0 @I8@ INDI
        1 NAME Marty
        2 GIVN Marty
        1 SEX M
        1 FAMC @F4@
        0 @I9@ INDI
        1 NAME Mary
        2 GIVN Mary
        1 SEX F
        1 FAMS @F8@
        1 FAMC @F4@
        0 @I10@ INDI
        1 NAME Mandy
        2 GIVN Mandy
        1 SEX F
        1 FAMC @F5@
        0 @I11@ INDI
        1 NAME Mike
        2 GIVN Mike
        1 SEX M
        1 FAMS @F7@
        1 FAMC @F5@
        0 @I12@ INDI
        1 NAME Bwanda
        2 GIVN Bwanda
        1 SEX F
        1 FAMS @F6@
        0 @I13@ INDI
        1 NAME Mitchell
        2 GIVN Mitchell
        1 SEX M
        1 FAMC @F6@
        0 @I14@ INDI
        1 NAME Michelle
        2 GIVN Michelle
        1 SEX F
        1 FAMS @F7@
        0 @I15@ INDI
        1 NAME Frank
        2 GIVN Frank
        1 SEX M
        1 FAMC @F7@
        0 @I16@ INDI
        1 NAME Francine
        2 GIVN Francine
        1 SEX F
        1 FAMC @F8@
        0 @I17@ INDI
        1 NAME Mark
        2 GIVN Mark
        1 SEX M
        1 FAMS @F8@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F3@ FAM
        1 HUSB @I3@
        1 WIFE @I2@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F4@ FAM
        1 HUSB @I3@
        1 WIFE @I6@
        1 CHIL @I8@
        1 CHIL @I9@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F5@ FAM
        1 HUSB @I7@
        1 WIFE @I4@
        1 CHIL @I10@
        1 CHIL @I11@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F6@ FAM
        1 HUSB @I7@
        1 WIFE @I12@
        1 CHIL @I13@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F7@ FAM
        1 HUSB @I11@
        1 WIFE @I14@
        1 CHIL @I15@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F8@ FAM
        1 HUSB @I17@
        1 WIFE @I9@
        1 CHIL @I16@
        1 _CURRENT N
        1 _PRIMARY N
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US17: INDI @I2@: Individual has married their decendent @I3@ in FAM @F3@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS17_3(self):
        # Husband marrying a grandchild, error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME John
        2 GIVN John
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Jane
        2 GIVN Jane
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Barry
        2 GIVN Barry
        1 SEX M
        1 FAMS @F3@
        1 FAMS @F4@
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Beth
        2 GIVN Beth
        1 SEX F
        1 DEAT Y
        1 FAMS @F5@
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Bob
        2 GIVN Bob
        1 SEX M
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME Brandi
        2 GIVN Brandi
        1 SEX F
        1 FAMS @F4@
        0 @I7@ INDI
        1 NAME Braxton
        2 GIVN Braxton
        1 SEX M
        1 FAMS @F5@
        1 FAMS @F6@
        0 @I8@ INDI
        1 NAME Marty
        2 GIVN Marty
        1 SEX M
        1 FAMC @F4@
        0 @I9@ INDI
        1 NAME Mary
        2 GIVN Mary
        1 SEX F
        1 FAMS @F8@
        1 FAMC @F4@
        0 @I10@ INDI
        1 NAME Mandy
        2 GIVN Mandy
        1 SEX F
        1 FAMC @F5@
        0 @I11@ INDI
        1 NAME Mike
        2 GIVN Mike
        1 SEX M
        1 FAMS @F7@
        1 FAMC @F5@
        0 @I12@ INDI
        1 NAME Bwanda
        2 GIVN Bwanda
        1 SEX F
        1 FAMS @F6@
        0 @I13@ INDI
        1 NAME Mitchell
        2 GIVN Mitchell
        1 SEX M
        1 FAMC @F6@
        0 @I14@ INDI
        1 NAME Michelle
        2 GIVN Michelle
        1 SEX F
        1 FAMS @F7@
        0 @I15@ INDI
        1 NAME Frank
        2 GIVN Frank
        1 SEX M
        1 FAMC @F7@
        0 @I16@ INDI
        1 NAME Francine
        2 GIVN Francine
        1 SEX F
        1 FAMS @F3@
        1 FAMC @F8@
        0 @I17@ INDI
        1 NAME Mark
        2 GIVN Mark
        1 SEX M
        1 FAMS @F8@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F3@ FAM
        1 HUSB @I3@
        1 WIFE @I16@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F4@ FAM
        1 HUSB @I3@
        1 WIFE @I6@
        1 CHIL @I8@
        1 CHIL @I9@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F5@ FAM
        1 HUSB @I7@
        1 WIFE @I4@
        1 CHIL @I10@
        1 CHIL @I11@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F6@ FAM
        1 HUSB @I7@
        1 WIFE @I12@
        1 CHIL @I13@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F7@ FAM
        1 HUSB @I11@
        1 WIFE @I14@
        1 CHIL @I15@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F8@ FAM
        1 HUSB @I17@
        1 WIFE @I9@
        1 CHIL @I16@
        1 _CURRENT N
        1 _PRIMARY N
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US17: INDI @I3@: Individual has married their decendent @I16@ in FAM @F3@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS17_4(self):
        # marrying a great grandchild, error should occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME John
        2 GIVN John
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Jane
        2 GIVN Jane
        1 SEX F
        1 FAMS @F1@
        1 FAMS @F3@
        0 @I3@ INDI
        1 NAME Barry
        2 GIVN Barry
        1 SEX M
        1 FAMS @F4@
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Beth
        2 GIVN Beth
        1 SEX F
        1 DEAT Y
        1 FAMS @F5@
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Bob
        2 GIVN Bob
        1 SEX M
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME Brandi
        2 GIVN Brandi
        1 SEX F
        1 FAMS @F4@
        0 @I7@ INDI
        1 NAME Braxton
        2 GIVN Braxton
        1 SEX M
        1 FAMS @F5@
        1 FAMS @F6@
        0 @I8@ INDI
        1 NAME Marty
        2 GIVN Marty
        1 SEX M
        1 FAMC @F4@
        0 @I9@ INDI
        1 NAME Mary
        2 GIVN Mary
        1 SEX F
        1 FAMS @F8@
        1 FAMC @F4@
        0 @I10@ INDI
        1 NAME Mandy
        2 GIVN Mandy
        1 SEX F
        1 FAMC @F5@
        0 @I11@ INDI
        1 NAME Mike
        2 GIVN Mike
        1 SEX M
        1 FAMS @F7@
        1 FAMC @F5@
        0 @I12@ INDI
        1 NAME Bwanda
        2 GIVN Bwanda
        1 SEX F
        1 FAMS @F6@
        0 @I13@ INDI
        1 NAME Mitchell
        2 GIVN Mitchell
        1 SEX M
        1 FAMC @F6@
        0 @I14@ INDI
        1 NAME Michelle
        2 GIVN Michelle
        1 SEX F
        1 FAMS @F7@
        0 @I15@ INDI
        1 NAME Frank
        2 GIVN Frank
        1 SEX M
        1 FAMS @F3@
        1 FAMC @F7@
        0 @I16@ INDI
        1 NAME Francine
        2 GIVN Francine
        1 SEX F
        1 FAMC @F8@
        0 @I17@ INDI
        1 NAME Mark
        2 GIVN Mark
        1 SEX M
        1 FAMS @F8@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F3@ FAM
        1 HUSB @I15@
        1 WIFE @I2@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F4@ FAM
        1 HUSB @I3@
        1 WIFE @I6@
        1 CHIL @I8@
        1 CHIL @I9@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F5@ FAM
        1 HUSB @I7@
        1 WIFE @I4@
        1 CHIL @I10@
        1 CHIL @I11@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F6@ FAM
        1 HUSB @I7@
        1 WIFE @I12@
        1 CHIL @I13@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F7@ FAM
        1 HUSB @I11@
        1 WIFE @I14@
        1 CHIL @I15@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F8@ FAM
        1 HUSB @I17@
        1 WIFE @I9@
        1 CHIL @I16@
        1 _CURRENT N
        1 _PRIMARY N
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US17: INDI @I2@: Individual has married their decendent @I15@ in FAM @F3@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS17_5(self):
        # Marrying a non-blood decendent (child of an in-law), error should not occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME John
        2 GIVN John
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME Jane
        2 GIVN Jane
        1 SEX F
        1 FAMS @F1@
        1 FAMS @F3@
        0 @I3@ INDI
        1 NAME Barry
        2 GIVN Barry
        1 SEX M
        1 FAMS @F4@
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Beth
        2 GIVN Beth
        1 SEX F
        1 DEAT Y
        1 FAMS @F5@
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Bob
        2 GIVN Bob
        1 SEX M
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME Brandi
        2 GIVN Brandi
        1 SEX F
        1 FAMS @F4@
        0 @I7@ INDI
        1 NAME Braxton
        2 GIVN Braxton
        1 SEX M
        1 FAMS @F5@
        1 FAMS @F6@
        0 @I8@ INDI
        1 NAME Marty
        2 GIVN Marty
        1 SEX M
        1 FAMC @F4@
        0 @I9@ INDI
        1 NAME Mary
        2 GIVN Mary
        1 SEX F
        1 FAMS @F8@
        1 FAMC @F4@
        0 @I10@ INDI
        1 NAME Mandy
        2 GIVN Mandy
        1 SEX F
        1 FAMC @F5@
        0 @I11@ INDI
        1 NAME Mike
        2 GIVN Mike
        1 SEX M
        1 FAMS @F7@
        1 FAMC @F5@
        0 @I12@ INDI
        1 NAME Bwanda
        2 GIVN Bwanda
        1 SEX F
        1 FAMS @F6@
        0 @I13@ INDI
        1 NAME Mitchell
        2 GIVN Mitchell
        1 SEX M
        1 FAMS @F3@
        1 FAMC @F6@
        0 @I14@ INDI
        1 NAME Michelle
        2 GIVN Michelle
        1 SEX F
        1 FAMS @F7@
        0 @I15@ INDI
        1 NAME Frank
        2 GIVN Frank
        1 SEX M
        1 FAMC @F7@
        0 @I16@ INDI
        1 NAME Francine
        2 GIVN Francine
        1 SEX F
        1 FAMC @F8@
        0 @I17@ INDI
        1 NAME Mark
        2 GIVN Mark
        1 SEX M
        1 FAMS @F8@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F3@ FAM
        1 HUSB @I13@
        1 WIFE @I2@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F4@ FAM
        1 HUSB @I3@
        1 WIFE @I6@
        1 CHIL @I8@
        1 CHIL @I9@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F5@ FAM
        1 HUSB @I7@
        1 WIFE @I4@
        1 CHIL @I10@
        1 CHIL @I11@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F6@ FAM
        1 HUSB @I7@
        1 WIFE @I12@
        1 CHIL @I13@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F7@ FAM
        1 HUSB @I11@
        1 WIFE @I14@
        1 CHIL @I15@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F8@ FAM
        1 HUSB @I17@
        1 WIFE @I9@
        1 CHIL @I16@
        1 _CURRENT N
        1 _PRIMARY N
        0 TRLR
        '''
        expectedOutput = "US17"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS17_6(self):
        # Marrying a child in-law, error should not occur
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME John
        2 GIVN John
        1 SEX M
        1 FAMS @F1@
        1 FAMS @F2@
        0 @I2@ INDI
        1 NAME Jane
        2 GIVN Jane
        1 SEX F
        1 FAMS @F2@
        0 @I3@ INDI
        1 NAME Barry
        2 GIVN Barry
        1 SEX M
        1 FAMS @F4@
        1 FAMC @F2@
        0 @I4@ INDI
        1 NAME Beth
        2 GIVN Beth
        1 SEX F
        1 DEAT Y
        1 FAMS @F5@
        1 FAMC @F2@
        0 @I5@ INDI
        1 NAME Bob
        2 GIVN Bob
        1 SEX M
        1 FAMC @F2@
        0 @I6@ INDI
        1 NAME Brandi
        2 GIVN Brandi
        1 SEX F
        1 FAMS @F1@
        1 FAMS @F4@
        0 @I7@ INDI
        1 NAME Braxton
        2 GIVN Braxton
        1 SEX M
        1 FAMS @F5@
        1 FAMS @F6@
        0 @I8@ INDI
        1 NAME Marty
        2 GIVN Marty
        1 SEX M
        1 FAMC @F4@
        0 @I9@ INDI
        1 NAME Mary
        2 GIVN Mary
        1 SEX F
        1 FAMS @F8@
        1 FAMC @F4@
        0 @I10@ INDI
        1 NAME Mandy
        2 GIVN Mandy
        1 SEX F
        1 FAMC @F5@
        0 @I11@ INDI
        1 NAME Mike
        2 GIVN Mike
        1 SEX M
        1 FAMS @F7@
        1 FAMC @F5@
        0 @I12@ INDI
        1 NAME Bwanda
        2 GIVN Bwanda
        1 SEX F
        1 FAMS @F6@
        0 @I13@ INDI
        1 NAME Mitchell
        2 GIVN Mitchell
        1 SEX M
        1 FAMC @F6@
        0 @I14@ INDI
        1 NAME Michelle
        2 GIVN Michelle
        1 SEX F
        1 FAMS @F7@
        0 @I15@ INDI
        1 NAME Frank
        2 GIVN Frank
        1 SEX M
        1 FAMC @F7@
        0 @I16@ INDI
        1 NAME Francine
        2 GIVN Francine
        1 SEX F
        1 FAMC @F8@
        0 @I17@ INDI
        1 NAME Mark
        2 GIVN Mark
        1 SEX M
        1 FAMS @F8@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I6@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F4@ FAM
        1 HUSB @I3@
        1 WIFE @I6@
        1 CHIL @I8@
        1 CHIL @I9@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F2@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 _CURRENT N
        1 _PRIMARY N
        0 @F5@ FAM
        1 HUSB @I7@
        1 WIFE @I4@
        1 CHIL @I10@
        1 CHIL @I11@
        1 MARR
        1 DIV
        1 _CURRENT N
        1 _PRIMARY N
        0 @F6@ FAM
        1 HUSB @I7@
        1 WIFE @I12@
        1 CHIL @I13@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F7@ FAM
        1 HUSB @I11@
        1 WIFE @I14@
        1 CHIL @I15@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F8@ FAM
        1 HUSB @I17@
        1 WIFE @I9@
        1 CHIL @I16@
        1 _CURRENT N
        1 _PRIMARY N
        0 TRLR
        '''
        expectedOutput = "US17"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US18_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US18 Tests (Siblings should not marry)
    def testUS18_1(self):
        # Siblings marrying, error should occur
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Mike
        1 SEX M
        1 FAMC @F1@
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy
        1 SEX F
        1 FAMC @F1@
        1 FAMS @F2@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I4@
        '''
        expectedOutput = "ANOMALY: US18: FAM @F1@: Siblings @I3@ and @I4@ are married in FAM @F2@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS18_2(self):
        # Siblings not marrying, error should not occur
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Mike
        1 SEX M
        1 FAMC @F1@

        0 @I4@ INDI
        1 NAME Mandy
        1 SEX F
        1 FAMC @F1@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        '''
        expectedOutput = "US18"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS18_3(self):
        # Siblings marrying, but not eachother, error should not occur
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Mike
        1 SEX M
        1 FAMC @F1@
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy
        1 SEX F
        1 FAMC @F1@
        1 FAMS @F3@

        0 @I5@ INDI
        1 NAME Mitchell
        1 SEX M
        1 FAMS @F2@

        0 @I6@ INDI
        1 NAME Michelle
        1 SEX F
        1 FAMS @F3@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I5@

        0 @F3@ FAM
        1 HUSB @I4@
        1 WIFE @I6@
        
        0 TRLR
        '''
        expectedOutput = "US18"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS18_4(self):
        # Half-siblings marrying. Error should not occur.
        # (maybe it should. Would need to be another user story)
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 FAMS @F1@

        0 @I2_@ INDI
        1 NAME Mary2
        1 SEX F
        1 FAMS @F1_@

        0 @I3@ INDI
        1 NAME Mike
        1 SEX M
        1 FAMC @F1@
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy
        1 SEX F
        1 FAMC @F1_@
        1 FAMS @F2@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 DIV
        2 DATE 1 JAN 2000
        1 MARR
        2 DATE 1 JAN 1990

        0 @F1_@ FAM
        1 HUSB @I1@
        1 WIFE @I2_@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 2003

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I4@
        
        0 TRLR
        '''
        expectedOutput = "US18"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)
    
    def testUS18_5(self):
        # step-siblings marrying. Error should not occur.
        # (maybe it should. Would need to be another user story)
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 FAMS @F1@
        1 FAMS @F1__@

        0 @I1_@ INDI
        1 NAME John
        1 SEX M
        1 FAMS @F1_@
        1 FAMS @F1__@

        0 @I2_@ INDI
        1 NAME Mary2
        1 SEX F
        1 FAMS @F1_@

        0 @I3@ INDI
        1 NAME Mike
        1 SEX M
        1 FAMC @F1@
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy
        1 SEX F
        1 FAMC @F1_@
        1 FAMS @F2@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 DIV
        2 DATE 1 JAN 2000
        1 MARR
        2 DATE 1 JAN 1990

        0 @F1_@ FAM
        1 HUSB @I1_@
        1 WIFE @I2_@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 2003
        1 DIV
        2 DATE 1 JAN 2004

        0 @F1__@ FAM
        1 HUSB @I1_@
        1 WIFE @I2@
        1 MARR
        2 DATE 1 JAN 2006

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I4@
        
        0 TRLR
        '''
        expectedOutput = "US18"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US19_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US19 Tests (First cousins should not marry)
    def testUS19_1(self):
        # First cousins marrying, error should occur (simple)
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John(GF)
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary(GM)
        1 SEX F
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Mike(F1)
        1 SEX M
        1 FAMC @F1@
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy(M1)
        1 SEX F
        1 FAMS @F2@

        0 @I5@ INDI
        1 NAME Mitchell(F2)
        1 SEX M
        2 FAMC @F1@
        2 FAMS @F3@

        0 @I6@ INDI
        1 NAME Michelle(M2)
        1 SEX F
        1 FAMS @F3@

        0 NOTE Above sets up family with grandparents and parents. Next we set up their children who are first cousins.

        0 @I7@ INDI
        1 NAME Paul(C1)
        1 SEX M
        1 FAMC @F2@
        1 FAMS @F4@

        0 @I8@ INDI
        1 NAME Pauline(C2)
        1 SEX F
        1 FAMC @F3@
        1 FAMS @F4@

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I5@

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I4@
        1 CHIL @I7@

        0 @F3@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I8@

        0 @F4@ FAM
        1 HUSB @I7@
        1 WIFE @I8@

        0 TRLR
        '''
        expectedOutput = "ANOMALY: US19: FAM @F4@: Wife @I8@ is married to their first cousin Husband @I7@"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)
    def testUS19_2(self):
        # First cousins NOT marrying, error should NOT occur (simple)
        testFile = '''
        0 HEAD
        
        0 @I1@ INDI
        1 NAME John(GF)
        1 SEX M
        1 FAMS @F1@

        0 @I2@ INDI
        1 NAME Mary(GM)
        1 SEX F
        1 FAMS @F1@

        0 @I3@ INDI
        1 NAME Mike(F1)
        1 SEX M
        1 FAMC @F1@
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy(M1)
        1 SEX F
        1 FAMS @F2@

        0 @I5@ INDI
        1 NAME Mitchell(F2)
        1 SEX M
        2 FAMC @F1@
        2 FAMS @F3@

        0 @I6@ INDI
        1 NAME Michelle(M2)
        1 SEX F
        1 FAMS @F3@

        0 NOTE Above sets up family with grandparents and parents. Next we set up their children who are first cousins.

        0 @I7@ INDI
        1 NAME Paul(C1)
        1 SEX M
        1 FAMC @F2@
        

        0 @I8@ INDI
        1 NAME Pauline(C2)
        1 SEX F
        1 FAMC @F3@
    

        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I5@

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I4@
        1 CHIL @I7@

        0 @F3@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I8@

        0 TRLR
        '''
        expectedOutput = "US19"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)
    def testUS19_3(self):
        # Marriage without grandparents, error should NOT occur (and should not crash)
        testFile = '''
        0 HEAD

        0 @I3@ INDI
        1 NAME Mike(F1)
        1 SEX M
        1 FAMS @F2@

        0 @I4@ INDI
        1 NAME Mandy(M1)
        1 SEX F
        1 FAMS @F2@

        0 @I5@ INDI
        1 NAME Mitchell(F2)
        1 SEX M
        2 FAMS @F3@

        0 @I6@ INDI
        1 NAME Michelle(M2)
        1 SEX F
        1 FAMS @F3@

        0 NOTE Above sets up family with grandparents and parents. Next we set up their children who are first cousins.

        0 @I7@ INDI
        1 NAME Paul(C1)
        1 SEX M
        

        0 @I8@ INDI
        1 NAME Pauline(C2)
        1 SEX F

        0 @F2@ FAM
        1 HUSB @I3@
        1 WIFE @I4@
        1 CHIL @I7@

        0 @F3@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I8@

        0 TRLR
        '''
        expectedOutput = "US19"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US20_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US20 Tests (Aunts and uncles should not marry nieces and nephews)
    def testUS20_1(self):
        pass

class US21_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US21 Tests (Correct gender for role)
    def testUS21_1(self):
        pass

class US22_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US22 Tests (Unique IDs)
    def testUS22_1(self):
        pass

class US23_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US23 Tests (Unique name and birth date)
    def testUS23_1(self):
        # Two identical people
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR

        '''
        expectedOutput = "ANOMALY: US23: INDI @I1@: Individuals @I1@ and @I2@ have the same name and birthdate"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS23_2(self):
        # Three identical people
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR


        '''
        expectedOutput = "ANOMALY: US23: INDI @I1@: Individuals @I1@ and @I2@ have the same name and birthdate"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS23_3(self):
        # Two identical people
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F1@
        0 @I2@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I6@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 CHIL @I5@
        1 CHIL @I6@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR

        '''
        expectedOutput = "ANOMALY: US23: INDI @I1@: Individuals @I1@ and @I2@ have the same name and birthdate"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS23_4(self):
        # No problems
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

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 20 JUN 1990
        0 TRLR'''
        expectedOutput = "US23"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS23_5(self):
        # No problems
        testFile = '''
        0 HEAD
        0 @I1@ INDI
        1 NAME Andrew /Smith/
        2 GIVN Andrew
        2 SURN Smith
        1 SEX M
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@

        0 @I2@ INDI
        1 NAME Mary
        1 SEX F
        1 BIRT
        2 DATE 13 FEB 1981
        1 FAMC @F1@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 MARR
        2 DATE 14 FEB 1980
        1 DIV
        2 DATE 20 JUN 1990
        0 TRLR'''
        expectedOutput = "US23"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

class US24_tests(unittest.TestCase):
    run_gedcom_test = run_test
    # US24 Tests (Unique families by spouses)
    def testUS24_1(self):
        # Two identical marriages
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX M
        1 FAMS @F1@
        1 FAMC @F2@
        0 @I2@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F2@
        0 @I6@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F2@
        0 @I7@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 FAMS @F3@
        1 FAMC @F2@
        0 @I8@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F3@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F2@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I1@
        1 CHIL @I7@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F3@ FAM
        1 HUSB @I7@
        1 WIFE @I8@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "ANOMALY: US24: FAM @F1@: Families @F1@ and @F3@ have the same spouses and marriage date"
        self.run_gedcom_test(testFile, expectedOutput, self.assertIn)

    def testUS24_2(self):
        # Same husb diff wife
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX M
        1 FAMS @F1@
        1 FAMC @F2@
        0 @I2@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F2@
        0 @I6@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F2@
        0 @I7@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 FAMS @F3@
        1 FAMC @F2@
        0 @I8@ INDI
        1 NAME Andre /Pickle/
        2 GIVN Andre
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F3@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F2@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I1@
        1 CHIL @I7@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F3@ FAM
        1 HUSB @I7@
        1 WIFE @I8@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR

        '''
        expectedOutput = "US24"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS24_3(self):
        # same wife diff husb
        testFile = '''
                0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX M
        1 FAMS @F1@
        1 FAMC @F2@
        0 @I2@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F2@
        0 @I6@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F2@
        0 @I7@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 FAMS @F3@
        1 FAMC @F2@
        0 @I8@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F3@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F2@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I1@
        1 CHIL @I7@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F3@ FAM
        1 HUSB @I7@
        1 WIFE @I8@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US24"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS24_4(self):
        # No common spouses
        testFile = '''
        0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX M
        1 FAMS @F1@
        1 FAMC @F2@
        0 @I2@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F2@
        0 @I6@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F2@
        0 @I7@ INDI
        1 NAME Andrew Jr /Pickle/
        2 GIVN Andrew Jr
        2 SURN Pickle
        2 _MARNM Pickle
        1 FAMS @F3@
        1 FAMC @F2@
        0 @I8@ INDI
        1 NAME Andred /Pickle/
        2 GIVN Andred
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F3@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F2@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I1@
        1 CHIL @I7@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F3@ FAM
        1 HUSB @I7@
        1 WIFE @I8@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR

        '''
        expectedOutput = "US24"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)

    def testUS24_5(self):
        # Different last names
        testFile = '''
                0 HEAD
        1 SOUR Family Echo
        2 WWW http://www.familyecho.com/
        1 FILE Family 5
        1 DATE 19 NOV 2022
        1 DEST ANSTFILE
        1 GEDC
        2 VERS 5.5.1
        2 FORM LINEAGE-LINKED
        1 SUBM @I3@
        2 NAME jeweler-giggle-0f@icloud.com
        1 SUBN
        1 CHAR UTF-8
        0 @I1@ INDI
        1 NAME Andrew Sr /Pickle/
        2 GIVN Andrew Sr
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX M
        1 FAMS @F1@
        1 FAMC @F2@
        0 @I2@ INDI
        1 NAME Andrea /Pickle/
        2 GIVN Andrea
        2 SURN Pickle
        2 _MARNM Pickle
        1 SEX F
        1 FAMS @F1@
        0 @I3@ INDI
        1 NAME David /Pickle/
        2 GIVN David
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I4@ INDI
        1 NAME Andrew /Pickle/
        2 GIVN Andrew
        2 SURN Pickle
        2 _MARNM Pickle
        1 BIRT
        2 DATE 1 JAN 2000
        1 FAMC @F1@
        0 @I5@ INDI
        1 NAME
        1 SEX M
        1 FAMS @F2@
        0 @I6@ INDI
        1 NAME
        1 SEX F
        1 FAMS @F2@
        0 @I7@ INDI
        1 NAME Andrew Sr /Rick/
        2 GIVN Andrew Sr
        2 SURN Rick
        2 _MARNM Rick
        1 FAMS @F3@
        1 FAMC @F2@
        0 @I8@ INDI
        1 NAME Andre /Rick/
        2 GIVN Andre
        2 SURN Rick
        2 _MARNM Rick
        1 SEX F
        1 FAMS @F3@
        0 @F1@ FAM
        1 HUSB @I1@
        1 WIFE @I2@
        1 CHIL @I3@
        1 CHIL @I4@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F2@ FAM
        1 HUSB @I5@
        1 WIFE @I6@
        1 CHIL @I1@
        1 CHIL @I7@
        1 _CURRENT Y
        1 _PRIMARY Y
        0 @F3@ FAM
        1 HUSB @I7@
        1 WIFE @I8@
        1 MARR
        2 DATE 1 JAN 1999
        1 _CURRENT Y
        1 _PRIMARY Y
        0 TRLR
        '''
        expectedOutput = "US24"
        self.run_gedcom_test(testFile, expectedOutput, self.assertNotIn)
        
if __name__ == '__main__':
    unittest.main()
