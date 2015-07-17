import argparse
import subprocess, shlex
import csv
import networkTools as nT

parser = argparse.ArgumentParser(description='Get network stats from edit data')
parser.add_argument('-i',
                   help='input file')
parser.add_argument('-o',
                   help='output file')
args = parser.parse_args()


fn = args.i
# Sort the CSV file, and create a csv.DictReader object
with open(fn, 'r') as f:
    header_row = f.readline().strip().split('\t')

p1 = subprocess.Popen(shlex.split('tail -n +2 {}'.format(fn)), stdout=subprocess.PIPE)
p2 = subprocess.Popen(shlex.split("sort -t'\t' -k2,2n -k3,3"), stdin=p1.stdout, stdout=subprocess.PIPE)
output = p2.communicate()[0]
output = output.decode('utf-8')
edits = csv.DictReader(output.splitlines(), delimiter="\t", fieldnames=header_row)

n = nT.make_coedit_network(edits)
print(n.density())
