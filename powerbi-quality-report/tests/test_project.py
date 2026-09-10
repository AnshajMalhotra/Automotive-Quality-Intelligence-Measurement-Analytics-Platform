import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_data import clean,metrics
class QualityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with (ROOT/'data/inspections_raw.csv').open() as f:cls.raw=list(csv.DictReader(f))
  cls.rows,cls.rejected,cls.dupes=clean(cls.raw)
 def test_accounting_and_results(self):
  self.assertEqual(len(self.raw),len(self.rows)+len(self.rejected)+self.dupes)
  self.assertEqual((len(self.rejected),self.dupes),(4,10))
  m=metrics(self.rows)
  self.assertEqual((m['failed_inspections'],m['first_pass_vehicles']),(324,562))
  self.assertAlmostEqual(m['vehicle_fpy'],562/840)
 def test_latest_version_retained(self):
  ids={r['InspectionID'] for r in self.raw if r['UpdatedAt'].endswith('08:00:00')}
  self.assertEqual(len(ids),10)
  self.assertTrue(all(r['Result']=='FAIL' for r in self.rows if r['InspectionID'] in ids))
 def test_empty_and_incomplete(self):
  self.assertIsNone(metrics([])['vehicle_fpy'])
  self.assertIsNone(metrics([])['inspection_defect_rate'])
  self.assertEqual(metrics(self.rows[1:])['complete_vehicles'],839)
 def test_report_bindings(self):
  model=json.loads((ROOT/'Quality.SemanticModel/model.bim').read_text())['model']
  tables={t['name']:{c['name'] for c in t['columns']}|{m['name'] for m in t.get('measures',[])} for t in model['tables']}
  visuals=list((ROOT/'Quality.Report').rglob('visual.json'))
  self.assertEqual(len(visuals),11)
  for path in visuals:
   v=json.loads(path.read_text())
   for role in v['visual']['query']['queryState'].values():
    for p in role['projections']:
     f=next(iter(p['field'].values()))
     self.assertIn(f['Property'],tables[f['Expression']['SourceRef']['Entity']])
  for r in model['relationships']:
   self.assertIn(r['fromColumn'],tables[r['fromTable']]);self.assertIn(r['toColumn'],tables[r['toTable']])
if __name__=='__main__':unittest.main()
