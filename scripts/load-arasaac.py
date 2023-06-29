#
# 
# read in the data from araasac
#
# first download wget  https://api.arasaac.org/api/pictograms/all/en
#
import json

with open('de') as f:
  data = json.load(f)

for entry in data:
  if entry['keywords']:
    print(entry['_id'], entry['synsets'], [k['keyword'] for k in entry['keywords']])
