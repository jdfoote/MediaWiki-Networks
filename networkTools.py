import re
import csv
import datetime
import igraph
import sys
from statistics import mean, median
from collections import namedtuple
import pandas as pd
import config


############ Goals: ###################
# High-level Goal
#   - Create network objects from edit data
#
# Network Types
#   - Co-editing (undirected) - A and B edit the same non-talk page within N 
#       edits/editors/seconds of each other => increment_edge(A,B)
#   - Collaboration (undirected) - network where edit_pattern = (A,B,C,...,A) =>
#       for e in edit_pattern: increment_edge(A, e) if A != e
#   - Talk (directed) - A and B edit the same talk page within N
#       edits/editors/seconds of each other OR
#       A edit's B's User_talk page => increment_edge(A,B)

class Edits:

    def __init__(self,
            fn,
            remove_anon = False,
            threshold = None,
            cutoff_date = None # Ignore edits after this date
            ):

        self.fn = fn
        self.threshold = threshold
        self.remove_anon = remove_anon
        self.cutoff_date = cutoff_date

    # Use the non-filtered version to find the last period of mutli-editor activity
    def clean_df(self):
        try:
            self.df = pd.read_csv(self.fn, delimiter='\t', doublequote=False,
                    dtype={'reverteds':object})
        except ValueError:
            print("No lines in", fn)
            self.df = None
        except:
            print("Error was:", sys.exc_info()[0])
            raise
        # Mark reverted edits (want to include bot reverts since these could be spam)
        self.mark_reverted_revs()
        # Just making it easier to refer to self.df
        d = self.df
        # Find the automated edits
        bots = d['editor'].apply(self.is_bot)
        # Store how many there were
        self.bot_edit_count = len(bots)
        # Remove the automated edits
        d = d[~bots]
        # Find the duplicate edits
        dup_edits = d.apply(lambda x: (x['editor'], x['sha1']) in config.bad_sha_list, axis=1)
        self.dup_edit_count = sum(dup_edits)
        d = d[~dup_edits]
        # Clean out any odd dates
        # Start by removing obvious errors (since these can break pd.to_datetime)
        good_dates = d['date_time'].str.startswith('2')
        self.bad_date_count = len(d) - sum(good_dates)
        d = d[good_dates]
        # Then convert to datetime
        d['date_time'] = pd.to_datetime(d['date_time'], errors="raise")
        # Then remove rows with other suspicious dates
        good_dates = (d['date_time'] > '2004-01-01') & (d['date_time'] < '2010-04-10')
        self.bad_date_count += len(d) - sum(good_dates)
        d = d[good_dates]
        if self.cutoff_date != None:
            d = d[d['date_time'] < self.cutoff_date] # Pretend like data collection happened at cutoff_date
        d = d.sort_values('date_time')
        # Anons aren't always marked correctly, so recalculate this based on whether the
        # user name is an IP address
        d['anon'] = d.editor.apply(is_anon)
        self.df = d
        return None

    def threshold_filter(self, filter_func = lambda x: True):
        d = self.df
        # Anons aren't always marked correctly, so recalculate this based on whether the
        # user name is an IP address
        d['anon'] = d.editor.apply(is_anon)
        if self.remove_anon:
            d = d[d['anon']==False]
        if self.threshold == None:
            self.df = d.copy()
            return None
        num_edits = len(d[d.apply(filter_func, axis=1)])
        # Figure out if there are enough edits to meet our criteria
        if num_edits >= self.threshold:
            # Only grab the edits that occur before the threshold 
            # (We do this by sorting by date and then summing the main ns edits and
            # removing any edits whose date is greater than the Nth main ns edit
            to_include = d.apply(filter_func, axis=1).cumsum()
            filtered_d = d[to_include <= self.threshold].copy()

            # Get the last active dates before we discard the newer edits
            self.final_edit = d['date_time'].iloc[-1]
            self.last_activity = self.get_last_active(n_days=30, n_editors = 2, min_date = filtered_d['date_time'].iloc[-1])
            d = filtered_d
            # Add quality score for each edit
            d['quality'] = d.apply(lambda x: quality_score(x), axis = 1)
            self.df = d
        else:
            self.df = None


    def mark_reverted_revs(self):
        # Create a list of all of the reverted ids
        temp_list = list(self.df.loc[self.df.reverteds.notna(), 'reverteds'])
        # Some of them are actually a list of ids, so we need to split them.
        reverteds = []
        for x in temp_list:
            reverteds += x.split(',')
        self.df['was_reverted'] = self.df.revid.isin(reverteds)


    def is_bot(self, editor):
        if editor in config.editor_ignore_list or config.bot_query.match(editor):
            return True
        else:
            return False

    def num_talk_edits(self):
        return len(self.df[self.df['namespace'] % 2 ==1])

    def edits_iterator(self):
        temp_df = self.df.sort_values(['articleid','date_time'])
        rows = temp_df.iterrows()
        while rows:
            yield next(rows)[1]

