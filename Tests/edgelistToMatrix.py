import csv
import sys

edgeList = sys.argv[1]
outputFile = sys.argv[2]
directed = sys.argv[3]
numUsers = 29

with open(edgeList, 'rb') as f:
    edges = csv.reader(f)
    edges.next()
    matrix = [[0]*numUsers for n in range(numUsers)]
    for e in edges:
        sender, receiver, strength = [int(x) for x in e]
        matrix[sender-1][receiver-1] += strength
        if directed == "False":
            matrix[receiver-1][sender-1] += strength


with open(outputFile, 'wb') as f:
    out = csv.writer(f, delimiter= ' ')
    for r in matrix:
        out.writerow(r)

