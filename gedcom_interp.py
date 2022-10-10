# https://github.com/Big-Shark-Ball-Launchers/agile
# David Treder, Tyler Seliber, Andrew Capro
# I pledge my honor that I have abided by the Stevens Honor System

import sys
import datetime
from dateutil.relativedelta import relativedelta
from user_stories import stories


def isValidTag(tag):
    validTags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC",
                 "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV",
                 "DATE", "HEAD", "TRLR", "NOTE"]
    return tag in validTags


def formatLine(s):
    '''Returns list in format [level, tag, arguments]'''
    l = s.split()
    if (len(l) < 2):
        return [0, 'ERROR', '']
    level = int(l[0])
    tag = l[1]
    args = ' '.join(l[2:])
    if level == 0 and (args == "FAM" or args == "INDI"):
        # edge cases for INDI and FAM mean that the third element in s is the tag
        return [level, args, tag]
    return [level, tag, args]


def addElement(entry, elem, level):
    key = ""
    value = ""
    if (level[2] == "DATE" and (level[1] == "BIRT" or level[1] == "DEAT" or level[1] == "MARR" or level[1] == "DIV")):
        key = level[1] + " " + level[2]
        value = elem[2]
    elif (elem[1] == "BIRT" or elem[1] == "MARR" or elem[1] == "DIV"):
        return
    elif (elem[1] == "CHIL" or elem[1] == "FAMS"):
        if not elem[1] in entry:
            key = elem[1]
            value = [elem[2]]
        else:
            key = elem[1]
            value = entry[elem[1]] + [elem[2]]
    else:
        key = elem[1]
        value = elem[2]

    if key != "":
        entry[key] = value


def makeIndiAssumptions(indi):
    '''Fills in assumptions about the data.'''
    indi["AGE"] = calculateAge(indi)
    return indi


def makeFamAssumptions(fam, indi):
    '''Fills in assumptions about the data.'''
    fam["HUSB NAME"] = indiIDtoName(indi, fam["HUSB"])
    fam["WIFE NAME"] = indiIDtoName(indi, fam["WIFE"])
    return fam


def gedStringToDatetime(s):
    '''Converts a gedcom date string to a datetime object'''
    try:
        return datetime.datetime.strptime(s, '%d %b %Y')
    except ValueError:
        return datetime.datetime(1, 1, 1)  # default in case of error


def datetimeToString(d):
    '''Converts a datetime object to a string in the format of a gedcom date'''
    return d.strftime('%d %b %Y').upper()


def timedeltaToYears(d):
    '''converts a timedelta object to years'''
    return int(d.days/365.25)


def calculateAge(indi):
    '''returns age of individual based on birth and death dates. If no death date, use current time.'''
    if (indi["DEAT"] == "N"):
        end = datetime.datetime.now()
    else:
        end = gedStringToDatetime(indi["DEAT DATE"])
    return timedeltaToYears(end - gedStringToDatetime(indi["BIRT DATE"]))
    # return indi

def calculateAgeAtTime(date1, date2):
    return timedeltaToYears(gedStringToDatetime(date2) - gedStringToDatetime(date1))


def dictListToPrettyTable(d):
    '''converts a list of dictionarys to PrettyTable'''
    from prettytable import PrettyTable
    t = PrettyTable(d[0].keys())
    for i in d:
        t.add_row(i.values())
    return t


def indiIDtoName(indi, id):
    '''returns name of individual based on their id'''
    for i in indi:
        if i["INDI"] == id:
            return i["NAME"]
    return "NA"


def defaultIndi():
    '''returns a default individual dictionary'''
    return {
        "INDI": "NA",
        "NAME": "NA",
        "SEX": "NA",
        "BIRT DATE": "NA",
        "AGE": 0,
        "DEAT": "N",
        "DEAT DATE": "NA",
        "FAMC": "NA",
        "FAMS": []
    }


