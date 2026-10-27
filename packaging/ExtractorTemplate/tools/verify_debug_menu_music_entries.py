"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "debug_menu_music_entries",\n  "title": "debug menu and level music selection contracts",\n  "sources": [\n    "src/core/debug_menu_music_entries.hpp",\n    "tests/debug_menu_music_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 1064966\n  },\n  "cases": 1064966,\n  "specs": [\n    {\n      "address": 23008,\n      "ranges": [\n        [\n          23008,\n          23042\n        ]\n      ],\n      "contract": "SetplaneC000/attributes6000, eraseoldcursor, updateinput, drawvalues(attributes4000),drawnewcursor inexactorder."\n    },\n    {\n      "address": 23042,\n      "ranges": [\n        [\n          23042,\n          23336\n        ]\n      ],\n      "contract": "Captureoldoptiontargetbeforeup/downselection;5validrows0..24step6; independentleft/rightfresh/heldrepeat25then2, bytebooleaninvertorWORD+/-1maskFF; music/effect/startfreshcommands ordered."\n    },\n    {\n      "address": 23336,\n      "ranges": [\n        [\n          23336,\n          23560\n        ]\n      ],\n      "contract": "Fivevalue-textrequests: music/effectdecimal71BA, C4C6last3digits,thenunlock/invincible/protectionstrings atoriginalpositions andattributes4000."\n    },\n    {\n      "address": 23560,\n      "ranges": [\n        [\n          23560,\n          23572\n        ],\n        [\n          23582,\n          23610\n        ]\n      ],\n      "contract": "Erasecursor5994atX8/Yoriginal5rowtable beforeinput, attributesinherited."\n    },\n    {\n      "address": 23572,\n      "ranges": [\n        [\n          23572,\n          23610\n        ]\n      ],\n      "contract": "Drawcursor5996atX8/Yoriginalselectedrow, attrsretained."\n    },\n    {\n      "address": 23816,\n      "ranges": [\n        [\n          23816,\n          23980\n        ]\n      ],\n      "contract": "ClearF2C6;original80selectormusicpairtable, FF/samepreviousskip; changedvalid27..32 musicrequest andoriginaldelay,region6/5scale; effectFFcycles16table,haspiece+rewardFFremaps8/14to9."\n    },\n    {\n      "address": 24008,\n      "ranges": [\n        [\n          24008,\n          24194\n        ]\n      ],\n      "contract": "Fouroriginalhelptextrequests atspecifiedXY/attributes;selectorFFFE,fadein,waitWORD199entry(200frames),fadeblack."\n    }\n  ],\n  "data_pins": [\n    [\n      23610,\n      "0007c5c600000009c5c80000000bc5cc0001000dc5cb0001000fc5cd0001"\n    ],\n    [\n      23980,\n      "00c800c800dc00fa015e00e60001040c0d1113040001040c0d11130d"\n    ],\n    [\n      306746,\n      "1eff1eff1eff1eff1eff1eff1eff1eff1eff1eff1eff1eff1eff1effffffff05ff08ff0e1dff1dff1dff1dff1dff1dff1dff1dffff0eff0e1dffff051dff1dff1dffff06ffff1fffffffffffff0bffffffffff08ffffffffff08ffffffffff0effffff0effff1cffff0e1fff1cff1cff1cff1cff1cff1cffff081cff1bff1bff20ff20ff20ffff0e20ff20ff20ff20ff20ffff08ffffffffffffff08ffffffff"\n    ]\n  ],\n  "proof": "OriginalBYTE/WORDcontrols andoldA5targetbeforeselectionreviewed. Onefocused1064966nativecases:5rowsx256valuesx256repeatcountersx3buttonstates;80selectorsx256previousIDsx2regionsx2piecegates;both-up/down+right+music/effect/startcomposition;7cursor/valueorderingand4helpdrawsnapshots. Actualoriginaltablespinned,decimalformatterverifiednativecomposition.",\n  "scope": "Localtypedoption/state/orderedtext/music/fade/waitservicecontracts,notactualdrawnsettingsscreen. Textserviceowns7094parseanditsfieldmutations; proofusesnonmutatingrequestobserver, completecaller/renderbindingexternal. MusicIDs27..32/FFandselector0..79actualROMtable; counter/maskBYTEdomains explicit. Debugmenuactions definedonly5originalsixBYTErows; noarbitraryRAM-addressing/CPUexecution."\n}')
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
