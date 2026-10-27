"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "game_over_text",\n  "title": "game-over formatting and immediate text contracts",\n  "sources": [\n    "src/core/game_over_text.hpp",\n    "tests/game_over_text_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 6825\n  },\n  "cases": 6825,\n  "specs": [\n    {\n      "address": 24984,\n      "ranges": [\n        [\n          24984,\n          25122\n        ]\n      ],\n      "contract": "Computecompletion,copyoriginalprefix,8scoreASCIIbytes;100percentcompletionflagchoosescompleteendingtext,otherwise100becomes99andappend2percentdigits/suffix;preserveuntouchedbuffer."\n    },\n    {\n      "address": 28820,\n      "ranges": [\n        [\n          28820,\n          28990\n        ]\n      ],\n      "contract": "Initializecursor;finitebyte0terminates,CRrestoressavedX/incrementsY/recomputesVRAMwordaddress;backspaceclampsnegativeXelsewritesSPACEwithoutadvancing;otherbytespublish/advancewith64column32rowwrapanddestinationreset."\n    }\n  ],\n  "data_pins": [\n    [\n      80998,\n      "01100947414d45204f564552060f0b0b010d0d53434f5245202000010e0f002520434f4d504c4554454403c80804ffff9804010d0f47414d4520434f4d504c455445442103c80804ffff9804033202010a175052455353205354"\n    ],\n    [\n      309930,\n      "0004bac6000800040004bae6000800080004bb06000400080000000009070c1d121314114d03050a1a19171e0204080b1f151c16010d0610201b2118292824253637390031302c2b0f38450027222d2a3b3a3d0034322f0e3c3349004840444e4341422600000000003f3e0000000140090a0c0db282889300280128551bc06fa3780d2c019c013c017e01820142012201120192017201f2014a016a01ea013affffd004bd00e3008b6101aac03ac021c031c02dc03ddf8406df00fea0092101d1401262036202e58406c41406d480b480f56802461bc06dc1780d01460ffffdb0f195e80ca2b003e57da9c7a7f6078c0f381ec03f607f85c605000e6017d0a006203ec07c40850195980ca27017721f37c1e006283ea240018b23f314007c595f70a007a1400f104302e4fe85003e0a000e1d2fc06914403f20fdf1858595f00900262ccff851e9f881fa17e01e603e213a5840d92481b2bc01b6b8fb1820d807373c00e8be3ea020e300bc85802f97903c8700818681058dc9f008342e0f880840f807d040e2ec75f19420012c020a70004005b4ff23e00800e0080180480300b000002a08001c00028a01"\n    ]\n  ],\n  "proof": "Fullboundaries/branchsemanticsreviewedagain. Correctedmixedstreamfixture(whichwasnewerthanpreviousblockedbinary)compiledandexecutedatthesameoriginaltestpath;noOSpolicybypass. Focused6825nativecases:0..70completednodes/maskpartitions xcompleteflag x4scores,independentfull512byteformatbufferoracle;all256textbytes x20cursorboundarypairs,controlpayloads,CR/backspace/wrapandlongmixedstream. Actualverifiedcompletionandtextpublicationhelperscomposed.",\n  "scope": "LocalfiniteoriginalROMtext/nodecatalogue,validoutputbuffersandtypednonmutatingtextports. Noactualgame-overSDLscreen/artwork/fade/audioadoption,VDPtimingorCPUtemporaryregister/CCR/ABIproof. PriorApplicationControlblocknotforcedpast;correctedtestsourcewasrecompiledlegitimatelyandpassed."\n}')
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
