import csv

inputName = "/home/jeremy/Dropbox/680Data.csv"
outputName = "/home/jeremy/Dropbox/680DataEdited.csv"
daysActiveCutoff = 1

with open(inputName, 'rb') as f:
    c = csv.reader(f)
    activeUsers = []
    # Skip header
    header = c.next()
    firstRow = c.next()
    currID, daysActive = firstRow[0], firstRow[-2]
    activeSum = int(daysActive)
    for row in c:
        # If this is a new user, check whether to add the old user to the list
        if row[0] != currID:
            if activeSum >= daysActiveCutoff:
                activeUsers.append(row)
            # Reset for this user's data
            activeSum = 0
            currID = row[0]
        activeSum += int(row[-2])

with open(outputName, 'wb') as f:
    o = csv.writer(f)
    o.writerow(header)
    o.writerows(activeUsers)
