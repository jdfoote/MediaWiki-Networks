MediaWiki-Networks
==================

This project is designed to take Wikimedia XML dump files and convert them into network files. 

The typical workflow is:
- Convert XML files to TSV files using the mediawiki_dump_tools
- Convert TSV files to networks
- Either store the networks as edgelists or visualize/create stats from them directly from the igraph objects

This imports mediawiki_dump_tools as a submodule. To use it:
From within the repository working directory, initiatlize and set up the submodule like::
	git submodule init
	git submodule update

An example project is in the example directory.

Pull requests are very welcome
