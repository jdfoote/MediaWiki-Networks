MediaWiki-Networks
==================
This is a bunch of code that I've been using to collect data from the XML dump of edit history for users of the WeRelate website.

Right now, it can produce three types of networks: co-editing, collaboration, and talk.

- Co-editing networks are undirected, and and edge is created (or incremented) between $i$ and $j$ iff $i$ and $j$ have edited the same page.
- Collaboration networks are similar, but only increment/create an edge between $i$ and $j$ if $i$ edits, then $j$ edits, then at some later point, $i$ edits again.
- Finally, talk networks generally work like co-editing networks, only they are directed, such that if $i$ edits the page after $j$, $i$ is assumed to be talking to $j$. In addition, the talk networks tries to find the owner of a user talk page, and makes an edge from the editor of the page to the owner.

The network_stats.py is a simple example of how you might retrieve networks statstics form a newtork.
