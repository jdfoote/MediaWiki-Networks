import re
import csv
import datetime
import igraph
#import networkx as nx
import sys


############ Goals: ###################
# High-level Goal
#   - Create network objects from edit data
#
# Technical Goals
#   - Work by streaming csv files instead of using SQL (i.e., no lookups)
#
# Network Types
#   - Co-editing (undirected) - A and B edit the same non-talk page within N 
#       edits/editors/seconds of each other => increment_edge(A,B)
#   - Collaboration (undirected) - network where edit_pattern = (A,B,C,...,A) =>
#       for e in edit_pattern: increment_edge(A, e) if A != e
#   - Talk (directed) - A and B edit the same talk page within N
#       edits/editors/seconds of each other OR
#       A edit's B's User_talk page => increment_edge(A,B)

# Idea space:
#   - Talk network. 
#       - Whether to connect people on Watercooler-type pages
#   - Sorting CSV will be required
#       - Sort by page, then timestamp should do the trick?


class EditNetwork(igraph.Graph):
    def __init__(self):
        super().__init__()
        self.temp_edges = []
    def new_edges(self, from_node, to_nodes):
        self.temp_edges += [[from_node, to_node] for to_node in to_nodes]
    def make_network(self):
        nodes = set([n for e in self.temp_edges for n in e])
        nodes = sorted(nodes)
        self.add_vertices(nodes)
        self.add_edges(self.temp_edges)
        self.es['weight'] = 1
    def collapse_weights(self):
        self.simplify(combine_edges={"weight": "sum"})



def make_network(edits, network_type="coedit", edit_limit=None, editor_limit=None,
        time_limit=None, section_filter=False):
    '''
    Creates a network object based on co-edits on the same page. Takes a list of edits.
    THESE MUST BE ORDERED, by page and by edit_time. Also takes a number
    of conditions that must exist for an edge to be created. edit_limit will create edges
    with the contributors of each of the last N edits (e.g., edit_limit = 1 means that
    only adjacent edits will result in edges.
    editor_limit is similar, but will create edges with the last N editors, while
    time_limit creates edges with all editors who have edited in the last N seconds.
    By default, there are no limits, and edges are created/incremented with all
    other contributors to the page.
    '''
    if network_type not in ['coedit', 'collaboration', 'talk']:
        raise Exception("network_type must be 'coedit', 'collaboration', or 'talk'")
    network = EditNetwork()
    curr_page = ''
    prev_edits = []
    for edit in edits:
        # Flag for whether this edit represents a collaboration (i.e., if
        # this editor has edited this page before, then intervening editors
        # are considered collaborators
        is_collaboration = False
        edit_is_talk_page = is_talk(edit)
        coeditors = []

        # If this is a talk network, then only look at talk pages. If it's a coedit
        # or collaboration network, then ignore talk pages
        if network_type != "talk" and edit_is_talk_page:
            continue
        if network_type == "talk":
            if edit_is_talk_page == False:
                continue
            else:
                # if this is a talk page, find out if it's a user talk page.
                # If it is, then create a talk edge between the editor and the
                # talk page owner
                page_owner = get_talk_page_owner(edit)
                if page_owner and page_owner != edit['editor']:
                    coeditors.append(page_owner)


        # If this is a new page, then reset stuff
        if edit['articleid'] != curr_page:
            curr_page = edit['articleid']
            prev_edits = [edit,]
            continue
        else:
            if edit_limit:
                prev_edits = prev_edits[-edit_limit:]
            # Go through each of the edits in reverse order, adding edges
            # to each. Once we find one that fails the tests, only keep
            # the edits after that one (since all others would also fail, 
            # for this and subsequent edits).
            for prev_edit in prev_edits[::-1]:
                if (
                        (editor_limit and len(coeditors) >= editor_limit) or
                        (time_limit and elapsed_time(edit, prev_edit) > time_limit)
                ):
                    # Only keep the good edits
                    prev_edits = prev_edits[-i:]
                    break
                # If we've already seen this contributor, then we stop looking for
                # more edges, because any edges previous to
                # this one will have been captured when we looked at this contributor
                # previously.
                #
                # We don't get rid of the other prev_edits, though, b/c they might
                # be valid edges for subsequent edits
                if same_editor(edit, prev_edit):
                    is_collaboration = True
                    break
                else:
                    # Don't add the same edge multiple times
                    if prev_edit['editor'] not in coeditors:
                        coeditors.append(prev_edit['editor'])
        # Create edges for each of the editors in the coeditor list
        if network_type != "collaboration" or is_collaboration == True:
            network.new_edges(edit['editor'],coeditors)
    network.make_network()
    network.collapse_weights()
    return network


def elapsed_time(edit1, edit2):
    return datetime.strptime(edit2['timestamp']) - datetime.strptime(edit1['timestamp'])

def is_talk(edit):
    return re.search('[Tt]alk', edit['namespace'])

def same_editor(edit1, edit2):
    return edit1['editor'] == edit2['editor']

def get_talk_page_owner(edit):
    '''Checks a talk page to see if it's a user talk page. If it is a user talk
    page, then returns the user name. Otherwise, returns None'''
    if edit['namespace'] == 'User_talk':
        return re.match('User_talk:(.*)$',edit['title']).group(1)
    else:
        return None


def getSectionFromComment(comment):
    '''Finds the section an edit was made to, based on the comment.

    The first edit to a section is formatted as "Section name [dd mon yyyy]".
    Subsequent edits are "/* Section name \* Comment here".
    If there is no section name, then return None.'''
    if comment:
        a = re.match(r'\/\* (.*) \*\/.*', comment)
        if a:
            return a.group(1).rstrip()
        b = re.match(r'(.*)\[[^]]*\]$', comment)
        if b:
            return b.group(1).rstrip()
    return None

