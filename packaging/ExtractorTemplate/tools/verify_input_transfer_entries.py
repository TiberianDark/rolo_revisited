"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "input_transfer_entries",\n  "title": "local input sampling and immediate transfer contracts",\n  "sources": [\n    "src/core/input_transfer_entries.hpp",\n    "tests/input_transfer_entries_verification_tests.cpp"\n  ],\n  "dependencies": [\n    "docs/stage9/input-phase-verification.json",\n    "docs/stage9/display-port-publication-verification.json"\n  ],\n  "results": {\n    "passed": true,\n    "input_cases": 1048576,\n    "dma_cases": 524288\n  },\n  "cases": 1048576,\n  "specs": [\n    {\n      "address": 8980,\n      "ranges": [\n        [\n          8980,\n          9294\n        ],\n        [\n          8978,\n          8980\n        ]\n      ],\n      "contract": "Requestbus,THdirection40/low0;244Epulse;readlowmask30shift2;THhigh40,pulse,readhighmask3F;releasebus. ComplementassembledBYTEtoC488. LiveC461nonzeroreturnspreservingmapping;else237Cnativefresh/heldmappingwithorderedaliaseddestinations."\n    },\n    {\n      "address": 9294,\n      "ranges": [\n        [\n          9294,\n          9318\n        ]\n      ],\n      "contract": "Releasebus;originalDBF10has11iterations,typedbarrier11;requestbusagain. No invented CPU instruction execution or timing claim."\n    },\n    {\n      "address": 9320,\n      "ranges": [\n        [\n          9320,\n          9488\n        ]\n      ],\n      "cases": 524288,\n      "contract": "LiveC432OR10,8F02,length9300/9400,sourceshift95/96/97writes;destinationlowWORDconstructscommandlatchC462 withD3OR. Publishhigh/low;pollstatusbit1untilclear;clearC432bit4afterpollusinglivevalue. WORDcountzeroandoddsourcepreservedoriginalmasksemantics."\n    }\n  ],\n  "proof": "One focused group:1048576inputfixtures overall65536rawlow/highpairs,eightprevious/mappingpartitions,two livegateconditions;independentmaskedbyteandmappingoracle,exact13requestevents.524288transferfixtures over65536source/count/destinationpatterns,eightcommand/busystatuspartitions;independentpacketarithmeticandmutablecontrol-stateoracle checksallwrites/pollcount/finalstate. Existinginputmap anddisplaywaitsourcepinsretained.",\n  "scope": "Local rawdevicebytes,stableinputmappingdestinations0..7,nonoverlappingnativebuffers,andDMAeventuallyclearstatusdomain. NativeWindowsinputadapter,busbarrier/devicecompletiontiming/actualVRAMcopy remainexplicitplatformservices. C461 islivegate,notanassumedreplayimplementation."\n}')
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
