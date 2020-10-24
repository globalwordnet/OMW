from packaging.version import Version
from collections import (
    OrderedDict as od
)

### sort by language, project version (Newest first)
def fetch_sorted_meta_by_version(projects, src_meta, lang_idm, lang_codem):
    src_sort = od()
    keys = list(src_meta.keys())
    keys.sort(key=lambda x: Version(src_meta[x]['version']), reverse=True)  # Version
    keys.sort(key=lambda x: src_meta[x]['id'])  # id
    keys.sort(key=lambda x: lang_idm[lang_codem['code'][src_meta[x]['language']]][1])  # Language
    for k in keys:
        if projects == 'current':  # only get the latest version
            if src_meta[k]['version'] != max((src_meta[i]['version'] for i in src_meta
                                              if src_meta[i]['id'] == src_meta[k]['id']),
                                             key=lambda x: Version(x)):
                continue
        src_sort[k] = src_meta[k]

    return src_sort