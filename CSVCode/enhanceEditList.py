import csv
import sys
import re

fn = sys.argv[1]
categoryList =["Media", "Special", "Talk", "User", "User talk", "WeRelate", "WeRelate talk", "Image", "Image talk", "MediaWiki", "MediaWiki talk", "Template", "Template talk", "Help", "Help talk", "Category", "Category talk", "Givenname", "Givenname talk", "Surname", "Surname talk", "Source", "Source talk", "Place", "Place talk", "Person", "Person talk", "Family", "Family talk", "MySource", "MySource talk", "Repository", "Repository talk", "Portal", "Portal talk", "Transcript", "Transcript talk"]
output = 'EnhancedEditList.tsv'

def filterNodes(editFile, output):
    '''Takes a TSV file of edits and adds metadata about the edits'''
    badCategories = []
    TranscriptPages = []
    index = 1
    for row in editFile:
        newRow = [row[0], row[1], '', row[2], row[3], row[4], row[5], 'false']
        pageName, user_id, comment = row[1], row[2], row[-1]
        category = re.match("([^:]*):", pageName)
        # Check for top-level pages
        if not category or category.group(1) not in categoryList:
            category = 'Article'
            if category:
                badCategories.append(pageName)
                if pageName[:1] == ':':
                    category = 'Transcript'
                    row[1] = 'Transcript:{}'.format(pageName)
                    TranscriptPages.append(pageName)
        else:
            category = category.group(1)
        newRow[2] = category
        if comment[:6] == 'Propag':
            newRow[-1] = 'true'
        output.writerow(newRow)
        if index % 100000 == 0 : print index
        index += 1
    print set(badCategories)
    print set(TranscriptPages)

if __name__ == "__main__":
    with open(fn, 'rb') as f:
        with open(output, 'wb') as g:
            editFile = csv.reader(f, delimiter="\t", quotechar="|")
            output = csv.writer(g, delimiter = '\t', quotechar='|')
            output.writerow(['page_id', 'page_name', 'page_category', 'user_id', 'user_name',
                'edit_time', 'comment', 'is_propagation'])
            filterNodes(editFile, output=output)
