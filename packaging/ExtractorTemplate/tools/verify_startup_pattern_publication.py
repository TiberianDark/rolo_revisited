"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "startup_pattern_publication",\n  "title": "startup pattern and colour publication contracts",\n  "sources": [\n    "src/core/startup_pattern_publication.hpp",\n    "tests/startup_pattern_publication_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 327936\n  },\n  "cases": 327936,\n  "specs": [\n    {\n      "address": 1886,\n      "ranges": [\n        [\n          1886,\n          1922\n        ]\n      ],\n      "contract": "Write native coordinate records128+D3 and8201+D4, publishX/0C00 OR D1/Y, incrementD1WORD/D4WORDby1/4, returnD0WORD128+D2; retainupperLONGhalves."\n    },\n    {\n      "address": 1922,\n      "ranges": [\n        [\n          1922,\n          1958\n        ]\n      ],\n      "contract": "Eightpaired075Epublicationswithsecondtilebase+32andD3WORD+6,thenfinalpairreplacesD1WORDwithD5WORDbeforelast075E;18recordpairs72dataWORDs,DBFlowWORDFFFF."\n    },\n    {\n      "address": 1958,\n      "ranges": [\n        [\n          1958,\n          1968\n        ]\n      ],\n      "contract": "D6WORD=D5WORD;D7WORD=D4WORD<<2;D6WORD+=D7WORD,WORDwrapandupperLONGhalvesretained."\n    },\n    {\n      "address": 1968,\n      "ranges": [\n        [\n          1968,\n          1990\n        ]\n      ],\n      "contract": "SuppliedC006dataLONGcopiedD3;SWAPD0intoD5,copyWORDintoD4;D5lowWORD=(originalhighWORD&7)<<2,D4lowWORD=ASR3thenASL5."\n    },\n    {\n      "address": 2062,\n      "ranges": [\n        [\n          2062,\n          2108\n        ]\n      ],\n      "contract": "OnlyD7WORD24publishescontrolC0120000,originalD0WORD,controlC0020000,andmaskedD0WORD;special0E86replaces0E22beforeAND0666;otherD7nooutputs."\n    }\n  ],\n  "proof": "Fulloriginalinstructionboundaries/WORDvsLONGmutationsandDBFloopreviewed. Onefocused327936caseassertionsenablednativepass:all65536WORDsforeachoffset/mask/palette/record/gatepartitionplus256actual18record72publicationloopfixtures,independentinteger/arithmetic/payloadoracle. Upperhalvesandwrapboundariesincluded.",\n  "scope": "Localnativefinitewritablecoordinatearraysandnonmutatingtypeddata/controlports. C006issupplieddataLONG,neverexecutedROMorCPUemulation. Originaldevicecadence,hoststartupscene,register/CCR/ABIandcallerbindingsnotcertified;notwholeinitialscreenfidelity."\n}')
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
