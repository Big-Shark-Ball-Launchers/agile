#David Treder
#I pledge my honor that I have abided by the Stevens Honor System
import sys
import datetime

def isValidTag(tag):
    validTags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", 
         "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", 
         "DATE", "HEAD", "TRLR", "NOTE"]
    return tag in validTags

def formatLine(s):
    '''Returns list in format [level, tag, arguments]'''
    print("formatting")
    l = s.split()
    if (len(l) < 2):
        return [0, 'ERROR', '']
    level = int(l[0])
    tag = l[1]
    args = ' '.join(l[2:])
    print(level)
    print(tag)
    print(args)
    if level == 0 and (args == "FAM" or args == "INDI"):
        print("special case")
        return [level, args, tag] #edge cases for INDI and FAM mean that the third element in s is the tag
    return [level, tag, args]

def addElement(entry, elem, level):
    #todo add special cases
    print("Adding element")
    print(entry)
    print(elem)
    if (level[2] == "DATE"):
        s = level[1] + " " + level[2]
        entry[s] = elem[2]
    elif (elem[1] == "BIRT" or elem[1] == "MARR"):
        pass
    elif (elem[1]=="CHIL" or elem[1]=="FAMS" or elem[1]=="FAMC"):
        if not elem[1] in entry:
            entry[elem[1]] = [elem[2]]
        else:
            entry[elem[1]] += [elem[2]]
    else:
        entry[elem[1]] = elem[2]

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
    return datetime.datetime.strptime(s, '%d %b %Y')

def datetimeToString(d):
    '''Converts a datetime object to a string in the format of a gedcom date'''
    return d.strftime('%d %b %Y')

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
        "DIV": "NA",
        "HUSB": "NA",
        "HUSB NAME": "NA",
        "WIFE": "NA",
        "WIFE NAME": "NA",
        "CHIL": []
    }


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
                
                #if tag is valid, check if INDI or FAM to save the information
                if (l[0] == 0):
                    level = [l[1], None, None]
                if (l[0] == 1):
                    level = [level[0], l[1], None]
                if (l[0] == 2):
                    level = [level[0], level[1], l[1]]
                print("--")
                print(l)
                print(level)
                if (indiFlag or famFlag) and l[0] == 0:
                    print(2)
                    #if we reach the end of an individual or family, add it to the list
                    if (indiFlag):
                        indi.append(curr)
                    else:
                        fam.append(curr)
                if ((l[1] == 'INDI' or l[1] == 'FAM') and l[0] == 0):
                    print(1)
                    curr = defaultIndi() if l[1] == 'INDI' else defaultFam()
                    addElement(curr, l, level)
                    print("curr")
                    print(curr)
                if (l[0] == 0):
                    print(3)
                    indiFlag = True if l[1] == 'INDI' else False
                    famFlag = True if l[1] == 'FAM' else False
                if indiFlag or famFlag:
                    print(4)
                    addElement(curr, l, level)
                


            print(f'<-- {l[0]}|{l[1]}|{valid}|{l[2]}')
        indi = [makeIndiAssumptions(i) for i in indi]
        fam = [makeFamAssumptions(f, indi) for f in fam]

        # indi = [calculateAge(i) for i in indi]
        print(len(indi))
        print(indi)
        print(len(fam))
        print(fam)
        print(dictListToPrettyTable(indi))
        print(dictListToPrettyTable(fam))
        for i in indi:
            print(len(i))

if __name__ == "__main__":
    main()