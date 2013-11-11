import sys
import re

fn = sys.argv[1]
with open(re.sub(r"\w+\.(\d+).csv", r"placesOnly.\1.tsv", fn), 'w') as g:
	with open(fn, 'r') as f:
		q = re.compile(r'(\d+),(\d+),(.*)')
		for line in f:
			g.write(re.sub(q, r'\1\t\2\t\3', line))


