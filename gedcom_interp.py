# https://github.com/Big-Shark-Ball-Launchers/agile
# David Treder, Tyler Seliber, Andrew Capro
# I pledge my honor that I have abided by the Stevens Honor System

import sys
import datetime
from dateutil.relativedelta import relativedelta
from user_stories import stories
from itertools import combinations

CURRENT_DATE = datetime.datetime.now()


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


def makeFamAssumptions(fam, indiList):
    '''Fills in assumptions about the data.'''
    fam["HUSB NAME"] = indiIDtoName(indiList, fam["HUSB"])
    fam["WIFE NAME"] = indiIDtoName(indiList, fam["WIFE"])
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


def indiIDtoName(indiList, id):
    '''returns name of individual based on their id'''
    for i in indiList:
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


def findIndi(iId, indiList):
    '''returns an individual given an INDI id'''
    for i in indiList:
        if (i["INDI"] == iId):
            return i


def findFam(fId, famList):
    '''returns a family given a FAM id'''
    for f in famList:
        if (f["FAM"] == fId):
            return f


def marriageRange(f, indiList):
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
    elif findIndi(f["HUSB"], indiList)["DEAT"] == "Y":
        end = gedStringToDatetime(findIndi(f["HUSB"], indiList)["DEAT DATE"])
    elif findIndi(f["WIFE"], indiList)["DEAT"] == "Y":
        end = gedStringToDatetime(findIndi(f["WIFE"], indiList)["DEAT DATE"])
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

def getDecendents(i, indiList, famList):
    '''returns a list of decendents of an individual'''
    indi = findIndi(i, indiList)
    decendents = []
    if (indi["FAMS"] != ""):
        for f in indi["FAMS"]:
            fam = findFam(f, famList)
            for c in fam["CHIL"]:
                decendents.append(c)
                decendents += getDecendents(c, indiList, famList)
    return decendents

def getParents(i, indiList, famList):
    '''returns a list of parents of an individual'''
    indi = findIndi(i, indiList)
    parents = []
    if (indi["FAMC"] != ""):
        fam = findFam(indi["FAMC"], famList)
        if (fam != None):
            parents.append(fam["HUSB"])
            parents.append(fam["WIFE"])
    return parents

def getSiblings(i, indiList, famList):
    '''returns a list of siblings of an individual'''
    indi = findIndi(i, indiList)
    siblings = []
    if (indi["FAMC"] != ""):
        fam = findFam(indi["FAMC"], famList)
        if (fam != None):
            for c in fam["CHIL"]:
                if (c != i):
                    siblings.append(c)
    return siblings

def areFirstCousins(i1, i2, indiList, famList):
    #returns boolean if two individuals are first cousins
    #first cousins share a grandparent
    #get the parents of i1
    parents1 = getParents(i1, indiList, famList)
    #get the parents of i2
    parents2 = getParents(i2, indiList, famList)
    #get the parents of the parents of i1
    grandParents1 = []
    for p in parents1:
        grandParents1 += getParents(p, indiList, famList)
    #get the parents of the parents of i2
    grandParents2 = []
    for p in parents2:
        grandParents2 += getParents(p, indiList, famList)

    #check if any of the grandparents of i1 are the same as any of the grandparents of i2
    for gp1 in grandParents1:
        for gp2 in grandParents2:
            if gp1 == gp2:
                return True
    return False
    
def hasNephewRelationship(i1, i2, indiList, famList):
    #returns boolean if two individuals have a nephew relationship
    #nephew relationship is when one individual is the sibling of the other individual's parent
    #get the parents of i1
    parents1 = getParents(i1, indiList, famList)
    #get the parents of i2
    parents2 = getParents(i2, indiList, famList)
    #get the siblings of the parents of i1
    siblings1 = []
    for p in parents1:
        siblings1 += getSiblings(p, indiList, famList)
    #get the siblings of i2
    siblings2 = getSiblings(i2, indiList, famList)

    #check if any of the siblings of the parents of i1 are the same as any of the siblings of the parents of i2
    for s1 in siblings1:
        for s2 in siblings2:
            if s1 == s2:
                return True
    return False

