"""Deterministic, fictional first-attempt inspection cohort. No external packages."""
import csv, random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['InspectionID','VehicleID','Date','Model','Shift','Station','Result','Defect','ReworkMinutes','UpdatedAt']
def generate():
    rng = random.Random(47)
    rows = []
    for day in range(28):
        stamp = (date(2026, 8, 1) + timedelta(days=day)).isoformat()
        for v in range(30):
            vehicle = f'DEMO-{day*30+v+1:05d}'
            model = ['Compact A','Compact B'][v % 2]
            shift = ['A','B','C'][v % 3]
            for stage, station in enumerate(['Body','Paint','Final']):
                fail = rng.random() < (0.16 - 0.003 * day + (0.04 if station == 'Paint' else 0))
                defect = rng.choice({'Body':['Panel gap','Weld appearance'],'Paint':['Surface inclusion','Paint finish'],'Final':['Fit and finish','Function check']}[station]) if fail else 'None'
                rows.append(dict(zip(FIELDS,[f'{vehicle}-{stage+1}',vehicle,stamp,model,shift,station,'FAIL' if fail else 'PASS',defect,rng.randint(8,50) if fail else 0,stamp+'T16:00:00'])))
    # Controlled corrections: an old duplicate says PASS but the later authoritative row says FAIL.
    for r in [x for x in rows if x['Result']=='FAIL'][:10]:
        older = dict(r, Result='PASS', Defect='None', ReworkMinutes=0, UpdatedAt=r['Date']+'T08:00:00')
        rows.append(older)
    # Valid whitespace/case variations exercise normalization.
    for r in rows[20:30]: r['Station']=' '+r['Station'].lower()+' '; r['Result']=' '+r['Result'].lower()+' '
    bad = [dict(rows[0],InspectionID='BAD-DATE',Date='not-a-date'),dict(rows[0],InspectionID='BAD-RESULT',Result='UNKNOWN'),dict(rows[0],InspectionID='BAD-MINUTES',ReworkMinutes=-5),dict(rows[0],InspectionID='BAD-VEHICLE',VehicleID='')]
    rows.extend(bad)
    # Stable shuffle ensures dedup does not accidentally rely on input ordering.
    rng.shuffle(rows)
    path=ROOT/'data'/'inspections_raw.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
    return path
if __name__=='__main__': print(generate())
