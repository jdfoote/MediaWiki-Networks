import csv
import datetime as dt
import yaml

inputName = "/home/jeremy/Dropbox/680DataEdited.csv"
outputName = "/home/jeremy/Dropbox/680DataFinal.csv"
daysActiveCutoff = 1
with open('./DBCreation/config.yaml', 'r') as f:
    config = yaml.load(f)

startDate = dt.date(2012,01,23)
endDate = config['endDate']
delta = config['timeDelta']
currDate = startDate
dateList = []
while currDate < endDate:
    dateList.append(currDate)
    currDate += dt.timedelta(days = delta)

print dateList

def addMissing(userRows):
    '''Takes a list of user rows, changes data to "missing" data for everything that occurred
    before the first_edit, and adds 0s for what occurred after the last edit'''
    existingDates = [x[1] for x in userRows]
    userID = userRows[0][0]
    first_edit, last_edit = userRows[0][-2], userRows[0][-1]
    first_edit = dt.datetime.strptime(first_edit, '%Y-%m-%d').date()
    last_edit = dt.datetime.strptime(last_edit, '%Y-%m-%d').date()
    sinceJoining = (endDate - first_edit).days
    sinceEditing = (endDate - last_edit).days
    newRows = []
    for currStart in dateList:
        currEnd = currStart + dt.timedelta(days = delta)
        currRow = [userID, dateList.index(currStart), sinceJoining, sinceEditing]
        foundDate = False
        for r in userRows:
            rowDate = dt.datetime.strptime(r[1], '%Y-%m-%d').date()
            if currStart == rowDate:
                if currEnd < first_edit:
                    # If the user hadn't joined the community, treat as missing data
                    newRows.append(currRow + ['.']*len(r[3:-2]))
                    # Otherwise, just adjust the format, and add original data
                else:
                    # Boy, this is quick and dirty!
                    newRows.append(currRow + r[3:-2])
                foundDate = True
                break
        # If there isn't a matching entry, that means it's after the last edit - will treat as 0s
        if foundDate == False:
            if currStart < last_edit:
                print [currStart]
                print [r[1] for r in userRows]
                print last_edit
                print userID
            newRows.append(currRow + [0] * len(r[3:-2]))
    return newRows


with open(inputName, 'rb') as f:
    c = csv.reader(f)
    activeUsers = []
    # Adjust header for new format
    header = c.next()[:-2]
    header[1:5] = 'monthNumber','daysSinceJoining','daysSinceEditing', 'all_Edits', 'manual_edits'
    firstRow = c.next()
    currID, daysActive = firstRow[0], int(firstRow[-3])
    activeSum = daysActive
    currUserRows = [firstRow]
    for row in c:
        # If this is a new user, check whether to add the old user to the list
        if row[0] != currID:
            if activeSum >= daysActiveCutoff:
                cr = addMissing(currUserRows)
                activeUsers += cr
            # Reset for this user's data
            activeSum = 0
            currID = row[0]
            currUserRows = []
        activeSum += int(row[-3])
        currUserRows.append(row)

with open(outputName, 'wb') as f:
    o = csv.writer(f)
    o.writerow(header)
    o.writerows(activeUsers)
