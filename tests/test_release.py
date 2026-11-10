import unittest,sys,json,csv,math,ast,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reproduce import calculate,family_counts
from metrics import keyness
class ReleaseTests(unittest.TestCase):
    def test_frequencies_against_archived_audit(self):
        expected=json.loads((ROOT/'data/expected_frequencies.json').read_text())
        actual=calculate()
        for v,variants in actual.items():
            for variant,r in variants.items():
                e=expected[v][variant]
                self.assertEqual(r['tokens'],e['tokens']);self.assertEqual(r['documents'],e['documents'])
                for w,stats in r['wordforms'].items():
                    for k,value in stats.items():
                        if isinstance(value,float):self.assertAlmostEqual(value,e['wordforms'][w][k],places=9)
                        else:self.assertEqual(value,e['wordforms'][w][k])
    def test_document_integrity(self):
        rows=list(csv.DictReader((ROOT/'data/de_document_counts.csv').read_text(encoding='utf-8').splitlines()))
        self.assertEqual(len(rows),98)
        self.assertEqual(len({(r['version'],r['case_id']) for r in rows}),98)
        forms=json.loads((ROOT/'data/tokenization.json').read_text())['wordforms']
        for r in rows:
            self.assertGreater(int(r['tokens']),0)
            for w in forms:self.assertTrue(0<=int(r[w])<=int(r['tokens']))
        a={r['case_id']:r for r in rows if r['version']=='adopted'}
        b={r['case_id']:r for r in rows if r['version']=='without_english_story'}
        self.assertEqual(sum(int(r['tokens']) for r in a.values())-sum(int(r['tokens']) for r in b.values()),1217)
        for id in a:
            if id!='DE-160':
                self.assertEqual({k:v for k,v in a[id].items() if k!='version'},{k:v for k,v in b[id].items() if k!='version'})
    def test_portal_direction_stability(self):
        historical=json.loads((ROOT/'data/historical_and_stress_reference.json').read_text())['historical']
        for v in calculate().values():
            for variant,stats in v.items():
                for w,r in stats['wordforms'].items():self.assertEqual(r['direction'],historical[variant]['wordforms'][w]['direction'])
    def test_family_assignments(self):
        d=json.loads((ROOT/'data/family_assignments.json').read_text());ids=[i for members in d['CN']['families'].values() for i in members]
        self.assertEqual(len(ids),32);self.assertEqual(len(set(ids)),32);self.assertEqual(len(d['CN']['families']),12)
        for lang,n in [('DE',23),('EN',11)]:
            a=d['BookTok'][lang];self.assertEqual(len(a['assignments']),n)
            self.assertEqual(dict(Counter(a['assignments'].values())),a['counts'])
        self.assertEqual(d['BookTok']['DE']['assignments']['18'],'—')
    def test_sankey_conservation(self):
        tree=ast.parse((ROOT/'figures/figure_1/build_sankey.py').read_text())
        values={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['NODES','LINKS']}
        nodes={n[0]:n[4] for n in values['NODES']};incoming=Counter();outgoing=Counter()
        for a,b,n in values['LINKS']:
            self.assertIn(a,nodes);self.assertIn(b,nodes);self.assertGreater(n,0)
            outgoing[a]+=n;incoming[b]+=n
        for id,n in nodes.items():
            if id in incoming:self.assertEqual(incoming[id],n,id)
            if id in outgoing:self.assertEqual(outgoing[id],n,id)
        self.assertEqual(nodes['de_wort'],49);self.assertEqual(nodes['cn_kern'],32)
    def test_metrics_edge_cases(self):
        self.assertEqual(keyness(0,0,10,20)['g2'],0)
        self.assertEqual(keyness(1,2,10,20)['direction'],'equal')
        a=keyness(1,5,10,20);b=keyness(5,1,20,10)
        self.assertAlmostEqual(a['g2'],b['g2']);self.assertEqual(a['direction'],'lc');self.assertEqual(b['direction'],'lk')
        with self.assertRaises(ValueError):keyness(11,0,10,20)
    def test_figure_dimensions_and_labels(self):
        from pypdf import PdfReader
        for folder,stem,height,labels in [('figure_1','Abb_Korpus_Sankey_K3',178,['KI-Kern 32','Wortzählung 49','22 zugeordnet']),('figure_2','Abb_Autorschaft_K8',160,['DE-018','CN-022','BT-EN-A-001'])]:
            p=PdfReader(ROOT/'figures'/folder/(stem+'.pdf')).pages[0]
            self.assertAlmostEqual(float(p.mediabox.width)*25.4/72,120,places=3)
            self.assertAlmostEqual(float(p.mediabox.height)*25.4/72,height,places=3)
            for label in labels:self.assertIn(label,p.extract_text())
if __name__=='__main__':unittest.main()
