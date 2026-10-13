import argparse, datetime, hashlib, pathlib, shutil, zipfile

APP=r'Src\App.pa.yaml'
SCREEN=r'Src\scrCutoverReadinessDash.pa.yaml'
COMP=r'Src\Components\cmpECCSCutoverReadinessDsh.pa.yaml'

def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--msapp',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args()
 source=pathlib.Path(a.msapp); out=pathlib.Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 if not source.is_file(): raise SystemExit('Input .msapp not found')
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');backup=out/f'ORIGINAL_{stamp}.msapp';shutil.copy2(source,backup)
 target=out/f'ECCS_REG_DASH_PATCHED_{stamp}.msapp';log=[]
 with zipfile.ZipFile(source) as z:
  names=z.namelist()
  for name in (APP,SCREEN,COMP):
   if name not in names: raise SystemExit(f'Missing expected source: {name}. Backup: {backup}')
  content={n:z.read(n) for n in names}
  app=content[APP].decode('utf-8-sig');screen=content[SCREEN].decode('utf-8-sig');comp=content[COMP].decode('utf-8-sig')
  anchor='      ClearCollect(\n          colRegReadiness,'
  if app.count(anchor)!=1: raise SystemExit('App.OnStart anchor not unique; refusing edit')
  if 'ClearCollect(\n          colReadinessFacilities,' not in app:
   init='''      // REG-DASH: initialize schema before colRegReadiness references it.
      ClearCollect(
          colReadinessFacilities,
          Filter('dim.Ref.Organizations', false)
      );
'''
   app=app.replace(anchor,init+anchor,1);log.append('App.OnStart: initialize colReadinessFacilities')
  else:log.append('App.OnStart: collection already initialized; skipped')
  if '      OnVisible: |+' in screen and '      OnVisible: |+\n        =\n' in screen:
   screen=screen.replace('      OnVisible: |+\n        =\n','      OnVisible: |+\n        =',1)
   log.append('Screen.OnVisible: removed standalone equals line')
  else:log.append('Screen.OnVisible: no standalone equals line detected')
  # Add native KPI cards without touching pre-existing controls or formulas.
  if 'lblREGDashTotalKPI:' not in comp:
   cards=[('Total','Total Configuration Records','Total Records',115),('Mapped','Mapped Records','Mapped Records',380),('NoMatch','NO MATCH Records','No Match Records',645),('Readiness','Mapping Readiness %','Readiness Percentage',910)]
   chunks=[]
   for key,title,field,x in cards:
    if key=='Readiness':
     formula='=If(CountRows(colECCSReadinessSnapshots)=0, "No data", Text(First(colECCSReadinessSnapshots).\'Readiness Percentage\', "0.0") & "%")'
    else:
     formula=f'=If(CountRows(colECCSReadinessSnapshots)=0, "No data", Text(Sum(colECCSReadinessSnapshots, \'{field}\'), "#,##0"))'
    chunks.append(f'''      - lblREGDash{key}Caption:
          Control: ModernText@1.0.0
          Properties:
            Text: ="{title}"
            Font: =Font.Arial
            Size: =11
            Color: =ColorValue("#54585A")
            X: ={x}
            Y: =350
            Width: =245
            Height: =28
      - lblREGDash{key}KPI:
          Control: ModernText@1.0.0
          Properties:
            Text: {formula}
            Font: =Font.Arial
            FontWeight: =FontWeight.Bold
            Size: =22
            Color: =ColorValue("{'#E05929' if key=='NoMatch' else '#03173E'}")
            X: ={x}
            Y: =380
            Width: =245
            Height: =48
''')
   comp=comp.rstrip()+ '\n' + ''.join(chunks)
   log.append('Component: appended 4 native KPI cards; blank-table display is No data')
  else:log.append('Component: KPI cards already exist; skipped')
  content[APP]=app.encode('utf-8');content[SCREEN]=screen.encode('utf-8');content[COMP]=comp.encode('utf-8')
  with zipfile.ZipFile(source) as zin, zipfile.ZipFile(target,'w') as zout:
   for info in zin.infolist():zout.writestr(info,content[info.filename])
  with zipfile.ZipFile(target) as verify:
   bad=verify.testzip()
   if bad:raise SystemExit(f'ZIP integrity failed: {bad}')
  report=out/'REG-DASH_BULK_PATCH_LATEST.txt'
  report.write_text('\n'.join(['REG-DASH bulk patch',f'Input: {source}',f'Backup: {backup}',f'Patched: {target}',f'Original SHA256: {sha(source.read_bytes())}',f'Backup SHA256: {sha(backup.read_bytes())}',f'Patched SHA256: {sha(target.read_bytes())}',*log,'ZIP integrity: PASS','PAC pack / Studio App Checker: NOT YET VERIFIED','No Dataverse records were created or populated.']),encoding='utf-8')
  print(report.read_text(encoding='utf-8'))
if __name__=='__main__':main()
