"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "animation_spawn_entries",\n  "title": "animation inherited and randomized spawn contracts",\n  "sources": [\n    "src/core/animation_spawn_entries.hpp",\n    "tests/animation_spawn_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 131072\n  },\n  "cases": 131072,\n  "specs": [\n    {\n      "address": 65156,\n      "ranges": [\n        [\n          65156,\n          65160\n        ],\n        [\n          65628,\n          65692\n        ]\n      ],\n      "contract": "SuppliedimmutabledefinitionIDallocatesatparentLONGXY/facing,marker/context0;advancecursor8regardlesssuccess;successfulheadcopiesparent121/58/122/62afterallocation;failurepreservesallocatorpartialstate."\n    },\n    {\n      "address": 65164,\n      "ranges": [\n        [\n          65164,\n          65168\n        ],\n        [\n          65698,\n          65822\n        ]\n      ],\n      "contract": "TwoactualRNGcalls0..WORD(2range),subtractrangeandpublishC494/C498;integerparentXY+offset32/34+delta,explicitincomingupperD2/D3becomefractionsviaSWAP;allocate/advancecursor8/inheritmotiononlysuccess."\n    }\n  ],\n  "data_pins": [\n    [\n      81612,\n      "00013eee0300400038c800040000a84c0000000104c80000000008000000000000000000000001e0400036c800040000a84c00000001015a000000004800000000000000"\n    ],\n    [\n      82224,\n      "00000000006060003ac800280000b702000000011a0e000099582000000000640004"\n    ]\n  ],\n  "proof": "Fulloriginalboundaries/liveparentreadorder/ADDQ-addresspreservedallocatorZ/randomSWAPfractionsemanticsreviewed. Focused131072nativecases:all65536RNG/range/fractionseeds x2entries;independentRNGarithmetic/requestoraclecomposedwithactualverifiedallocator;originalone/tworecorddefinitions,empty/one/twofreeactors,graphicsfailureandpartialchainfailure;all48actors/freestack/cursor/globaltargets/resultidentitieschecked. Compile-onlymissingtestincludesfixedbeforefirstsuccessfulrun;no passedtestrepeated.",\n  "scope": "Localstableparentoutsidefreepool,validfiniteoriginaldefinitionchainsandexplicitincomingfraction/definition/cursorhandles. DefinitionIDalreadydecodedfromanimationdataargument;sharedFD94enginecontinuation/CPUtemporaryregister/CCRABI andremaininganimationcallercontextsnotcertified. NoROMexecutionorSDLadoption;notwholeanimationfidelity."\n}')
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