class EditNetwork(igraph.Graph):

    def __init__(self):
        super().__init__(directed=True)
        self.temp_edges = []

    def median_weight(self):
        return median(self.es['weight'])

    def mean_weight(self):
        return mean(self.es['weight'])

    def make_network(self, edges):
        if len(edges) == 0:
            return None
        nodes = set([e.from_node for e in edges] + [e.to_node for e in edges])
        nodes = list(nodes)
        self.add_vertices(nodes)
        self.add_edges([(e.from_node, e.to_node) for e in edges])
        self.es['weight'] = 1
        # for each attribute, create a list of the values, and add it
        # to the list of edges
        for att in edges[0]._fields:
            if att not in ['from_node', 'to_node']:
                self.es[att] = [getattr(e, att) for e in edges]
        # Collapsing edges; any filtering should happen before this step
        self.collapse_weights()

    def subgraph(self, vertices):
        v_names = [x['name'] for x in self.vs()]
        return self.induced_subgraph([v for v in vertices if v in v_names])

    def get_edgelist_with_atts(self):
        '''Writes out an edgelist, followed by edge attributes'''
        output = []
        # Get attribute names from first edge
        attributes = sorted(self.es[0].attribute_names())
        for e in self.es:
            output.append([self.vs[e.source]['name'], #Name of the source node
                self.vs[e.target]['name']] + # Name of the target node
                [e.attributes()[x] for x in attributes]) # All of the attributes
        return {'header':['from_node','to_node'] + attributes, 'data':output}


    def collapse_weights(self):
        # This will combine edges, summing the weights,
        # adding the minimum time, and simplifying the attributes

        def min_with_none(x):
            filtered_list = [y for y in x if y is not None]
            return min(filtered_list) if filtered_list else None

        self.simplify(combine_edges={'weight':'sum',
            'from_time':'min',
            'from_anon': 'first',
            'to_anon': 'first',
            'timediff': min_with_none,
            'intermediate_edits': min_with_none,
            'intermediate_editors': min_with_none
            })


    def make_undirected(self):
        '''Makes a graph undirected and sums the weights'''
        self.to_undirected(combine_edges={'weight':'sum',
            # There is a bug here - when making undirected, the from and to nodes can be
            # switched, so anonymity is not preserved.
            'from_anon':'first',
            'to_anon':'first',
            'from_time':'min'})


    def dichotomize(self, threshhold = 1):
        edges_to_keep = [e for e in self.es if e['weight'] >= threshhold]
        temp = self.subgraph_edges(edges_to_keep)
        #temp.es['weight'] = 1
        return temp

    def betweenness(self, vertices=None, normalized=True):
        '''Takes a single vertex or list of vertices, and returns the betweenness from igraph.
        If normalized == True, then normalizes based on the constant used by ipython in R'''

        def normalize_val(x):
            # This is the normalization used by ipython in R (http://igraph.org/r/doc/betweenness.html)
            if x == 0:
                return 0
            else:
                return x * 2 / (n*n - 3*n + 2)

        #if sum(self.es['weight']) != len(self.es()):
            #print('Converting to binary network for betweeness centrality')
            #self.dichotomize()

        non_normalized_betweenness = super(EditNetwork, self).betweenness(vertices=vertices)
        n = self.vcount()

        if normalized == True:
            try:
                # If it's just a float, then normalize and return
                return normalize_val(non_normalized_betweenness)
            except TypeError:
                # Otherwise, normalize the whole list, and return
                return [normalize_val(x) for x in non_normalized_betweenness]
        else:
            return non_normalized_betweenness

    def hierarchy(self):
        '''Returns the hierarchy measure created by Krackhardt(1994) for the graph.
        This is defined as the ratio of paths in the graph which are cyclical/reciprocated.
        For a given path from v_i to v_j, the path is cyclical if there also exists a path
        from v_j to v_i.'''
        if not self.is_directed():
            raise ValueError("Hierarchy measure is only available on directed networks")
        # Get the shortest paths (this tells us whether there is a path between any two nodes)
        p = self.shortest_paths()
        # Number of hierarchical paths (non-cycles)
        h_paths = 0
        # Number of cyclical paths 
        cycles = 0
        for i in range(len(p)):
            for j in range(len(p)):
                # Check if a path exists between the nodes
                if i != j and p[i][j] != float('inf'):
                    # If it does, and the reciprocal path also exist, increment the cycle count
                    if p[j][i] < float('inf'):
                        cycles += 1
                    else:
                        # Otherwise, increment the h_paths count
                        h_paths += 1
        # Return the ratio of h_paths
        if h_paths == cycles == 0:
            return None
        return h_paths / (h_paths + cycles)

    def effective_size(self, vertex):
        ego_neighbors = self.neighbors(vertex)
        neighbor_graph = self.induced_subgraph(ego_neighbors)
        # Calculation of effective size, as described at http://www.analytictech.com/ucinet/help/hs4126.htm
        # First, get the degree of all the neighbors
        ng_degree = neighbor_graph.degree()
        # Then average the degree, and subtract it from the number of neighbors
        return len(ng_degree) - sum(ng_degree)/len(ng_degree)

