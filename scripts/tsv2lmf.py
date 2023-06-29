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
parser.add_argument(
    '--version', help='version for this wordnet',
    default='1.0')
parser.add_argument(
    '--citation', help='citation for this wordnet (using rst)',
    default='...')
args = parser.parse_args()

###print(args.tsv)

log = open('log/tsv2wn_{}.log'.format(args.lang),'w')

open_license = {'CC BY 3.0':'https://creativecommons.org/licenses/by/3.0/',
                'CC-BY 3.0':'https://creativecommons.org/licenses/by/3.0/',
                'CC BY 4.0':'https://creativecommons.org/licenses/by/4.0/',
                'CC BY SA 3.0':'https://creativecommons.org/licenses/by-sa/3.0/',
                'CC BY-SA':'https://creativecommons.org/licenses/by-sa/',
                'CC BY SA':'https://creativecommons.org/licenses/by-sa/',
                'CC BY SA 4.0':'https://creativecommons.org/licenses/by-sa/4.0/',
                'Apache 2.0':'https://opensource.org/licenses/Apache-2.0',
                'CeCILL-C':'http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html',
                'MIT':'https://opensource.org/licenses/MIT/',
                'wordnet':'wordnet',
                'unicode':'https://www.unicode.org/license.html',
                'ODC-BY 1.0':'http://opendefinition.org/licenses/odc-by/'}

citation = '...'
if args.citation:
    try:
        cfh = open(args.citation)
        citation = html.escape(cfh.read().strip())
        cfh.close()
    except:
        citation = '...'
        
meta_default = { 'id': args.wnid, 
                 'label':'???',
                 'lang': args.lang,
                 'l639':  'unknown',
                 'email':'bond@ieee.org',
                 'license':'https://creativecommons.org/licenses/by/',
                 'version': args.version,
                 'citation':citation,
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
    ilimap[row[1]] = row[0]
    if row[1].endswith('-s'):
        ### map as either -s or -a
        ilimap[row[1].replace('-s','-a')] = row[0]

def clean(lemma):
    if lemma.startswith('"') and lemma.endswith('"'):
        lemma = lemma[1:-1]
        print('CLEANED: {} (removed start and end double quote)'.format(lemma), file=log)
    if '"' in lemma:
        print('WARNING: {} (contains a double quote)'.format(lemma), file=log)
    lemma = lemma.replace('_', ' ')    
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
    ss_defs = dd(lambda: dd(list)) # ssdefs['synsetID']['eng'] = [(0, "first English def"), ]
    ss_exes = dd(lambda: dd(list)) # ssexes['synsetID']['eng'] = [(0, "first English example"), ]
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
        else:
            print('UNKNOWN LICENSE', lce, file=sys.stderr)
            print('UNKNOWN LICENSE', lce, file=log)
        meta['license'] = html.escape(lce)
        meta['l639'] = l639.strip()

    else:
        print('NO META DATA', file=sys.stderr)
        
        
    for line in tab_file:
        if line == "\n" or line.startswith('#'):
            continue
        tab = line.split('\t')
        ##
        ## Process lines with lemmas
        ##
        if tab[1].endswith(':lemma') or tab[1] =='lemma':  # also check language?
            lex_c += 1

            ss = tab[0].strip().replace('-s', '-a')
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

        elif  tab[1].endswith('def'):
            ss = tab[0].strip().replace('-s', '-a')
            ssID = meta['id']+'-'+ss
            if len(tab[1].split(':')) > 1:
                lang = tab[1].split(':')[0].strip()
            else:
                lang = l639
            ### need to rewrite to bp47
            order = int(tab[2].strip())
            definition = tab[3].strip()
            ss_defs[ssID][lang].append((order, definition))
            #print ('ss_defs', ssID, lang, order, definition)
        elif  tab[1].endswith('exe'):
            ss = tab[0].strip().replace('-s', '-a')
            ssID = meta['id']+'-'+ss
            if len(tab[1].split(':')) > 1:
                lang = tab[1].split(':')[0].strip()
            else:
                lang = l639
            ### need to rewrite to bp47
            order = int(tab[2].strip())
            example = tab[3].strip()
            ss_exes[ssID][lang] .append((order, example))
        elif  tab[2].startswith('rel'):
            print('FIXME Sense link', line.strip(), file=log)
        else:
            print('FIXME Unknown type', line.strip(), file=log)

    return lexicon, meta, ss_defs,  ss_exes


################################################################################
# PRINT OUT
################################################################################

wn, wnmeta, ss_defs,  ss_exes = read_wn(ilimap, args.tsv)
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
    if ssID in ss_defs and \
       wnmeta['l639'] in  ss_defs[ssID]:
        #print  ('ss_defs[ssID]', ss_defs[ssID][wnmeta['l639']])
        dfn = "; ".join([html.escape(x[1], quote=False) for x in sorted(ss_defs[ssID][wnmeta['l639']])])
    else:
        dfn = ''
    if ssID in ss_exes and \
       wnmeta['l639'] in  ss_exes[ssID]:
        #print  ('ss_defs[ssID]', ss_defs[ssID][wnmeta['l639']])
        exe = "; ".join([html.escape(x[1], quote=False) for x in sorted(ss_exes[ssID][wnmeta['l639']])])
    else:
        exe = ''

    if dfn and exe:
        synEntry  = """    <Synset id="{}" ili="{}" partOfSpeech="{}">
      <Definition language="{}">{}</Definition>
      <Example language="{}">{}</Example>
    </Synset>""".format(ssID, ili, pos, args.lang, dfn, args.lang, exe)
    elif dfn:
            synEntry  = """    <Synset id="{}" ili="{}" partOfSpeech="{}">
      <Definition language="{}">{}</Definition>
    </Synset>""".format(ssID, ili, pos, args.lang, dfn)

    elif exe:
                synEntry  = """    <Synset id="{}" ili="{}" partOfSpeech="{}">
     <Example language="{}">{}</Example>
    </Synset>""".format(ssID, ili, pos, args.lang, exe)

    else: 
        synEntry  = """    <Synset id="{}" ili="{}" partOfSpeech="{}" />""".format(ssID, ili, pos)
    print(synEntry)

print(footer)
