"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "text_tile_publication",\n  "title": "text tile payload publication",\n  "sources": [\n    "src/core/text_tile_publication.hpp",\n    "tests/text_tile_publication_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 262157\n  },\n  "cases": 262157,\n  "specs": [\n    {\n      "address": 24240,\n      "ranges": [\n        [\n          24240,\n          24330\n        ]\n      ],\n      "contract": "Low19cursor gate and nonzeroerase row; signedWORD arithmetic shift3, WORDadd/mask/shift7/base; exactVDPcommand encoding then32LONGzero writes."\n    },\n    {\n      "address": 24466,\n      "ranges": [\n        [\n          24466,\n          24622\n        ]\n      ],\n      "contract": "8F02 then two independently addressed glyph rows; WORDglyph<<2 ORattributes then wrapping+2,+1,+1,+1 tile stores; signedcursor row, WORDrowmask and address truncations."\n    },\n    {\n      "address": 26188,\n      "ranges": [\n        [\n          26188,\n          26248\n        ]\n      ],\n      "contract": "8F02; nested WORDDBF loops, source sequentialWORD masked07FF then wrapped attributes addition; address+128LONG eachrow; saved column counter restored, finalrowcounterFFFF."\n    },\n    {\n      "address": 28716,\n      "ranges": [\n        [\n          28716,\n          28760\n        ]\n      ],\n      "contract": "WORDcharacter subtract32/add07B4 wrap before ORattributes; original address command from lowWORD; oneWORDtile publication."\n    },\n    {\n      "address": 28760,\n      "ranges": [\n        [\n          28760,\n          28820\n        ]\n      ],\n      "contract": "Copy originalX/Y to saved words, destinationWORD=base+2X+(Y<<7), return fullLONGsource without changing input fields."\n    }\n  ],\n  "proof": "Static original boundaries/branches reviewed. One focused optimized assertions-enabled test: all65536WORD glyph/character/layout inputs with independently computed packet oracle and varied masks/attributes/cursors;196608scroll gate/address cases;13rectangle shapes including65536WORD column/row DBF extremes, addressLONGwrap, source sequential masks and preserved state. NoROMexecution.",\n  "scope": "Local state and ordered typed control/data publication packets with readable immutable source extent. Ports are nonmutating observers; arbitrary service mutation of original shared RAM, originalVDPdevice semantics, retainedCPUregister/CCR state, full caller admission and SDLbinding remain external. Rectangle1..65536rows/columns requires native source capacity; exhausted spans reject. Not whole-screen fidelity."\n}')
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
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: '+CONFIG['title'],native_sources=[CONFIG['sources'][0]],checked_cases=spec.get('cases',CONFIG['cases']),contract=spec['contract'],proof=CONFIG['proof'],scope=spec.get('scope',CONFIG['scope'])))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/('docs/stage9/'+slug+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(str(len(records))+' local contracts registered: '+slug)
