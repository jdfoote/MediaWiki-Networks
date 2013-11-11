import csv
import networkTools as nT
import datetime as dt
import pickle
import sys

# The first file is the CSV containing edits of interest
editCSV = sys.argv[1]
nodeFile = sys.argv[2]

# Parameters for which edits to include, and how to make the network
endDate = dt.datetime(2013,02,11) # Last day that should be included
daysBefore = 14 # How many days before end date to include as edits of interest
placesOnly = False # Whether to only include edits in place namespace
cutoff = 1 # How many ties count to include in network
includePropagations = False # Include edits that are propagations from other edits
directed = True # Observation network (directed) or co-edit network
isDichotomized = False # Keep tie weight or dichotomize based on cutoff

startDate = endDate - dt.timedelta(days=daysBefore)

def makeEditDict(editFile, nodeList):
    '''Takes an edit csv object and returns a
    dictionary in the format {user1:{user2:count}}.'''
    networkDict = {n:{} for n in nodeList} # Initialize dictionary with entry for each node
    currPage = ''
    storedRows = []
    for row in editFile:
        # Gather the rows that belong to the same page.
        newPage = row[1]
        if newPage == currPage or not storedRows:
            storedRows.append(row)
        else:
            # Create a list of those who edited this page.
            coEditors = []
            storedRows.reverse()
            for sRow in storedRows:
                pageID, page, userID, userName, date, comment = sRow
                # Check all of our conditions
                if placesOnly == True:
                    if page[:6] != 'Place:':
                        continue
                if includePropagations == False:
                    if comment[:5] == 'Propa':
                        continue
                date = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                if date > endDate:
                    continue
                if date < startDate:
                    if directed:
                        coEditors.append(userID)
                    break
                # If it passes all conditions, add the editor to the list of coEditors
                else:
                    coEditors.append(userID)
            if len(coEditors) > 1:
                for i, e in enumerate(coEditors):
                    if i > 0:
                        # Get the id of the user who made the edit one more recent
                        lastID = coEditors[i-1]
                        if e != lastID: # no self-loops allowed
                            if lastID not in nodeList or e not in nodeList:
                                print storedRows
                                print coEditors
                            networkDict[lastID][e] = networkDict[lastID].get(e, 0) + 1
            currPage = newPage
            storedRows = [row]
    return networkDict

if __name__ == "__main__":
    with open(nodeFile, 'r') as f:
        nodeList = pickle.load(f)
    with open(editCSV, 'rb') as f:
        editFile = csv.reader(f, delimiter = '\t', quotechar = '|')
        editDict = makeEditDict(editFile, nodeList)
    finalMatrix = nT.networkDictToMatrix(editDict, nodeList, cutoff, dichotomize=isDichotomized)
    with open('EditNetworkMatrix{}to{}.csv'.format(dt.datetime.strftime(startDate, '%Y%m%d'),
        dt.datetime.strftime(endDate,'%Y%m%d')), 'wb') as f:
        for l in finalMatrix:
            f.write(' '.join(l) + '\n')
