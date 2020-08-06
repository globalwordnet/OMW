#
# 
# read in the data from araasac
#
# first download wget  https://api.arasaac.org/api/pictograms/all/en
#
import json

with open('en') as f:
  data = json.load(f)

for entry in data:
    print(entry['_id'], entry['synsets'], [k['keyword'] for k in entry['keywords']])
