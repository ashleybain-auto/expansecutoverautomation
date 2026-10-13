import argparse, pathlib, datetime, json, re
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',default='diagnostics');a=p.parse_args()
root=pathlib.Path(a.source).resolve(); out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
files=list(root.rglob('*.yaml'))+list(root.rglob('*.yml'))+list(root.rglob('*.fx.yaml'))
terms=['cmpECCSCutoverReadinessDsh','Screen 01','Readiness','DataSources','ComponentDefinitions']
lines=['ECCS READ-ONLY INVENTORY',f'Source: {root}',f'Files: {len(files)}','']
for f in files:
 try: s=f.read_text(encoding='utf-8-sig')
 except:continue
 matches=[t for t in terms if t.lower() in s.lower() or t.lower() in str(f).lower()]
 if matches:
  lines.append(f'{f.relative_to(root)} | matches: {", ".join(matches)}')
  for i,line in enumerate(s.splitlines(),1):
   if any(t.lower() in line.lower() for t in terms):lines.append(f'  L{i}: {line[:180]}')
(out/'ECCS_Dashboard_Inventory.txt').write_text('\n'.join(lines),encoding='utf-8')
print('Wrote',out/'ECCS_Dashboard_Inventory.txt')
