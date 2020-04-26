# 
#  Take an OMW 1.0 wordnet tsv and convert to LMF
# 
# 

import sys
import argparse
from collections import defaultdict as dd
import html
meta =  dict()


parser = argparse.ArgumentParser(
    description='A program to make wordnet LMF from OMW 1.0 tsv',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)


parser.add_argument(
    'wnid', help='wordnet ID (short unique name)')
parser.add_argument(
    'lang', help='language code (BCP 47)')
parser.add_argument(
    'ili_map', help='ili mapping')
parser.add_argument(
    'tsv', help='tsv file to be parsed')
args = parser.parse_args()

###print(args.tsv)

log = open('tsv2wn_{}.log'.format(args.lang),'w')

open_license = {'CC BY 3.0':'https://creativecommons.org/licenses/by/3.0/',
                'CC BY 4.0':'https://creativecommons.org/licenses/by/4.0/',
                'CC BY SA 3.0':'https://creativecommons.org/licenses/by-sa/3.0/',
                'Apache 2.0':'https://opensource.org/licenses/Apache-2.0',
                'CeCILL-C':'http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html',
                'MIT':'https://opensource.org/licenses/MIT/'}

meta_default = { 'id': args.wnid, 
                 'label':'???',
                 'lang': args.lang,
                 'email':'bond@ieee.org',
                 'license':'https://creativecommons.org/licenses/by/',
                 'version':'1.0',
                 'citation':'...',
                 'url':'...',
                 'description':"Wordnet made from OMW 1.0 data",
                 'conf':'1.0' }


def print_header(meta, comment):
    """print the header of the lexicon, filled in with meta data"""

    header = str()

    header += ("""<?xml version="1.0" encoding="UTF-8"?>\n""")
    header += ("""<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.0.dtd">\n""")
    header += ("""<LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">\n""")

    if comment:
        header += ("""<!-- {}  -->\n""".format(comment))

    header += ("""  <Lexicon id="{}" \n""".format(meta['id']))
    header += ("""           label="{}" \n""".format(meta['label']))
    header += ("""           language="{}" \n""".format(meta['lang']))
    header += ("""           email="{}" \n""".format(meta['email']))
    header += ("""           license="{}" \n""".format(meta['license']))
    header += ("""           version="{}" \n""".format(meta['version']))
    header += ("""           citation="{}" \n""".format(meta['citation']))
    header += ("""           url="{}" \n""".format(meta['url']))
    header += ("""           dc:publisher="Global Wordnet Association" \n""")
    header += ("""           dc:format="OMW-LMF" \n""")
    header += ("""           dc:description="{}" \n""".format(meta['description']))
    header += ("""           confidenceScore="{}">""".format(meta['conf']))

    return header

def print_footer():

    footer = str()
    footer += ("  </Lexicon>\n")
    footer += ("</LexicalResource>")

    return footer


ilimap = dd(str)
map_file = open(args.ili_map,'r')
for l in map_file:
    row = l.strip().split()
    ilimap[row[1].replace('-s','-a')] = row[0]

def clean(lemma):
    if lemma.startswith('"') and lemma.endswith('"'):
        lemma = lemma[1:-1]
        print('CLEANED: {} (removed start and end double quote)'.format(lemma), file=log)
    if '"' in lemma:
        print('WARNING: {} (contains a double quote)'.format(lemma), file=log)
    return lemma
    
def read_wn(ilimap, fn):
    """
    Given a .tab+ file (also ready for forms), 
    it prepares lexical entries and senses

    meta is a dictionary of meta data
    meta['label'] = 'Wordnet Bahasa'
    

    """

    wn = dd(lambda:set())
    lexicon = dd(lambda: dd(lambda: dd(lambda:set())))
    meta = meta_default
    tab_file = open(fn, 'r')
    lex_c = 0
    header = tab_file.readline()
    if header.startswith('# '):
        (lbl,
         l639,
         url,
         lce) = header[2:].strip().split('\t')
        meta['label'] = html.escape(lbl)
        meta['url'] = html.escape(url)
        if lce in open_license:
            lce = open_license[lce]
        meta['license'] = html.escape(lce)

    else:
        print('NO META DATA', file=sys.stderr)
        
        
    for line in tab_file:
        if line == "\n" or line.startswith('#'):
            continue
        tab = line.split('\t')
        ##
        ## Process lines with lemmas
        ##
        if tab[1].endswith(':lemma'):  # also check language?
            lex_c += 1

            ss = tab[0].strip()
            lemma = tab[2].strip()
            lemma = clean(lemma)
            pos = ss[-1].replace('s', 'a')

            var_end = len(tab) - 1
            variants = set()
            for v in tab[3:]:
                variants.add(v.strip())


            ssID = meta['id']+'-'+ss

            if lexicon['Lex'][(lemma,tuple(variants),pos)]['lexID']:
                lexID = list(lexicon['Lex'][(lemma,tuple(variants),pos)]['lexID'])[0]
            
            else:
                lexID = meta['id']+'-'+'lex'+str(lex_c)


            senseID = lexID+'-'+ss

            lexicon['Synset'][ssID]['pos'].add(pos)
            lexicon['Synset'][ssID]['ili'].add(ilimap[ss])
            lexicon['Lex'][(lemma,tuple(variants),pos)]['lexID'].add(lexID)
            lexicon['LexEntry'][lexID]['lemma'].add(lemma)
            lexicon['LexEntry'][lexID]['pos'].add(pos)
            for var in variants:
                lexicon['LexEntry'][lexID]['variants'].add(var)
            lexicon['LexEntry'][lexID]['sense'].add(ssID)
        elif  tab[2].startswith('rel'):
            print('Sense link', line.strip())
        else:
            print('Unknown type', line.strip())

    return lexicon, meta


################################################################################
# PRINT OUT
################################################################################

wn, wnmeta = read_wn(ilimap, args.tsv)
header = print_header(wnmeta, "OMW 1.0 converted to 2.0 by tsv2lmf.py")
footer = print_footer()



print(header)

for lexID in wn['LexEntry']:

    lexEntry = str()
    lexEntry += """    <LexicalEntry id="{}">\n""".format(lexID)

    lemma = list(wn['LexEntry'][lexID]['lemma'])[0]
    pos = list(wn['LexEntry'][lexID]['pos'])[0]
    lexEntry += """      <Lemma writtenForm="{}" partOfSpeech="{}"/>\n""".format(html.escape(lemma),pos)

    variants = wn['LexEntry'][lexID]['variants']
    for v in variants:
        lexEntry += """      <Form  writtenForm="{}"></Form>\n""".format(html.escape(v))

    senses = wn['LexEntry'][lexID]['sense']
    for ssID in senses:
        senseID = lexID+'-'+ssID[5:]
        lexEntry += """      <Sense id="{}" synset="{}"></Sense>\n""".format(senseID,ssID)

    lexEntry += """    </LexicalEntry>"""
    
    print(lexEntry)


for ssID in wn['Synset']:
    pos = list(wn['Synset'][ssID]['pos'])[0]
    ili = list(wn['Synset'][ssID]['ili'])[0]
    synEntry = """    <Synset id="{}" ili="{}" partOfSpeech="{}"></Synset>""".format(ssID, ili, pos)
    
    print(synEntry)

print(footer)
