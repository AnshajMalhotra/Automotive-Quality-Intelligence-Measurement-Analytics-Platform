"""Build editable Power BI project source; does not run Power BI Desktop."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def write(path,data):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
measures={
 'Inspections':('COUNTROWS(FactInspection)','#,0'),
 'Failed inspections':('CALCULATE([Inspections], KEEPFILTERS(FactInspection[Result] = "FAIL"))','#,0'),
 'Inspection defect rate':('DIVIDE([Failed inspections], [Inspections])','0.0%'),
 'Complete vehicles':('CALCULATE(COUNTROWS(FactVehicle), FactVehicle[Complete] = TRUE())','#,0'),
 'First-pass vehicles':('CALCULATE(COUNTROWS(FactVehicle), FactVehicle[FirstPass] = TRUE())','#,0'),
 'Vehicle FPY':('DIVIDE([First-pass vehicles], [Complete vehicles])','0.0%'),
 'Rework hours':('DIVIDE(SUM(FactInspection[ReworkMinutes]), 60)','0.0'),
 'Defect rate last 7 days':('VAR EndDate = MAX(DimDate[Date])\nRETURN CALCULATE([Inspection defect rate], REMOVEFILTERS(DimDate), DATESBETWEEN(DimDate[Date], EndDate - 6, EndDate))','0.0%')}
(ROOT/'dax').mkdir(exist_ok=True)
(ROOT/'dax/measures.dax').write_text('\n\n'.join(n+' =\n'+e for n,(e,_) in measures.items())+'\n')
for name,col,values in [('DimModel','Model',['Compact A','Compact B']),('DimShift','Shift',['A','B','C']),('DimStation','Station',['Body','Paint','Final'])]:
 (ROOT/f'power-query/{name}.m').write_text('#table(type table ['+col+' = text], {'+', '.join('{"'+v+'"}' for v in values)+'})\n')
tables={
'FactInspection':{'InspectionID':'string','VehicleID':'string','Date':'dateTime','Model':'string','Shift':'string','Station':'string','Result':'string','Defect':'string','ReworkMinutes':'double'},
'FactVehicle':{'VehicleID':'string','Date':'dateTime','Model':'string','Shift':'string','InspectionCount':'int64','FailCount':'int64','Complete':'boolean','FirstPass':'boolean'},
'DimDate':{'Date':'dateTime','Year':'int64','Month':'string','WeekStart':'dateTime'},
'DimModel':{'Model':'string'},'DimShift':{'Shift':'string'},'DimStation':{'Station':'string'},
'DataAudit':{'RawRows':'int64','RejectedRows':'int64','DuplicateRows':'int64','CleanRows':'int64'},
'RejectedRows':{'InspectionID':'string','VehicleID':'string','Date':'string','Station':'string','Result':'string','ReworkMinutes':'string','Issue':'string'}}
model={'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','tables':[],'relationships':[],'expressions':[]}
for p in sorted((ROOT/'power-query').glob('*.m')):
 if p.stem not in tables and 'example' not in p.stem:
  model['expressions'].append({'name':p.stem,'kind':'m','expression':p.read_text().splitlines()})
for name,cols in tables.items():
 t={'name':name,'columns':[{'name':c,'dataType':typ,'sourceColumn':c,'summarizeBy':'none',**({'formatString':'yyyy-MM-dd'} if typ=='dateTime' else {})} for c,typ in cols.items()], 'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':(ROOT/f'power-query/{name}.m').read_text().splitlines()}}]}
 if name=='FactInspection': t['measures']=[{'name':n,'expression':e.splitlines(),'formatString':fmt} for n,(e,fmt) in measures.items()]
 model['tables'].append(t)
for fact in ['FactInspection','FactVehicle']:
 for dim,col in [('DimDate','Date'),('DimModel','Model'),('DimShift','Shift')]+([('DimStation','Station')] if fact=='FactInspection' else []):
  model['relationships'].append({'name':fact+'_'+dim,'fromTable':fact,'fromColumn':col,'toTable':dim,'toColumn':col,'crossFilteringBehavior':'oneDirection'})
write(Path('Quality.SemanticModel/model.bim'),{'name':'Quality','compatibilityLevel':1600,'model':model})
write(Path('Quality.SemanticModel/definition.pbism'),{'version':'1.0','settings':{}})
write(Path('Quality.pbip'),{'version':'1.0','artifacts':[{'report':{'path':'Quality.Report'}}],'settings':{'enableAutoRecovery':True}})
base='https://developer.microsoft.com/json-schemas/fabric/item/report/'
write(Path('Quality.Report/definition.pbir'),{'$schema':base+'definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Quality.SemanticModel'}}})
write(Path('Quality.Report/definition/version.json'),{'$schema':base+'definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
write(Path('Quality.Report/definition/report.json'),{'$schema':base+'definition/report/3.1.0/schema.json','themeCollection':{}})
write(Path('Quality.Report/definition/pages/pages.json'),{'$schema':base+'definition/pagesMetadata/1.0.0/schema.json','pageOrder':['qualityoverview'],'activePageName':'qualityoverview'})
page=Path('Quality.Report/definition/pages/qualityoverview')
write(page/'page.json',{'$schema':base+'definition/page/2.0.0/schema.json','name':'qualityoverview','displayName':'Quality overview | synthetic data','displayOption':'FitToPage','width':1280,'height':800})
def field(table,name,measure=False): return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
def visual(name,kind,title,x,y,w,h,roles):
 query={role:{'projections':[{'field':field(t,n,m),'queryRef':t+'.'+n,'nativeQueryRef':n} for t,n,m in values]} for role,values in roles.items()}
 write(page/f'visuals/{name}/visual.json',{'$schema':base+'definition/visualContainer/2.1.0/schema.json','name':name,'position':{'x':x,'y':y,'z':0,'width':w,'height':h,'tabOrder':0},'visual':{'visualType':kind,'query':{'queryState':query},'visualContainerObjects':{'title':[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},'text':{'expr':{'Literal':{'Value':"'"+title+"'"}}}}}]}}})
for i,(m,title) in enumerate([('Inspections','Inspections'),('Inspection defect rate','Inspection defect rate'),('Vehicle FPY','Vehicle FPY | all stations'),('Rework hours','Recorded rework hours')]):
 visual('kpi'+str(i),'card',title,20+i*315,20,300,120,{'Data':[('FactInspection',m,True)]})
for i,(t,c) in enumerate([('DimDate','Date'),('DimModel','Model'),('DimShift','Shift')]):visual('filter'+str(i),'slicer',c,20+i*420,155,400,80,{'Values':[(t,c,False)]})
visual('trend','lineChart','Daily inspection defect rate',20,250,760,260,{'Category':[('DimDate','Date',False)],'Y':[('FactInspection','Inspection defect rate',True)]})
visual('defects','clusteredBarChart','Failed inspections by defect',800,250,460,260,{'Category':[('FactInspection','Defect',False)],'Y':[('FactInspection','Failed inspections',True)]})
visual('stations','tableEx','Station results | FPY above covers all stations',20,530,760,240,{'Values':[('DimStation','Station',False),('FactInspection','Inspections',True),('FactInspection','Failed inspections',True),('FactInspection','Inspection defect rate',True),('FactInspection','Rework hours',True)]})
visual('audit','tableEx','Import audit | entire refresh, unaffected by slicers',800,530,460,240,{'Values':[('DataAudit',n,False) for n in tables['DataAudit']]})
print('Generated model, 11 visuals, and 8 DAX measures.')
if __name__=='__main__': pass