def displayAnomaly(storyKey, **kwargs):
    '''prints a formatted error/anomaly message'''
    anomalyString = stories[storyKey]
    formattedAnaomalyString = anomalyString.format(**kwargs, story=storyKey)
    print(formattedAnaomalyString)


def processFile(filename):
    indiList = []
    famList = []

    # keeps track of the tag of levels
    level = []
    indiFlag = False
    famFlag = False
    curr = defaultIndi()
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
                        indiList.append(curr)
                    else:
                        famList.append(curr)
                if ((l[1] == 'INDI' or l[1] == 'FAM') and l[0] == 0):
                    curr = defaultIndi() if l[1] == 'INDI' else defaultFam()
                    addElement(curr, l, level)
                if (l[0] == 0):
                    indiFlag = True if l[1] == 'INDI' else False
                    famFlag = True if l[1] == 'FAM' else False
                if indiFlag or famFlag:
                    addElement(curr, l, level)

        if (indiFlag):
            indiList.append(curr)
        else:
            famList.append(curr)

        indiList = [makeIndiAssumptions(i) for i in indiList]
        famList = [makeFamAssumptions(f, indiList) for f in famList]
        return (indiList, famList)

def checkIndiAnomalies(indiList, famList):
    index = 0
    # Loop through each individual and family to check for errors/anomalies
    for i in indiList:

        # US01 - Dates before current date
        if (i["BIRT DATE"] != "NA" and gedStringToDatetime(i["BIRT DATE"]) > CURRENT_DATE):
            displayAnomaly("US01", id=i["INDI"], date=i["BIRT DATE"],
                           dateType="BIRT", currentDate=datetimeToString(CURRENT_DATE))
        if (i["DEAT DATE"] != "NA" and gedStringToDatetime(i["DEAT DATE"]) > CURRENT_DATE):
            displayAnomaly("US01", id=i["INDI"], date=i["DEAT DATE"],
                           dateType="DEAT", currentDate=datetimeToString(CURRENT_DATE))

        # US03 - Birth before death
        if (i["AGE"] < 0):
            displayAnomaly(
                "US03", id=i["INDI"], dDate=i["DEAT DATE"], bDate=i["BIRT DATE"])

        # US07 - Less than 150 years old
        if (i["AGE"] > 150):
            displayAnomaly("US07", id=i["INDI"], age=i["AGE"])

        # US08 - Birth before marriage of parents
        anomalyFound = False
        family = findFam(i["FAMC"], famList)
        if (family != None):
            mDateStr = family["MARR DATE"]
            dDateStr = family["DIV DATE"]
            bDateStr = i["BIRT DATE"]
            if (mDateStr == "NA"):  # born when parents were never married
                anomalyFound = True
            # born before marriage of parents
            elif (gedStringToDatetime(bDateStr) < gedStringToDatetime(mDateStr)):
                anomalyFound = True
            # born after 9 months of divorce of parents
            if (dDateStr != "NA" and gedStringToDatetime(bDateStr) > (gedStringToDatetime(dDateStr) + relativedelta(months=+9))):
                anomalyFound = True
            if (anomalyFound):
                displayAnomaly("US08", id=i["INDI"], bDate=bDateStr,
                               mDate=mDateStr, dDate=dDateStr, famID=family["FAM"])

        # US09 - Birth before death of parents
        if (i["FAMC"] != "NA"):
            family = findFam(i["FAMC"], famList)
            husband = findIndi(family["HUSB"], indiList)
            wife = findIndi(family["WIFE"], indiList)
            husb_death = husband["DEAT DATE"]
            wife_death = wife["DEAT DATE"]
            if (husb_death != "NA"):
                husb_effective_death = datetimeToString(
                    gedStringToDatetime(husb_death) + relativedelta(months=+9))
            birth_date = i["BIRT DATE"]
            if ((wife_death != "NA" and calculateAgeAtTime(birth_date, wife_death) < 0) or (husb_death != "NA" and calculateAgeAtTime(birth_date, husb_effective_death)) < 0):
                displayAnomaly("US09", id=i["INDI"], dDeath=husband["DEAT DATE"],
                               mDeath=wife["DEAT DATE"], bDate=i["BIRT DATE"])

        # US10 - Marriage after 14
        if (i["FAMS"]):
            for f in i["FAMS"]:
                fam_ = findFam(f, famList)
                bDate = i["BIRT DATE"]
                marDate = fam_["MARR DATE"]
                if (calculateAgeAtTime(bDate, marDate) < 14):
                    displayAnomaly("US10", id=i["INDI"], fam=fam_[
                                   "FAM"], date=marDate)

        # US11 - No bigamy
        if (len(i["FAMS"]) > 1):
            # list of ranges of marraiges for this individual
            marraigeRangeList = [marriageRange(
                findFam(f, famList), indiList) for f in i["FAMS"]]
            if (datetimeRangeOverlap(marraigeRangeList)):
                displayAnomaly("US11", id=i["INDI"], fams=i["FAMS"])

        # US21 - Correct gender for role

        # US22 - Unique IDs

        # US23 - Unique name and birth date
        for x in range(index+1,len(indiList)-1):
            j = indiList[x]
            if(i["NAME"] == j["NAME"] and i["BIRT DATE"] == j["BIRT DATE"]):
                displayAnomaly("US23", id=i["INDI"], id2=j["INDI"]) 

        # US24 - Unique families by spouses

        index+=1


