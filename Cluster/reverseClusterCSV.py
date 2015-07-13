import csv
import sys

'''In order to look at how people leave the community, we reverse the clusters they are in,
and remove the users who haven't ever left'''

inFile = sys.argv[1] # Must include "NA" for the final month, when a user leaves.
outFile = sys.argv[1][:-4] + 'Reversed.csv'

with open(inFile, 'rb') as f:
    origCSV = csv.reader(f)
    with open(outFile, 'wb') as o:
        newCSV = csv.writer(o)
        # Keep header
        newCSV.writerow(origCSV.next())
        for row in origCSV:
            if row[-1] == 'NA':
                newRow = [row[0]] + row[-2:0:-1]
                newCSV.writerow(newRow)