def defaultFam():
    '''returns a default family dictionary'''
    return {
        "FAM": "NA",
        "MARR DATE": "NA",
        "DIV DATE": "NA",
        "HUSB": "NA",
        "HUSB NAME": "NA",
        "WIFE": "NA",
        "WIFE NAME": "NA",
        "CHIL": []
    }


def findIndi(iId, list):
    for i in list:
        if (i["INDI"] == iId):
            return i


def findFam(fId, list):
    for f in list:
        if (f["FAM"] == fId):
            return f

def marriageRange(f, indi):
    '''Returns the range of dates between the start and end of a marriage.
    If the marraige never started, both values will be None.
    If the marraige never ended, the second value will be today.
    Marraige can end in death or divorce.'''
    if (f["MARR DATE"] == "NA"):
        start = None
    else:
        start = gedStringToDatetime(f["MARR DATE"])
    if f["DIV DATE"] != "NA":
        end = gedStringToDatetime(f["DIV DATE"])
    elif findIndi(f["HUSB"], indi)["DEAT"] == "Y":
        end = gedStringToDatetime(findIndi(f["HUSB"], indi)["DEAT DATE"])
    elif findIndi(f["WIFE"], indi)["DEAT"] == "Y":
        end = gedStringToDatetime(findIndi(f["WIFE"], indi)["DEAT DATE"])
    else:
        end = datetime.datetime.now()
    return (start, end)

def datetimeWithinRange(d, r):
    '''returns true if d is within the range r'''
    if (r[0] == None):
        return False
    if (r[1] == None):
        return d >= r[0]
    return d >= r[0] and d <= r[1]

def datetimeRangeOverlap(rl):
    '''returns true if any of the ranges in rl overlap'''
    for i in range(len(rl)):
        for j in range(len(rl)):
            # as long as we are not looking at the start of the same range
            # check if the start of the range is within the other range
            # if this is ever the case, the ranges overlap
            if (i != j):
                if (datetimeWithinRange(rl[j][0], rl[i])):
                    return True
    return False

def displayAnomaly(storyKey, **kwargs):
    '''prints a formatted error/anomaly message'''
    anomalyString = stories[storyKey]
    formattedAnaomalyString = anomalyString.format(**kwargs, story=storyKey)
    print(formattedAnaomalyString)