def checkFamAnomalies(indiList, famList):
    indexf = 0
    for f in famList:

        # US01 - Dates before current date
        if (f["MARR DATE"] != "NA" and gedStringToDatetime(f["MARR DATE"]) > CURRENT_DATE):
            displayAnomaly("US01", id=f["FAM"], date=f["MARR DATE"],
                           dateType="MARR", currentDate=datetimeToString(CURRENT_DATE))
        if (f["DIV DATE"] != "NA" and gedStringToDatetime(f["DIV DATE"]) > CURRENT_DATE):
            displayAnomaly("US01", id=f["FAM"], date=f["DIV DATE"],
                           dateType="DIV", currentDate=datetimeToString(CURRENT_DATE))

        # US02 - Birth before marriage
        husb = f["HUSB"]
        wife = f["WIFE"]
        husbIndi = findIndi(husb, indiList)
        wifeIndi = findIndi(wife, indiList)
        if (husbIndi and timedeltaToYears(gedStringToDatetime(f["MARR DATE"]) - gedStringToDatetime(husbIndi["BIRT DATE"])) < 0):
            displayAnomaly(
                "US02", id=husbIndi["INDI"], mDate=f["MARR DATE"], bDate=husbIndi["BIRT DATE"])
        if (wifeIndi and timedeltaToYears(gedStringToDatetime(f["MARR DATE"]) - gedStringToDatetime(wifeIndi["BIRT DATE"])) < 0):
            displayAnomaly(
                "US02", id=wifeIndi["INDI"], mDate=f["MARR DATE"], bDate=wifeIndi["BIRT DATE"])

        # US04 - Marriage before divorce
        if (f["DIV DATE"] != "NA"):
            if (timedeltaToYears(gedStringToDatetime(f["DIV DATE"]) - gedStringToDatetime(f["MARR DATE"])) < 0):
                displayAnomaly(
                    "US04", id=f["FAM"], mDate=f["MARR DATE"], dDate=f["DIV DATE"])

        # US05 - Marriage before death
        marDate = gedStringToDatetime(f["MARR DATE"])
        husb = findIndi(f["HUSB"], indiList)
        wife = findIndi(f["WIFE"], indiList)

        if (husb and wife and marDate != "NA"):
            if ((husb["DEAT DATE"] != "NA" and marDate > gedStringToDatetime(husb["DEAT DATE"]))):
                displayAnomaly(
                    'US05', id=f["FAM"], mDate=f["MARR DATE"], indiId=husb["INDI"])
            if ((wife["DEAT DATE"] != "NA" and marDate > gedStringToDatetime(wife["DEAT DATE"]))):
                displayAnomaly(
                    'US05', id=f["FAM"], mDate=f["MARR DATE"], indiId=wife["INDI"])

        # US06 - Divorce before death
        divDate = gedStringToDatetime(f["DIV DATE"])
        husb = findIndi(f["HUSB"], indiList)
        wife = findIndi(f["WIFE"], indiList)
        if (husb and wife and divDate != "NA" and ((husb["DEAT DATE"] != "NA" and divDate > gedStringToDatetime(husb["DEAT DATE"])) or (wife["DEAT DATE"] != "NA" and divDate > gedStringToDatetime(wife["DEAT DATE"])))):
            displayAnomaly('US06', id=f["FAM"], dDate=f["DIV DATE"])

        # US12 - Parents not too old
        h_exists = f["HUSB"] != "NA"
        w_exists = f["WIFE"] != "NA"
        if (h_exists):
            fbirthstr = findIndi(f["HUSB"], indiList)["BIRT DATE"]
        if (w_exists):
            mbirthstr = findIndi(f["WIFE"], indiList)["BIRT DATE"]

        for c in f["CHIL"]:
            cbirthstr = findIndi(c, indiList)["BIRT DATE"]
            mConditions = w_exists and mbirthstr != "NA" and cbirthstr != "NA"
            fConditions = h_exists and fbirthstr != "NA" and cbirthstr != "NA"
            if (mConditions and (calculateAgeAtTime(mbirthstr, cbirthstr) >= 60)):
                displayAnomaly("US12", id=c, bDate=cbirthstr,
                               parentBirthdate=mbirthstr, ageLimit=60, parentString="mother")
            if (fConditions and (calculateAgeAtTime(fbirthstr, cbirthstr) >= 80)):
                displayAnomaly("US12", id=c, bDate=cbirthstr,
                               parentBirthdate=fbirthstr, ageLimit=80, parentString="father")

        # US13 - Siblings spacing
        for c1 in f["CHIL"]:
            c1birthstr = findIndi(c1, indiList)["BIRT DATE"]
            c1birth = gedStringToDatetime(c1birthstr)
            for c2 in f["CHIL"]:
                if (c1 != c2):
                    c2birthstr = findIndi(c2, indiList)["BIRT DATE"]
                    c2birth = gedStringToDatetime(c2birthstr)
                    if (c1birthstr != "NA" and c2birthstr != "NA"):
                        ranged = (c1birth + relativedelta(days=2), c1birth + relativedelta(months=8))
                        if (datetimeWithinRange(c2birth, ranged)):
                            displayAnomaly("US13", id=c1, sibID=c2, bDate=c1birthstr, siblingBirthdate=c2birthstr)

        # US14 - Multiple births <= 5
        nuplets = []
        pairs = [comb for comb in combinations(f["CHIL"], 2)]
        for c1, c2 in pairs:
            c1birthstr = findIndi(c1, indiList)["BIRT DATE"]
            c1birth = gedStringToDatetime(c1birthstr)
            c2birthstr = findIndi(c2, indiList)["BIRT DATE"]
            c2birth = gedStringToDatetime(c2birthstr)
            if (c1birthstr != "NA" and c2birthstr != "NA"):
                bornDelta = abs(c1birth - c2birth)
                if (bornDelta.days == 0):
                    nuplets += [c1, c2]
                        
        nuplets = sorted(list(set(nuplets)))
        if len(nuplets) > 5:
            displayAnomaly("US14", id=f["FAM"], nuplets=nuplets)

        # US15 - Fewer than 15 siblings
        siblingCounter = 0
        for c in f["CHIL"]:
            siblingCounter = siblingCounter + 1
        if siblingCounter >= 15:
            displayAnomaly("US15", id=f["FAM"])
            
        # US16 - Male last names
        if f["HUSB NAME"] and f["CHIL"]:
            parentName = f["HUSB NAME"]
            check = 0
            for s in parentName:
                if s == '/':
                    check = check + 1
                if check > 0:    
                    parentLastName = parentName.split()[1]
                    for c in f["CHIL"]:
                        child = findIndi(c,indiList)
                        childGender = child["SEX"]
                        childName = child["NAME"]
                        childLastName = childName.split()[1]
                        if childGender == "M" and childLastName != parentLastName:
                            displayAnomaly("US16", id=f["FAM"], indiId=childName, famName=parentLastName)

        # US17 - No marriages to descendants
        h_exists = f["HUSB"] != "NA"
        w_exists = f["WIFE"] != "NA"
        if (h_exists and w_exists):
            husb = findIndi(f["HUSB"], indiList)
            wife = findIndi(f["WIFE"], indiList)
            husbDecendents = getDecendents(f["HUSB"], indiList, famList)
            wifeDecendents = getDecendents(f["WIFE"], indiList, famList)
            if (f["WIFE"] in husbDecendents):
                displayAnomaly("US17", id=f["HUSB"], famId=f["FAM"], decendentId=f["WIFE"])
            if (f["HUSB"] in wifeDecendents):
                displayAnomaly("US17", id=f["WIFE"], famId=f["FAM"], decendentId=f["HUSB"])
            
        # US18 - Siblings should not marry
        for c1, c2 in pairs:
            c1indi = findIndi(c1, indiList)
            c2indi = findIndi(c2, indiList)
            if c1indi["FAMS"] != "NA" and c2indi["FAMS"] != "NA":
                for fam in c1indi["FAMS"]:
                    if fam in c2indi["FAMS"]:
                        displayAnomaly("US18", id=f["FAM"], sib1=c1, sib2=c2, famId=fam)

        # US19 - First cousins should not marry

        #for every marriage (fam), check if the husband and wife are first cousins
        #if they are, then display the anomaly
        wife = f["WIFE"]
        husband = f["HUSB"]
        if (wife != "NA" and husband != "NA"):
            if (areFirstCousins(wife, husband, indiList, famList)):
                displayAnomaly("US19", id=f["FAM"], wifeId=wife, husbandId=husband)

        # US20 - Aunts and uncles

        #for every marriage (fam), check if husband and wife are aunt/uncle and niece/nephew
        #if they are, then display the anomaly
        wife = f["WIFE"]
        husband = f["HUSB"]
        if (wife != "NA" and husband != "NA"):
            if (hasNephewRelationship(wife, husband, indiList, famList)):
                displayAnomaly("US20", id=f["FAM"], wifeId=wife, husbandId=husband)
            if (hasNephewRelationship(husband, wife, indiList, famList)):
                displayAnomaly("US20", id=f["FAM"], wifeId=wife, husbandId=husband)

        # US21 - Correct gender for role

        # US22 - Unique IDs

        # US23 - Unique name and birth date
        
        # US24 - Unique families by spouses
        for y in range(indexf+1,len(famList)):
            j = famList[y] 
            if(f["HUSB NAME"] == j["HUSB NAME"] and f["WIFE NAME"] == j["WIFE NAME"] and f["MARR DATE"] == j["MARR DATE"]):
                displayAnomaly("US24", id=f["FAM"], id2=j["FAM"]) 

        indexf+=1



def main():
    if (len(sys.argv) <= 1):
        filename = 'full_family.ged'  # default file path
        filename = 'testing.ged'
    else:
        filename = sys.argv[1]
    indiList, fam = processFile(filename)

    # Print out the individuals and families
    print(dictListToPrettyTable(sorted(indiList, key=lambda x: x["INDI"])))
    print(dictListToPrettyTable(sorted(fam, key=lambda x: x["FAM"])))
    # Check for errors and anomalies for the individuals and families
    checkIndiAnomalies(indiList, fam)
    checkFamAnomalies(indiList, fam)


if __name__ == "__main__":
    main()
