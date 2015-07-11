import csv
import argparse
import re
from mw.xml_dump import Iterator

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="input file location")
parser.add_argument("-o", help="output file location")
args = parser.parse_args()
in_fn = args.i
out_fn = args.o

# Construct dump file iterator
dump = Iterator.from_file(open(in_fn))

with open(out_fn, 'w') as o:
    output = csv.writer(o, delimiter = '\t', quotechar='|')
    output.writerow(['pageID','page_title','namespace','editor_id','username','timestamp','comment'])
    # Iterate through pages
    for page in dump:
        # Iterate through a page's revisions
        for rev in page:
            output.writerow([page.id, page.title, page.namespace,rev.contributor.user_text,
            rev.timestamp,rev.comment])
