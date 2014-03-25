import csv
import sys

inFile = sys.argv[1]
outFile = sys.argv[2]
# Make sure to change this to reflect the data.
columnsToChange = range(4, 39)

with open(inFile, 'rb') as i:
    origData = csv.reader(i)
    with open(outFile, 'wb') as o:
        output = csv.writer(o)
        # Write header
        output.writerow(origData.next() + ['manual_edits'])
        for row in origData:
            outRow = []
            totEdits = float(sum([int(row[x]) for x in columnsToChange]))
            for i in range(len(row)):
                if i in columnsToChange and int(row[i]) > 0:
                    outRow.append(int(row[i]) / totEdits)
                else:
                    outRow.append(row[i])
            output.writerow(outRow + [totEdits])
