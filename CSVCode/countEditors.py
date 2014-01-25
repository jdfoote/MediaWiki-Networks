import csv
import networkTools as nT
import datetime as dt
import sys
import pickle

editCSV = sys.argv[1]
startDate = dt.datetime(2012,12,31)
endDate = dt.datetime(2013,2,25)
includePropagations = False
IDsToIgnore = ['','48']

def countEditors(editFile):
    editors = {}
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
            for sRow in reversed(storedRows):
                pageID, page, userID, userName, date, comment = sRow
                # Check all of our conditions
                if userID in IDsToIgnore:
                    continue
                if includePropagations == False:
                    if comment[:5] == 'Propa':
                        continue
                date = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                if date > endDate:
                    continue
                coEditors.append(userID)
                if date < startDate:
                    break
            coEditors = set(coEditors)
            if len(coEditors) > 1:
                for coEditor in coEditors:
                    editors[coEditor] = editors.get(coEditor, 0) + 1
            currPage = newPage
            storedRows = [row]
    return editors


if __name__ == "__main__":
    with open(editCSV, 'rb') as f:
        editFile = csv.reader(f, delimiter = '\t', quotechar = '|')
        output = countEditors(editFile)
    with open('EditorList.csv', 'w') as f:
        f.write('Editors: {}\n'.format(len(output)))
        for k,v in output.items():
            f.write('{}\t{}\tEditor\n'.format(k,v))
    with open('EditorList{}to{}.pkl'.format(dt.datetime.strftime(startDate, '%Y%m%d'),
        dt.datetime.strftime(endDate,'%Y%m%d')), 'w') as f:
        # Combine the dictionaries, then pickle the user IDs
        pickle.dump(sorted(output.keys()), f)
