"""Independent Python reference for the M pipeline and DAX KPI definitions.
Does not execute Power Query or DAX. Run those acceptance checks in Desktop.
"""
import csv,json
from datetime import date,datetime
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def clean(rows):
    accepted=[];rejected=[]
    for rownum,raw in enumerate(rows):
        r={k:str(v).strip() for k,v in raw.items()};r['Station']=r['Station'].title();r['Result']=r['Result'].upper();r['Shift']=r['Shift'].upper()
        try:
            date.fromisoformat(r['Date']);datetime.fromisoformat(r['UpdatedAt']);mins=float(r['ReworkMinutes'])
            assert r['InspectionID'] and r['VehicleID']
            assert r['Station'] in ['Body','Paint','Final'] and r['Model'] in ['Compact A','Compact B'] and r['Shift'] in ['A','B','C']
            assert r['Result'] in ['PASS','FAIL'] and mins>=0
            assert (r['Result']=='PASS' and r['Defect']=='None' and mins==0) or (r['Result']=='FAIL' and r['Defect'] in ['Panel gap','Weld appearance','Surface inclusion','Paint finish','Fit and finish','Function check'])
            r['ReworkMinutes']=mins;r['_Row']=rownum;accepted.append(r)
        except (ValueError,AssertionError):rejected.append(raw)
    ordered=sorted(accepted,key=lambda r:(r['UpdatedAt'],r['_Row']),reverse=True)
    unique={}
    for r in ordered: unique.setdefault(r['InspectionID'],r)
    return sorted(unique.values(),key=lambda r:r['InspectionID']),rejected,len(accepted)-len(unique)
def metrics(rows):
    grouped=defaultdict(list)
    for r in rows:grouped[r['VehicleID']].append(r)
    vehicles=[]
    for key,rs in grouped.items():
        consistent=all(len({r[c] for r in rs})==1 for c in ['Date','Model','Shift'])
        complete=consistent and len(rs)==3 and {r['Station'] for r in rs}=={'Body','Paint','Final'}
        vehicles.append({'id':key,'complete':complete,'pass':complete and all(r['Result']=='PASS' for r in rs)})
    n=len(rows);fails=sum(r['Result']=='FAIL' for r in rows);eligible=sum(v['complete'] for v in vehicles);passed=sum(v['pass'] for v in vehicles)
    defects=Counter(r['Defect'] for r in rows if r['Result']=='FAIL')
    return {'inspections':n,'failed_inspections':fails,'inspection_defect_rate':fails/n if n else None,'vehicles':len(vehicles),'complete_vehicles':eligible,'first_pass_vehicles':passed,'vehicle_fpy':passed/eligible if eligible else None,'rework_hours':sum(r['ReworkMinutes'] for r in rows)/60,'defects':dict(sorted(defects.items(),key=lambda x:(-x[1],x[0])))}
def main():
    with (ROOT/'data/inspections_raw.csv').open() as f:rows=list(csv.DictReader(f))
    valid,rejected,dupes=clean(rows);result=metrics(valid)
    result.update(raw_rows=len(rows),rejected_rows=len(rejected),duplicate_rows_removed=dupes)
    assert result['inspections']==2520 and result['vehicles']==840
    assert len(rejected)==4 and dupes==10
    assert result['complete_vehicles']==840
    (ROOT/'data/expected_kpis.json').write_text(json.dumps(result,indent=2)+'\n')
    with (ROOT/'data/inspections_clean_reference.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=[k for k in valid[0] if k!='_Row']);w.writeheader();w.writerows({k:v for k,v in r.items() if k!='_Row'} for r in valid)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
