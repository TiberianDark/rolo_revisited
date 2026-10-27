"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "startup_reset_entries",\n  "title": "startup RAM and display reset payload plus tile pair publication",\n  "sources": [\n    "src/core/startup_reset_entries.hpp",\n    "tests/startup_reset_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 67584\n  },\n  "cases": 67584,\n  "specs": [\n    {\n      "address": 2272,\n      "ranges": [\n        [\n          2272,\n          2438\n        ]\n      ],\n      "contract": "Clear exactly 65500 work RAM bytes, retain final 36 bytes; enter display reset critical section, publish 15 original register words, clear 16384 display LONGs, select pattern destination and call generator with zero, select final destination, negate generated WORD, leave critical section."\n    },\n    {\n      "address": 2992,\n      "ranges": [\n        [\n          2992,\n          3002\n        ]\n      ],\n      "contract": "Write incoming tile WORD and its wrapped successor to auto-incrementing data port; return tile plus two modulo 65536."\n    }\n  ],\n  "proof": "Original instruction boundaries and DBF iteration counts reviewed. All 65536 pair inputs plus 2048 reset cases independently check order, original constants, all RAM bytes including preserved tail, child mutation retention, display zero count and return WORD boundaries. Test event count fixture corrected after first failed check, then focused family passed.",\n  "scope": "Local reset payload with returning synchronous data/control services and platform begin/end critical-section adapter. Original physical SR/register ABI, hardware timing, generator internals and SDL integration are outside this contract."\n}')
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
slug=CONFIG['name'].replace('_','-');result=root/('work/'+slug+'-results.json');r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==CONFIG['results']
sources=list(CONFIG['sources']);pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
exe=root/('work/'+CONFIG['name']+'_verification_tests.exe');assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
sources+=CONFIG.get('dependencies',[])
for at,expected in CONFIG.get('data_pins',[]):assert rom[at:at+len(bytes.fromhex(expected))].hex()==expected
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for lo,hi in CONFIG.get('boundary_extensions',[]):
 assert CONFIG.get('boundary_basis') and CONFIG.get('boundary_producers')
 for source,encoded in CONFIG['boundary_producers']:assert rom[source:source+len(bytes.fromhex(encoded))].hex()==encoded
 cursor=lo
 while cursor<hi:
  accepted.add(cursor);cursor+=Decoder(rom,cursor).decode()['size']
 assert cursor==hi
for spec in CONFIG['specs']:
 start=spec['address'];ranges=spec['ranges'];items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 end=max(b for a,b in ranges)
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: '+CONFIG['title'],native_sources=spec.get('native_sources',[CONFIG['sources'][0]]),checked_cases=spec.get('cases',CONFIG['cases']),contract=spec['contract'],proof=CONFIG['proof'],scope=spec.get('scope',CONFIG['scope'])))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/('docs/stage9/'+slug+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(str(len(records))+' local contracts registered: '+slug)
