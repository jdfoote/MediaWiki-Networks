import csv
from collections import defaultdict

csvLoc = '/home/jeremy/Dropbox/680Data.csv'
output = '/home/jeremy/Dropbox/680Edited2.csv'

editCats = {'family_edits':'simple_ratio','family_talk_edits': 'local_talk_ratio','person_edits': 'simple_ratio',
        'person_talk_edits': 'local_talk_ratio', 'place_edits': 'complex_ratio',
        'place_talk_edits': 'local_talk_ratio', 'article_edits': 'other_ratio', 'category_edits':'complex_ratio',
        'category_talk_edits': 'community_talk_ratio', 'givenname_edits':'complex_ratio',
        'givenname_talk_edits':'local_talk_ratio', 'help_edits': 'community_ratio',
        'help_talk_edits': 'community_talk_ratio','image_edits':'complex_ratio',
        'image_talk_edits': 'local_talk_ratio', 'mediawiki_edits': 'other_ratio',
        'mediawiki_talk_edits':'other_ratio', 'mysource_edits':'complex_ratio',
        'mysource_talk_edits':'local_talk_ratio','portal_edits':'complex_ratio',
        'portal_talk_edits':'community_talk_ratio','repository_edits':'complex_ratio',
        'repository_talk_edits':'local_talk_ratio', 'source_edits': 'complex_ratio',
        'source_talk_edits':'local_talk_ratio', 'surname_edits': 'complex_ratio',
        'surname_talk_edits': 'local_talk_ratio', 'talk_edits':'local_talk_ratio',
        'template_edits':'complex_ratio', 'template_talk_edits':'local_talk_ratio',
        'transcript_edits': 'complex_ratio','user_edits': 'complex_ratio',
        'user_talk_edits': 'local_talk_ratio', 'werelate_edits': 'community_ratio',
        'werelate_talk_edits': 'community_talk_ratio'}

with open(csvLoc, 'rb') as f:
    header = csv.reader(f).next()
    header = header[0:4] + ['manual_edits','simple_ratio','local_talk_ratio',
            'complex_ratio','other_ratio','community_ratio','community_talk_ratio'] + header[-3:]
with open(csvLoc, 'rb') as f:
    rows = csv.DictReader(f)
    results = []
    for row in rows:
        collapsedCats = defaultdict(int)
        fullData = {}
        allEdits = 0
        for c in row:
            if c in editCats:
                editCount = int(row[c])
                collapsedCats[editCats[c]] += editCount
                allEdits += editCount
            elif c in header:
                # If it's not in the category list, then just add it
                fullData[c] = row[c]
            else:
                print c
        # Get the ratios
        for k,v in collapsedCats.iteritems():
            if allEdits > 0:
                fullData[k] = float(v)/allEdits
            else:
                fullData[k] = 0
        fullData['manual_edits'] = allEdits
        assert len(fullData) == len(header)
        results.append([fullData[x] for x in header])

with open(output, 'wb') as f:
    o = csv.writer(f)
    o.writerow(header)
    o.writerows(results)
