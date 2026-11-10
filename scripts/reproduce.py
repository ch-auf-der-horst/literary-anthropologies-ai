"""Recalculate published aggregates from document-level sufficient statistics."""
import csv,json
from collections import Counter
from pathlib import Path
from metrics import keyness
ROOT=Path(__file__).resolve().parents[1]
def calculate():
    rows=list(csv.DictReader((ROOT/'data/de_document_counts.csv').read_text(encoding='utf-8').splitlines()))
    forms=json.loads((ROOT/'data/tokenization.json').read_text())['wordforms']
    result={}
    for version in ['adopted','without_english_story']:
        result[version]={}
        for variant in ['all','without_mixed','without_mixed_and_summaries']:
            selected=[r for r in rows if r['version']==version and
                not (variant!='all' and int(r['mixed'])) and
                not (variant=='without_mixed_and_summaries' and int(r['summary']))]
            groups={g:[r for r in selected if r['portal']==g] for g in ['lk','lc']}
            totals={g:sum(int(r['tokens']) for r in rs) for g,rs in groups.items()}
            words={}
            for w in forms:
                counts={g:sum(int(r[w]) for r in rs) for g,rs in groups.items()}
                words[w]={**{g+'_count':n for g,n in counts.items()},
                    **{g+'_document_frequency':sum(int(r[w])>0 for r in rs) for g,rs in groups.items()},
                    **keyness(counts['lk'],counts['lc'],totals['lk'],totals['lc'])}
            result[version][variant]={'tokens':totals,'documents':{g:len(rs) for g,rs in groups.items()},'wordforms':words}
    return result

def family_counts():
    data=json.loads((ROOT/'data/family_assignments.json').read_text())
    return {'CN':{f:len(ids) for f,ids in data['CN']['families'].items()},
        'BT_DE':dict(Counter(data['BookTok']['DE']['assignments'].values())),
        'BT_EN':dict(Counter(data['BookTok']['EN']['assignments'].values()))}

if __name__=='__main__':
    out=ROOT/'results';out.mkdir(exist_ok=True)
    (out/'frequencies.json').write_text(json.dumps(calculate(),ensure_ascii=False,indent=2)+'\n')
    (out/'family_counts.json').write_text(json.dumps(family_counts(),ensure_ascii=False,indent=2)+'\n')
    print('Reproduced 84 wordform comparisons and CN / BookTok family counts.')
