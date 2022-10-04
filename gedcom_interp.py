#https://github.com/Big-Shark-Ball-Launchers/agile
#David Treder, Tyler Seliber, Andrew Capro
#I pledge my honor that I have abided by the Stevens Honor System

import sys
import datetime
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
        return [level, args, tag] #edge cases for INDI and FAM mean that the third element in s is the tag
    return [level, tag, args]

def addElement(entry, elem, level):
    key = ""
    value = ""
    if (level[2] == "DATE" and (level[1] == "BIRT" or level[1] == "DEAT" or level[1] == "MARR" or level[1] == "DIV")):
        key = level[1] + " " + level[2]
        value = elem[2]
    elif (elem[1] == "BIRT" or elem[1] == "MARR"):
        return
    elif (elem[1]=="CHIL" or elem[1]=="FAMS" or elem[1]=="FAMC"):
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
        return datetime.datetime(1,1,1) #default in case of error

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
        "FAMC": [],
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

def displayAnomaly(storyKey, **kwargs):
    '''prints a formatted error/anomaly message'''
    anomalyString = stories[storyKey]
    formattedAnaomalyString = anomalyString.format(**kwargs, story=storyKey)
    print(formattedAnaomalyString)

def main():
    if (len(sys.argv) <= 1):
        filename = 'My-Family-25-Sep-2022-221241779.ged' #default file path
    else:
        filename = sys.argv[1]

    indi = []
    fam = []
    #keeps track of the tag of levels
    level = []
    indiFlag = False
    famFlag = False
    with open(filename, 'r') as f:
        for line in f:
            print(f'--> {line}', end='')
            l = formatLine(line)
            valid = 'Y' if isValidTag(l[1]) else 'N'
            if isValidTag(l[1]):
                
                if (l[0] == 0):
                    level = [l[1], None, None]
                if (l[0] == 1):
                    level = [level[0], l[1], None]
                if (l[0] == 2):
                    level = [level[0], level[1], l[1]]

                if (indiFlag or famFlag) and l[0] == 0:
                    #if we reach the end of an individual or family, add it to the list
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
                


            print(f'<-- {l[0]}|{l[1]}|{valid}|{l[2]}')
        indi = [makeIndiAssumptions(i) for i in indi]
        fam = [makeFamAssumptions(f, indi) for f in fam]
        print(dictListToPrettyTable(sorted(indi, key = lambda x: x["INDI"])))
        print(dictListToPrettyTable(sorted(fam, key = lambda x: x["FAM"])))

        # Loop through each individual and family to check for errors/anomalies
        for i in indi:

            # US01
            currentDate = datetime.datetime.now()
            if (i["BIRT DATE"] != "NA" and gedStringToDatetime(i["BIRT DATE"]) > currentDate):
                displayAnomaly("US01", id=i["INDI"], date=i["BIRT DATE"], dateType="BIRT", currentDate=datetimeToString(currentDate))
            if (i["DEAT DATE"] != "NA" and gedStringToDatetime(i["DEAT DATE"]) > currentDate):
                displayAnomaly("US01", id=i["INDI"], date=i["DEAT DATE"], dateType="DEAT", currentDate=datetimeToString(currentDate))
                
            # US03
            if(i["AGE"] < 0):
                displayAnomaly("US03", id = i["INDI"], dDate = i["DEAT DATE"], bDate = i["BIRT DATE"])

        for f in fam:
        
            # US01
            if (f["MARR DATE"] != "NA" and gedStringToDatetime(f["MARR DATE"]) > currentDate):
                displayAnomaly("US01", id=f["FAM"], date=f["MARR DATE"], dateType="MARR", currentDate=datetimeToString(currentDate))
            if (f["DIV DATE"] != "NA" and gedStringToDatetime(f["DIV DATE"]) > currentDate):
                displayAnomaly("US01", id=f["FAM"], date=f["DIV DATE"], dateType="DIV", currentDate=datetimeToString(currentDate))
                
            # US02
            husb = f["HUSB"]
            wife = f["WIFE"]
            husbIndi = findIndi(husb, indi)
            wifeIndi = findIndi(wife, indi)
            if(husbIndi and timedeltaToYears(gedStringToDatetime(f["MARR DATE"]) - gedStringToDatetime(husbIndi["BIRT DATE"])) < 0):
                displayAnomaly("US02", id = husbIndi["INDI"], mDate = f["MARR DATE"], bDate = husbIndi["BIRT DATE"])
            if(wifeIndi and timedeltaToYears(gedStringToDatetime(f["MARR DATE"]) - gedStringToDatetime(wifeIndi["BIRT DATE"])) < 0):
                displayAnomaly("US02", id = wifeIndi["INDI"], mDate = f["MARR DATE"], bDate = wifeIndi["BIRT DATE"])
            
            # US04
            if(f["DIV DATE"] != "NA"):
                if(timedeltaToYears(gedStringToDatetime(f["DIV DATE"]) - gedStringToDatetime(f["MARR DATE"])) < 0):
                    displayAnomaly("US04", id = f["FAM"], mDate = f["MARR DATE"], dDate = f["DIV DATE"])

            # US05 Marriage before death
            marDate = gedStringToDatetime(f["MARR DATE"])
            husb = findIndi(f["HUSB"], indi)
            wife = findIndi(f["WIFE"], indi)
            if (husb and wife and marDate != "NA" and ((husb["DEAT DATE"] != "NA" and marDate > gedStringToDatetime(husb["DEAT DATE"])) or (wife["DEAT DATE"] != "NA" and marDate > gedStringToDatetime(wife["DEAT DATE"])))):
                displayAnomaly('US05', id=f["FAM"], mDate = f["MARR DATE"])

            # US06 Divorce before death
            divDate = gedStringToDatetime(f["DIV DATE"])
            husb = findIndi(f["HUSB"], indi)
            wife = findIndi(f["WIFE"], indi)
            if (husb and wife and divDate != "NA" and ((husb["DEAT DATE"] != "NA" and divDate > gedStringToDatetime(husb["DEAT DATE"])) or (wife["DEAT DATE"] != "NA" and divDate > gedStringToDatetime(wife["DEAT DATE"])))):
                displayAnomaly('US06', id=f["FAM"], dDate = f["DIV DATE"])

if __name__ == "__main__":
    main()