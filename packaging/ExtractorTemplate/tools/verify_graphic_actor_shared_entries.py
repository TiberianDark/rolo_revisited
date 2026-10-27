"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "graphic_actor_shared_entries",\n  "title": "glyph palette and actor arithmetic contracts",\n  "sources": [\n    "src/core/graphic_actor_shared_entries.hpp",\n    "tests/graphic_actor_shared_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 1442304\n  },\n  "cases": 1442304,\n  "specs": [\n    {\n      "address": 27540,\n      "ranges": [\n        [\n          27540,\n          27644\n        ]\n      ],\n      "contract": "GlyphnibbleRMW: signedWORDblock/rowaddressincrements, bit2+2, shift4*(~X&3), rotatedFFF0mask,8F00/readcommand/readWORD/writecommand/ORdata; unmaskedfullWORDink retained."\n    },\n    {\n      "address": 27644,\n      "ranges": [\n        [\n          27644,\n          27734\n        ]\n      ],\n      "contract": "32sourceBYTEs highthenlownibbles replicated1111,64fillrequestsfromdestination64step32/count31/control40000000;final7777fillat32."\n    },\n    {\n      "address": 26366,\n      "ranges": [\n        [\n          26366,\n          26448\n        ]\n      ],\n      "contract": "Compose4actualnative16colour/rate0paletteeffectinitializations;firstincomingjobthen3bankjobs,typedfourbankordering."\n    },\n    {\n      "address": 36724,\n      "ranges": [\n        [\n          36724,\n          36772\n        ]\n      ],\n      "contract": "SignedWORDhalfwidth floor, wrappedleft/right andtop/bottomcomparisons; returnsFFFFFFFFwhenoutsideelse0withoutactormutation."\n    },\n    {\n      "address": 52708,\n      "ranges": [\n        [\n          52708,\n          52756\n        ]\n      ],\n      "contract": "DirectionBYTEsignselectsLONGforceaddition/subtraction, negativeresultnegatesmagnitude/directionBYTE, signedclampF0000;80000000selfnegationpreserved."\n    }\n  ],\n  "proof": "ReviewedoriginalWORDsignedEA/ROLmask/ports, palettejobcomponents andLONGNbranches. Onefocused1442304nativecases:65536glyphX/Y/ink/oldWORDpatterns withindependentcommand/nibblemaskoracle;65536width/rectanglepatterns/fullactorpreservation;1310720direction/force/speedboundarycasesincluding80000000;256expandedglyphpatterns65fills and256fourbankpalettematrices comparedperchannel. Actualverifiedfill_display_bytes/palette_effecthelperscomposed.",\n  "scope": "Localtypedpixelport/RAMeffectstate andactorarithmetics. Palettejobstorage/targetbankhandles representedbyfourindependenttypedobjects; originalA4cursor/CPUvolatileoutputsandout-of-domainaliases external. GlyphRMWread_word supplieshostpatternword, notVDPemulation; transfer/actualvideo/audiotimingexternal. RectangleallWORDdataallowedlocalmodulararithmetic,nochangelegacySDL."\n}')
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
