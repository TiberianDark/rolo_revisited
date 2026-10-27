"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "text_numeric_sprites",\n  "title": "numeric text and glyph sprite initialization",\n  "sources": [\n    "src/core/text_numeric_sprites.hpp",\n    "tests/text_numeric_sprites_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 65792\n  },\n  "cases": 65792,\n  "specs": [\n    {\n      "address": 25476,\n      "ranges": [\n        [\n          25476,\n          25510\n        ]\n      ],\n      "contract": "Clear exactly16actor-typegateBYTEs then set3/4/5/2FF; externalbytes retained."\n    },\n    {\n      "address": 27734,\n      "ranges": [\n        [\n          27734,\n          27822\n        ]\n      ],\n      "contract": "80reverse8BYTEsprite records:8groups of8advancingtiles+blank,then8blanks; flagsOR8000,WORDtilewrap, links80..1, finalBYTE740Bclear."\n    },\n    {\n      "address": 27970,\n      "ranges": [\n        [\n          27970,\n          28024\n        ]\n      ],\n      "contract": "WORDaddressbase+2X+(Y<<7), zeroextendedmodeBYTE toverified702Ccharacterpublisher, clear mode andincrementXWORD."\n    },\n    {\n      "address": 29114,\n      "ranges": [\n        [\n          29114,\n          29174\n        ]\n      ],\n      "contract": "9originaldecimal powers100000000..1; ASCII+48lowBYTEquotients; blank atmost8leadingzeroes, ninthdigitretained, terminator0."\n    },\n    {\n      "address": 29214,\n      "ranges": [\n        [\n          29214,\n          29218\n        ],\n        [\n          29222,\n          29246\n        ]\n      ],\n      "contract": "EightleftrotatedLONGnibbles map original0123456789ABCDEFtable, terminator0; no signformatting."\n    }\n  ],\n  "data_pins": [\n    [\n      29174,\n      "05f5e10000989680000f4240000186a000002710000003e8000000640000000a0000000100000000"\n    ],\n    [\n      29246,\n      "30313233343536373839414243444546"\n    ]\n  ],\n  "proof": "Reviewed original DBF/DBCS/publication boundaries; oneoptimized nativecheck65536WORDattribute inputs comparingfull640BYTEspritepayload and4guardbytes,decimal/hexLONGpatterns includingFFFFFFFF independentlyquotient/remainder orprintf compared,65536glyphcellpacket/fieldpreservationcases and256initialgatefills. AllWORDspriteflags exercised, samples not exhaustiveallLONGdecimalinputs.",\n  "scope": "Local admittedtable/packet/statecontracts. Glyphcellusesverified702Cpublication,nonmutatingtypedports; device/CCR/retainedCPUregisters andsourcecaller integration external. Decimalalgebraic quotient/remainder matches admittedDBCSloops (firstquotient<=42,others<=9 for allLONGvalues); samplednativecomparisons do not implyfullscreenfidelity.16BYTEgateobject and640BYTEspriteextent explicit."\n}')
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
