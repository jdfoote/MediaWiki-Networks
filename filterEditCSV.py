import csv
import pickle
import datetime
import sys
import re

fn = sys.argv[1]
output = 'FilteredEditList.tsv'
nodeFile = sys.argv[2]
includePropagations = False # Whether to include edits that just propagate other edits
idsToIgnore = ['0','48','']

def filterNodes(editFile, nodes, output):
    '''Takes a TSV file of edits and a list of nodes of interest, and returns a TSV file with only
    edits made by nodes of interest. If nodes is empty, then returns all nodes'''
    for row in editFile:
        userID, comment = row[2], row[-1]
        if not includePropagations:
            if comment[:5] == 'Propa':
                continue
        if userID in idsToIgnore:
            continue
        if nodes:
            if userID not in nodes:
                continue
        output.writerow(row)

if __name__ == "__main__":
    with open(nodeFile, 'r') as f:
        nodeList = pickle.load(f)
        nodeList = [] # Delete this
    with open(fn, 'rb') as f:
        with open(output, 'wb') as g:
            editFile = csv.reader(f, delimiter="\t", quotechar="|")
            output = csv.writer(g, delimiter = '\t', quotechar='|')
            editDict = filterNodes(editFile, nodes = nodeList, output=output)
