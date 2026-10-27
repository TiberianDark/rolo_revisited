"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "startup_image_scene",\n  "title": "original startup geometry image and layout publication payload",\n  "sources": [\n    "src/core/startup_image_scene.hpp",\n    "tests/startup_image_scene_verification_tests.cpp"\n  ],\n  "dependencies": [\n    "tests/fixtures/startup-scene-reference.bin"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 64\n  },\n  "cases": 64,\n  "specs": [\n    {\n      "address": 2438,\n      "ranges": [\n        [\n          2438,\n          2992\n        ]\n      ],\n      "contract": "Generate original two geometry planes with nine-row height/cap data and fractional97B4/4BDA steps, publish each576 LONGs, compose three native18-record layout groups, decode originalC7C image via nativeBBAcodec into work RAM and dictionary, publish palette/patterns/rectangular tiles plus decorative tile pairs, set startup scroll226; return exhausted WORDcounterFFFF."\n    }\n  ],\n  "data_pins": [\n    [\n      3142,\n      "01010202030304040606040302020201020101010101000101000100010000000100000000000002070a0a070004080b0e151c251e0046080000"\n    ]\n  ],\n  "proof": "Original complete162-instruction payload and child call argument/state progression reviewed; independent Python reference reconstructs entire65536-byte RAM and ordered typed data/control event stream for64 different RAM seeds and incoming WORDs. Native uses previously verified pattern records, pixel writer and forward image codec; actual pinned original compressed image decoded as DATA. All64 complete payload comparisons passed.",\n  "scope": "Pinned original image/tables,64 tested RAM/initial-word partitions, synchronous typed publication services. Full native child composition; physical VDP timing/register ABI, initial interrupt orchestration and SDL startup adoption outside local contract."\n}')
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