def main():
    if (len(sys.argv) <= 1):
        filename = 'full_family.ged'  # default file path
    else:
        filename = sys.argv[1]

    indi = []
    fam = []
    # keeps track of the tag of levels
    level = []
    indiFlag = False
    famFlag = False
    curr = defaultIndi()
    sawTRLR = False
    with open(filename, 'r') as f:
        for line in f:
            # print(f'--> {line}', end='')
            l = formatLine(line)
            valid = 'Y' if isValidTag(l[1]) else 'N'
            if isValidTag(l[1]):
                
                if (l[1] == "TRLR"):
                    break

                if (l[0] == 0):
                    level = [l[1], None, None]
                if (l[0] == 1):
                    level = [level[0], l[1], None]
                if (l[0] == 2):
                    level = [level[0], level[1], l[1]]

                if (indiFlag or famFlag) and l[0] == 0:
                    # if we reach the end of an individual or family, add it to the list
                    if (indiFlag):
                        indi.append(curr)
                    else:
                        fam.append(curr)
                if ((l[1] == 'INDI' or l[1] == 'FAM') and l[0] == 0):
                    curr = defaultIndi() if l[1] == 'INDI' else defaultFam()
                    addElement(curr, l, level)
                if (l[0] == 0):
                    indiFlag = True if l[1] == 'INDI' else False
                    famFlag = True if l[1] == 'FAM' else False
                if indiFlag or famFlag:
                    addElement(curr, l, level)

            # print(f'<-- {l[0]}|{l[1]}|{valid}|{l[2]}')
        if (indiFlag):
            indi.append(curr)
        else:
            fam.append(curr)

        indi = [makeIndiAssumptions(i) for i in indi]
        fam = [makeFamAssumptions(f, indi) for f in fam]
        print(fam)
        print(dictListToPrettyTable(sorted(indi, key=lambda x: x["INDI"])))
        print(dictListToPrettyTable(sorted(fam, key=lambda x: x["FAM"])))

        # Loop through each individual and family to check for errors/anomalies
        for i in indi:

            # US01
            currentDate = datetime.datetime.now()
            if (i["BIRT DATE"] != "NA" and gedStringToDatetime(i["BIRT DATE"]) > currentDate):
                displayAnomaly("US01", id=i["INDI"], date=i["BIRT DATE"],
                               dateType="BIRT", currentDate=datetimeToString(currentDate))
            if (i["DEAT DATE"] != "NA" and gedStringToDatetime(i["DEAT DATE"]) > currentDate):
                displayAnomaly("US01", id=i["INDI"], date=i["DEAT DATE"],
                               dateType="DEAT", currentDate=datetimeToString(currentDate))

            # US03
            if (i["AGE"] < 0):
                displayAnomaly(
                    "US03", id=i["INDI"], dDate=i["DEAT DATE"], bDate=i["BIRT DATE"])
                    
            # US07
            if (i["AGE"] > 150):
                displayAnomaly("US07", id=i["INDI"], age=i["AGE"])

            # US08
            anomalyFound = False
            family = findFam(i["FAMC"], fam)
            if (family != None):
                mDateStr = family["MARR DATE"]
                dDateStr = family["DIV DATE"]
                bDateStr = i["BIRT DATE"]
                if (mDateStr == "NA"): # born when parents were never married
                    anomalyFound = True
                elif (gedStringToDatetime(bDateStr) < gedStringToDatetime(mDateStr)): # born before marriage of parents
                    anomalyFound = True
                if (dDateStr != "NA" and gedStringToDatetime(bDateStr) > (gedStringToDatetime(dDateStr) + relativedelta(months=+9))): # born after 9 months of divorce of parents
                    anomalyFound = True
                if (anomalyFound):
                    displayAnomaly("US08", id=i["INDI"], bDate=bDateStr, mDate=mDateStr, dDate=dDateStr, famID = family["FAM"])

            # US09 - Birth before death of parents
            if (i["FAMC"] != "NA"):
                family = findFam(i["FAMC"], fam)
                husband = findIndi(family["HUSB"], indi)
                wife = findIndi(family["WIFE"], indi)
                husb_death = husband["DEAT DATE"]
                wife_death = wife["DEAT DATE"]
                if (husb_death != "NA"):
                    husb_effective_death = datetimeToString(gedStringToDatetime(husb_death) + relativedelta(months=+9))
                birth_date = i["BIRT DATE"]
                if ((wife_death != "NA" and calculateAgeAtTime(birth_date, wife_death) < 0) or (husb_death != "NA" and calculateAgeAtTime(birth_date, husb_effective_death)) < 0):
                    displayAnomaly("US09", id=i["INDI"], dDeath=husband["DEAT DATE"], mDeath=wife["DEAT DATE"], bDate=i["BIRT DATE"])

            # US10
            if(i["FAMS"]):
                for f in i["FAMS"]:
                    fam_ = findFam(f,fam)
                    bDate = i["BIRT DATE"]
                    marDate = fam_["MARR DATE"]
                    if(calculateAgeAtTime(bDate, marDate) < 14):
                        displayAnomaly("US10", id=i["INDI"], fam=fam_["FAM"], date=marDate)

            # US11 (no bigamy)
            if (len(i["FAMS"]) > 1):
                count = 0
                # list of ranges of marraiges for this individual
                mr = [marriageRange(findFam(f, fam), indi) for f in i["FAMS"]]
                if (datetimeRangeOverlap(mr)):
                    displayAnomaly("US11", id=i["INDI"], fams=i["FAMS"])

            

        for f in fam:

            # US01
            if (f["MARR DATE"] != "NA" and gedStringToDatetime(f["MARR DATE"]) > currentDate):
                displayAnomaly("US01", id=f["FAM"], date=f["MARR DATE"],
                               dateType="MARR", currentDate=datetimeToString(currentDate))
            if (f["DIV DATE"] != "NA" and gedStringToDatetime(f["DIV DATE"]) > currentDate):
                displayAnomaly("US01", id=f["FAM"], date=f["DIV DATE"],
                               dateType="DIV", currentDate=datetimeToString(currentDate))

            # US02
            husb = f["HUSB"]
            wife = f["WIFE"]
            husbIndi = findIndi(husb, indi)
            wifeIndi = findIndi(wife, indi)
            if (husbIndi and timedeltaToYears(gedStringToDatetime(f["MARR DATE"]) - gedStringToDatetime(husbIndi["BIRT DATE"])) < 0):
                displayAnomaly(
                    "US02", id=husbIndi["INDI"], mDate=f["MARR DATE"], bDate=husbIndi["BIRT DATE"])
            if (wifeIndi and timedeltaToYears(gedStringToDatetime(f["MARR DATE"]) - gedStringToDatetime(wifeIndi["BIRT DATE"])) < 0):
                displayAnomaly(
                    "US02", id=wifeIndi["INDI"], mDate=f["MARR DATE"], bDate=wifeIndi["BIRT DATE"])

            # US04
            if (f["DIV DATE"] != "NA"):
                if (timedeltaToYears(gedStringToDatetime(f["DIV DATE"]) - gedStringToDatetime(f["MARR DATE"])) < 0):
                    displayAnomaly(
                        "US04", id=f["FAM"], mDate=f["MARR DATE"], dDate=f["DIV DATE"])

            # US05 Marriage before death
            marDate = gedStringToDatetime(f["MARR DATE"])
            husb = findIndi(f["HUSB"], indi)
            wife = findIndi(f["WIFE"], indi)
            if (husb and wife and marDate != "NA" and ((husb["DEAT DATE"] != "NA" and marDate > gedStringToDatetime(husb["DEAT DATE"])) or (wife["DEAT DATE"] != "NA" and marDate > gedStringToDatetime(wife["DEAT DATE"])))):
                displayAnomaly('US05', id=f["FAM"], mDate=f["MARR DATE"])

            # US06 Divorce before death
            divDate = gedStringToDatetime(f["DIV DATE"])
            husb = findIndi(f["HUSB"], indi)
            wife = findIndi(f["WIFE"], indi)
            if (husb and wife and divDate != "NA" and ((husb["DEAT DATE"] != "NA" and divDate > gedStringToDatetime(husb["DEAT DATE"])) or (wife["DEAT DATE"] != "NA" and divDate > gedStringToDatetime(wife["DEAT DATE"])))):
                displayAnomaly('US06', id=f["FAM"], dDate=f["DIV DATE"])
            
            # US12 Parents not too old
            h_exists = f["HUSB"] != "NA"
            w_exists = f["WIFE"] != "NA"
            if (h_exists):
                fbirthstr = findIndi(f["HUSB"], indi)["BIRT DATE"]
            if (w_exists):
                mbirthstr = findIndi(f["WIFE"], indi)["BIRT DATE"]
                
            for c in f["CHIL"]:
                found = False
                cbirthstr = findIndi(c, indi)["BIRT DATE"]
                if (w_exists and mbirthstr != "NA" and cbirthstr != "NA" and (calculateAgeAtTime(mbirthstr, cbirthstr) >= 60)):
                    found = True
                if (h_exists and fbirthstr != "NA" and cbirthstr != "NA" and (calculateAgeAtTime(fbirthstr, cbirthstr) >= 80)):
                    found = True
                if (found):
                    displayAnomaly("US12", id=c, bDate = cbirthstr, mbDate=mbirthstr, fbDate=fbirthstr)

if __name__ == "__main__":
    main()
