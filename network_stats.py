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

coedit_net = nT.make_network(edits, "coedit")
talk_net = nT.make_network(edits, "talk")

with open(args.o, 'w') as output:
    o = csv.writer(output, delimiter="\t")
    o.writerow(['wiki_name', 'coedit_density','coedit_diameter',
        'coedit_clustering_coef', 'talk_density', 'talk_diameter', 'talk_clustering_coef'])
    o.writerow([fn, coedit_net.density(), coedit_net.diameter(),
                coedit_net.transitivity_undirected(),
                talk_net.density(), talk_net.diameter(),
                talk_net.transitivity_undirected()])

