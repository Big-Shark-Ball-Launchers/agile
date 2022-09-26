#David Treder
#I pledge my honor that I have abided by the Stevens Honor System
import sys
def isValidTag(tag):
    validTags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", 
         "FAMS", "FAM", "MARR", "HUBS", "WIFE", "CHIL", "DIV", 
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
    elif (elem[1]=="CHIL"):
        if not "CHIL" in entry:
            entry[elem[1]] = [elem[2]]
        else:
            entry[elem[1]] += [elem[2]]
    else:
        entry[elem[1]] = elem[2]

'''
0 @I3@ INDI
1 NAME Joe /Williams/
2 SURN Williams
2 GIVN Joe
1 SEX M
1 BIRT
2 DATE 11 Jun 1861
2 PLAC Idaho Falls, Bonneville, Idaho, United States of America
1 FAMC @F1@
1 FAMC @F2@
2 PEDI adopted
1 ADOP 
2 DATE 16 Mar 1864'''

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
                    curr = {}
                    addElement(curr, l, level)
                    print("curr")
                    print(curr)
                if (indiFlag or famFlag) and l[0] == 0:
                    print(2)
                    #if we reach the end of an individual or family, add it to the list
                    if (indiFlag):
                        indi.append(curr)
                    else:
                        fam.append(curr)
                if (l[0] == 0):
                    print(3)
                    indiFlag = True if l[1] == 'INDI' else False
                    famFlag = True if l[1] == 'FAM' else False
                if indiFlag or famFlag:
                    print(4)
                    addElement(curr, l, level)
                


            print(f'<-- {l[0]}|{l[1]}|{valid}|{l[2]}')
        print(indi)
        print(fam)

if __name__ == "__main__":
    main()