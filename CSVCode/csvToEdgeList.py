import sys
import re
import csv

fn = sys.argv[1]

with open(re.search(r"\d+", fn).group(0) + "Edgelist.csv", 'wb') as g:
    with open(fn, 'rb') as f:
        csvFile = csv.reader(f, delimiter=' ')
        for node1, line in enumerate(csvFile):
            for node2, edge in enumerate(line):
                if edge == '1':
                    g.write('{};{}\n'.format(node1, node2))
