import sys
import csv
import re

fn = sys.argv[1]
with open(re.sub(r"\w+\.(\d+)\.tsv", r"placesOnly.\1.tsv", fn), 'w') as g:
	with open(fn, 'rb+') as f:

		csvFile = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
		csvFile.next()
		for line in csvFile:
			if line[1] == '106':
				g.write('{}\t{}\t{}\n'.format(line[0],line[1],line[2]))

