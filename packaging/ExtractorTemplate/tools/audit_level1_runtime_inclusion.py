"""Source inclusion census only: inclusion is not proof of a runtime call."""
import json,re
from pathlib import Path
p=Path(__file__).resolve().parents[1]
seen=set()
def visit(name):
 if name in seen:return
 path=p/name
 if not path.is_file():return
 seen.add(name)
 for inc in re.findall(r'^\s*#include\s+"([^"]+)"',path.read_text(),re.M):
  target=p/'src'/inc
  if target.is_file():visit(target.relative_to(p).as_posix())
visit('src/main.cpp')
d=p/'docs/stage9'
candidates=set(json.loads((d/'level1-current-candidates.json').read_text())['candidate_addresses'])
rows=[]
for r in json.loads((d/'inventory.json').read_text())['routines']:
 if r['address'] not in candidates:continue
 sources=[s for s in r['native_sources'] if s.startswith('src/') and (p/s).is_file()]
 included=[s for s in sources if s in seen]
 rows.append(dict(address=r['hex'],subsystem=r['subsystem'],sources=sources,included_sources=included,source_included=bool(included)))
out=dict(scope='Conservative Level1 candidate set, including sound. Source inclusion only; does not establish that a routine is called, bound correctly or faithful.',candidate_count=len(rows),source_included=sum(r['source_included'] for r in rows),outside_source_closure=sum(not r['source_included'] for r in rows),rows=rows)
(d/'level1-runtime-inclusion-current.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='rows'})
