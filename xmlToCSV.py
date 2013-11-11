import csv
#import sys
#import datetime
#import pickle
import lxml.etree as ET
import re

with open('pages-all.xml', 'rU') as f:
	NS = '{http://www.mediawiki.org/xml/export-0.3/}'
	with open('pagesCSV.csv', 'wb') as g:
		output = csv.writer(g, delimiter = '\t', quotechar='|')
		for event, elem in ET.iterparse(f):
			if elem.tag == '{0}page'.format(NS):
				pageTitle, pageID = '',''
				t = elem.find("{0}title".format(NS))
				if t is not None:
					pageTitle = t.text
				p = elem.find("./{0}id".format(NS))
				if p is not None:
					pageID = p.text
				revs = elem.findall("./{0}revision".format(NS))
				for r in revs:
					editor,revDate,comment,username = '','','',''
					e = r.find("./{0}contributor/{0}id".format(NS))
					if e is not None:
						editor = e.text
					d = r.find("./{0}timestamp".format(NS))
					if d is not None:
						revDate = d.text
					c = r.find("./{0}comment".format(NS))
					if c is not None:
						comment = c.text
					u = r.find("./{0}contributor/{0}username".format(NS))
					if u is not None:
						username = u.text
					output.writerow([u'{}'.format(re.sub('\n',' ',x)).encode('utf-8') for x in [pageID,pageTitle,editor,username,revDate,comment]])
				elem.clear()

				'''
				e = elem.findall(".//{0}contributor/{0}id".format(NS))
				if e is not None:
					editors = [a.text for a in e]
				r = elem.findall(".//{0}timestamp".format(NS))
				if r:
					revDates = [a.text for a in r]
				c = elem.findall('''