def make_coedit_network(
        # Function to use to filter namespaces. By default, it's all non-talk namespaces.
        # To get just the main ns, use lambda x: x == 0
        namespace_filter=lambda x: x % 2 == 0,
        **kwargs): # Additional arguments to pass to make_network
    kwargs['edits'] = (x for x in kwargs['edits'] if namespace_filter(x['namespace']))
    network = make_network(**kwargs)
    return network

def make_talk_network(namespace_filter=lambda x: x % 2 == 1,
        # Determines whether to include edges where User A writes on User B's
        # talk page, whether or not User B writes back.
        include_user_talk = True,
        **kwargs):
    network = make_network(namespace_filter = namespace_filter,
            **kwargs)
    if not include_user_talk:
        network = network.remove_user_talk()
    return network

def make_collaboration_network(namespace_filter=lambda x: x % 2 == 0,
        **kwargs):
    # TODO: Add filter to only collaborative edits
    kwargs['edits'] = (x for x in kwargs['edits'] if namespace_filter(x['namespace']))
    network = make_network(**kwargs)
    network = network.only_collaborative_edits()
    return network

Edge = namedtuple('Edge', ['from_node',
                            'to_node',
                            'from_anon',
                            'to_anon',
                            'edit_type',
                            'timediff',
                            'intermediate_edits',
                            'intermediate_editors'])
Edge.__new__.__defaults__ = (None,) * len(Edge._fields)


