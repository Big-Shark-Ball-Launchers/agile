stories = {
    "US01": "ERROR: {story}: INDI/FAM {id}: Date {dateType} {date} occurs after current date {currentDate}",
    "US02": "ERROR: {story}: INDI/FAM {id}: Marriage date: {mDate} occurs before the individual's birthdate {bDate}",
    "US03": "ERROR: {story}: INDI/FAM {id}: Death date: {dDate} occurs before the individual's birthdate {bDate}",
    "US04": "ERROR: {story}: FAM {id}: Divorce date {dDate} occurs before marriage date {mDate}",
    "US05": "ERROR: {story}: FAM {id}: Marriage date {mDate} occurs after death of INDI {indiId}",
    "US06": "ERROR: {story}: FAM {id}: Divorce date {dDate} occurs before death of one or both spouses",
    "US07": "ANOMALY: {story}: INDI {id}: Age over 150 years old: {age}",
    "US08": "ANOMALY: {story}: INDI {id}: Birth date {bDate} occurs before parents' marriage date {mDate} or more than 9 months after parents' divorce date {dDate} in FAM {famID}",
    "US09": "ANOMALY: {story}: INDI {id}: Birth date {bDate} occurs after mother's death {mDeath} or more than 9 months after father's death {dDeath}",
    "US10": "ANOMALY: {story}: INDI {id}: Marriage date: {date} occurs before age of 14",
    "US11": "ANOMALY: {story}: INDI {id} is an active spouse in muliple families. FAMS: {fams}",
    "US12": "ANOMALY: {story}: INDI {id}: Birthdate {bDate} occurs more than {ageLimit} years after {parentString}'s birthday: {parentBirthdate}",
    "US13": "ANOMALY: {story}: INDI {id}: Birthdate {bDate} occurs within 2 days to 8 months of sibling {sibID}: {siblingBirthdate}",
    "US14": "ANOMALY: {story}: FAM {id}: More than 5 children born at the same time: {nuplets}",
    "US15": "ANOMALY: {story}: FAM {id}: Family contains 15 or more siblings",
    "US16": "ANOMALY: {story}: FAM {id}: Individual {indiId} has a different last name from his family {famName}",
    "US17": "ANOMALY: {story}: INDI {id}: Individual has married their decendent {decendentId} in FAM {famId}",
    "US18": "ANOMALY: {story}: FAM {id}: Siblings {sib1} and {sib2} are married in FAM {famId}",
    "US19": "ANOMALY: {story}: FAM {id}: Wife {wifeId} is married to their first cousin Husband {husbandId}",
    "US20": "ANOMALY: {story}: FAM {id}: Husband {husbandId} has nibling relationship with Wife {wifeId}",
    "US21": "ANOMALY: {story}: INDI {id}: Unexpected gender {gender} for role {role}",
    "US22": "ERROR: {story}: INDI/FAM {id}: ID {id} is not unique (multiple individuals/families share this ID) - further checks may be inaccurate",
    "US23": "ANOMALY: {story}: INDI {id}: Individuals {id} and {id2} have the same name and birthdate",
    "US24": "ANOMALY: {story}: FAM {id}: Families {id} and {id2} have the same spouses and marriage date",
}