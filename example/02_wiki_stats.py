import re
import pandas as pd
import sys
import csv
import argparse
from os import path
import networkTools as nT
from statistics import median, mean
import config

##### Parameters for making the network #####
# Edits must be within this many days of each other to create a link
TIME_LIMIT = None # None means there is no limit
# Edits must be within this many edits of each other
EDIT_LIMIT = 5

def main():

    parser = argparse.ArgumentParser(description='Create temporal measures from wiki')
    parser.add_argument('-i', help='Location of the tsv file of wiki edits')
    parser.add_argument('-t', type=int, help='Threshold number of edits')
    parser.add_argument('-o', type=str, help='Output file directory. Defaults to ./output',
            default='./output', nargs='?')
    parser.add_argument('--remove_anon', help='Pass this flag to remove anonymous contributors', action='store_true')
    parser.add_argument('-d', type=int, default=1,
            help='Value at which to dichotimize graph')
    parser.add_argument('--edgelist', help = 'If a file location is passed in, saves the edgelist to that location and quits.',
            default = None)

    args = parser.parse_args()


    wiki_name = re.match('(.*)\.tsv', path.split(args.i)[1]).group(1)
    OUTPUT_FILE_NAME = '{}/{}_stats.csv'.format(args.o,wiki_name)
    if path.isfile(OUTPUT_FILE_NAME):
        print('{} stats file already exists'.format(wiki_name))
        quit()

    print("Analyzing {} wiki".format(wiki_name))

    wiki_edits = nT.Edits(fn = args.i,
            threshold = args.t,
            remove_anon = args.remove_anon,
            cutoff_date = None)
    wiki_edits.clean_df()
    wiki_edits.threshold_filter(
            # Function that tells which edits to count toward the threshold edits.
            # In this case, main namespace edits that weren't reverted
            filter_func = lambda x: (x.namespace == 0) & (x.was_reverted==False))
    # If it has enough edits, then get the stats
    d = wiki_edits.df
    if d is None:
        print("Not enough edits in {}".format(args.i))
        quit()
    # Create a df of just the main ns edits
    d_main_edits = d[d['namespace'] == 0]
    # Get the edit counts by editor
    editors = d_main_edits.groupby('editor')
    # Create networks
    talk_net = make_network(wiki_edits, dichotomize_level=args.d)
    if args.edgelist:
        talk_net.write_edgelist(args.edgelist)
        quit()
    if not talk_net:
        print('No users in graph for {}'.format(wiki_name))
        quit()
    # Get the subgraphs which only includes active editors
    with open(OUTPUT_FILE_NAME, 'w') as f:
        o = csv.writer(f)
        o.writerow(['wiki.name',
                    'main.ns.edits',
                    'talk.ns.edits',
                    'network.nodes',
                    'mean.weight',
                    'median.weight',
                    'degree.gini',
                    'betweenness.gini',
                    'density',
                    'diameter',
                    'clustering.coef',
                    'kcore.gt.2',
                    'kcore.gt.1',
                    'hierarchy',
                    'gini.main.ns.edits.non.reverted',
                    'founding.date'
                    ])
        o.writerow([wiki_name,
                    # total edits (in main namespace)
                    len(d_main_edits),
                    # Talk edits 
                    wiki_edits.num_talk_edits(),
                    # Network size
                    talk_net.vcount(),
                    # Mean weight of edges
                    talk_net.mean_weight(),
                    talk_net.median_weight(),
                    # Centralization measures
                    gini(talk_net.indegree()),
                    gini(talk_net.betweenness()),
                    # Density
                    talk_net.density(),
                    # Diameter
                    talk_net.diameter(),
                    # Clustering
                    talk_net.transitivity_undirected(),
                    # Ratio of members with k-shell number greater than 2 (one measure of core-periphery)
                    kcore_ratio(talk_net,2),
                    kcore_ratio(talk_net,1),
                    # Hierarchy
                    talk_net.hierarchy(),
                    gini(d_main_edits[d_main_edits.was_reverted == False].groupby('editor').size()),
                    # Date of first edit
                    d['date_time'].iloc[0],
                    ])


def get_betweenness(graph, editor):
    '''These are hacks. For the talk networks, the founder might not be in the network.
    If that happens, we get a ValueError. These functions just return 0 in that case.
    I could have put the error catching in the class function, but there may be cases
    where you expect that an editor will be in the graph, and so the error should
    be raised'''
    try:
        return graph.betweenness(editor)
    except ValueError:
        return 0

def get_effective_size(graph, editor):
    try:
        return graph.effective_size(editor)
    except ValueError:
        return 0

def kcore_ratio(graph, k):
    '''Looks at the k-core value for each vertex (this is the highest k for
    which the vertex is in a subgraph where all of the vertices have at least
    k edges). Returns the proportion of vertices whose k-core value is greater
    than k'''
    shells = graph.coreness()
    try:
        return len([x for x in shells if x > k]) / len(shells)
    except ZeroDivisionError:
        return None

def make_network(df, dichotomize_level=1):
    # Put df in order by page, then edit time.
        return nT.make_talk_network(edits = df,
                edit_limit = EDIT_LIMIT,
                time_limit = TIME_LIMIT,
                dichotomize_level=dichotomize_level)

def gini(x):
    '''Code transferred from R reldist package (https://www.rdocumentation.org/packages/reldist/versions/1.6-6/topics/gini).
    Takes in a list of values and calculates the gini for them'''
    if len(x) < 2 or max(x) == 0:
        return None
    weights = [1/len(x)]*len(x)
    x = pd.Series(x)
    x = x.sort_values()
    p = pd.Series(weights).cumsum() # Perfect equality
    nu = (weights*x.values).cumsum()
    n = len(nu)
    nu = nu / nu[n-1] # Normalization of values
    return (nu[1:n]*p[:n-1]).sum() - (nu[:n-1]*p[1:n]).sum()


if __name__ == '__main__':
    main()