def make_network(edits,
        edit_limit=None,
        editor_limit=None,
        time_limit=None,
        section_filter=False,
        dichotomize_level=1,
        namespace_filter = lambda x: True
        ):
    '''
    Creates a network object based on co-edits on the same page. Takes an Edit object.
    Also takes a number of parameters that determine whether and edge should be created.
    edit_limit will create edges with the contributors of each of the last N edits
    (e.g., edit_limit = 1 means that only adjacent edits will result in edges).
    editor_limit is similar, but will create edges with the last N editors, while
    time_limit creates edges with all editors who have edited in the last N days.
    By default, there are no limits, and edges are created/incremented with all
    other contributors to the page.
    '''

    def edges_from_page_edits(page_edits):
        '''Go through each edit to a page and figure out which
        subsequent edits should have edges to this edit'''
        if len(page_edits) == 0:
            return []
        edges = []
        # If it's a talk page, figure out the owner
        page_owner = get_talk_page_owner(page_edits[0])
        for i, edit in enumerate(page_edits):
            # Reset temp variables
            curr_edges = []
            curr_editors = []
            curr_section = get_section_from_comment(edit) if section_filter else None
            curr_time = edit['date_time']
            intermediate_edits = 1

            # If this is a talk page, then add edges to the owner of the page
            if page_owner and page_owner != edit['editor']:
                edges.append(make_user_talk_edge(edit, page_owner))

            # Now loop through all subsequent edits
            for j in range(i+1, len(page_edits)):
                new_edit = page_edits[j]
                # If the sections don't match, then pretend like this edit doesn't exist
                if section_filter and get_section_from_comment(new_edit) != curr_section:
                    continue

                # If this edit is too late then break (since all future
                # edits will also be too late)
                new_time = new_edit['date_time']

                # If they are the same person, then mark the previous edits as
                # collaborative, and break the inner loop
                # (since future edges will be captured once we get to this
                # edit in the main loop)
                if same_editor(edit,new_edit):
                    curr_edges = [e._replace(edit_type = 'collaborative') for e in curr_edges]
                    break

                # Add this editor to the set of editors, if necessary
                if new_edit['editor'] in curr_editors:
                    # One edit can't result in multiple
                    # edges to the same alter. E.g., if A edits the page
                    # and then B, C, B edit the page A will only have 1 tie with B. 
                    # So, don't add the edge but increment the edit count
                    intermediate_edits += 1
                    continue
                else:
                    curr_editors.append(new_edit['editor'])

                # Create a new edge, and add it
                curr_edges.append(Edge(
                    from_node = new_edit['editor'],
                    to_node = edit['editor'],
                    edit_type = 'normal',
                    from_anon = new_edit['anon'],
                    to_anon = edit['anon'],
                    timediff = new_time - curr_time,
                    intermediate_edits = intermediate_edits,
                    intermediate_editors = len(curr_editors),
                    ))
                intermediate_edits += 1

                # Now check the other parameters and break if they are met
                if (
                        # We incremented this so if it's larger then break
                        (edit_limit and intermediate_edits > edit_limit) or
                        # If the next editor is already in the list then we won't create an edge
                        # So as long as we've reached the limit now we are safe to break
                        (editor_limit and len(curr_editors) == editor_limit)
                        ):
                    break
            # At the end of the loop, add the edges
            edges += curr_edges
        return edges

    def make_user_talk_edge(edit, page_owner):
        return Edge(from_node = edit['editor'],
                    to_node = page_owner,
                    from_anon = edit['anon'],
                    to_anon = is_anon(page_owner),
                    edit_type = 'user_talk_owner'
                    )



    '''The basic logic is that we identify all the edits on a single
    page, then convert that page's edits to edges and move on to the
    next page'''
    time_limit = datetime.timedelta(days = time_limit) if time_limit else None
    all_edges = []
    curr_page = ''
    curr_page_edits = []

    edits = (x for x in edits.edits_iterator() if namespace_filter(x['namespace']))
    for edit in edits:
        if edit['articleid'] != curr_page:
            all_edges += edges_from_page_edits(curr_page_edits)
            curr_page_edits = [edit]
            curr_page = edit['articleid']
        else:
            curr_page_edits.append(edit)
    # Get the last pages edges
    all_edges += edges_from_page_edits(curr_page_edits)
    # Make the network
    network = EditNetwork()
    network.make_network(all_edges)
    network = network.dichotomize(dichotomize_level)
    if len(network.vs) == 0:
        return None
    return network


def make_timestamp(edit):
    return datetime.datetime.strptime(edit['date_time'], '%Y-%m-%d %H:%M:%S')


def is_anon(username):
    '''Check if a username is an ipv4 ip address. We use this as
    a marker of whether the user is anonymous'''
    if re.match('([0-9]{1,3}\.){3}[0-9]{1,3}',username):
        return True
    else:
        return False


def same_editor(edit1, edit2):
    return edit1['editor'] == edit2['editor']

def get_talk_page_owner(edit):
    '''Checks a talk page to see if it's a user talk page (ASSUMES THAT
    THESE ARE NAMESPACE 3). If it is a user talk
    page, then returns the user name. Otherwise, returns None'''
    if edit['namespace'] == 3:
        return re.match('[^:]+:(.*)$',edit['title']).group(1)
    else:
        return None


def get_section_from_comment(edit):
    '''Finds the section an edit was made to, based on the comment.

    ASSUMPTION:
    The first edit to a section is formatted as "Section name [dd mon yyyy]".
    Subsequent edits are "/* Section name \* Comment here".
    If there is no section name, then return None.'''
    try:
        comment = edit['comment']
    except KeyError:
        return None
    if comment:
        a = re.match(r'\/\* (.*) \*\/.*', comment)
        if a:
            return a.group(1).rstrip()
        b = re.match(r'(.*)\[[^]]*\]$', comment)
        if b:
            return b.group(1).rstrip()
    return None

