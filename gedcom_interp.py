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
    l = s.split()
    if (len(l) < 2):
        return [0, 'ERROR', '']
    level = l[0]
    tag = l[1]
    args = ' '.join(l[2:])
    if ('INDI' in s) or ('FAM' in s):
        return [level, args, tag] #edge cases for INDI and FAM mean that the third element in s is the tag
    return [level, tag, args]

def main():
    if (len(sys.argv) <= 1):
        filename = 'gedcom.ged' #default file path
    else:
        filename = sys.argv[1]
    with open(filename, 'r') as f:
        for line in f:
            print(f'--> {line}', end='')
            l = formatLine(line)
            valid = 'Y' if isValidTag(l[1]) else 'N'
            print(f'<-- {l[0]}|{l[1]}|{valid}|{l[2]}')

if __name__ == "__main__":
    main()