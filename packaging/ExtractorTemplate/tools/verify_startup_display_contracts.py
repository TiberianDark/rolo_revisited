"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "startup_display_contracts",\n  "title": "startup and display configuration state",\n  "sources": [\n    "src/core/startup_display_contracts.hpp",\n    "tests/startup_display_contracts_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 65793\n  },\n  "cases": 65793,\n  "specs": [\n    {\n      "address": 5140,\n      "ranges": [\n        [\n          5140,\n          5162\n        ]\n      ],\n      "contract": "Captureopaquecontinuationbefore clearingexact65536workRAMbytes, returncapturedhandle; guardbytesretained, nativecallerownstransfer."\n    },\n    {\n      "address": 5218,\n      "ranges": [\n        [\n          5218,\n          5228\n        ]\n      ],\n      "contract": "Assign displaycachedWORD8104."\n    },\n    {\n      "address": 5228,\n      "ranges": [\n        [\n          5228,\n          5278\n        ]\n      ],\n      "contract": "EightorderedcontrolWORDpublications8230/8407/8334/857A/8D3C/8B00/8C81/9001."\n    },\n    {\n      "address": 5974,\n      "ranges": [\n        [\n          5974,\n          6034\n        ]\n      ],\n      "contract": "Setframehook171C,planeC000,activetextresumeLONGor13CB2ifzero,attributes4000, cleardelay/modeBYTEs;resumeunchanged."\n    },\n    {\n      "address": 9916,\n      "ranges": [\n        [\n          9916,\n          9928\n        ]\n      ],\n      "contract": "Preparefallthroughfillrequest:swap0/1and2/3; replicateoldD1lowBYTEintoD0lowWORDretainingupper; copyBYTEtoD4low; decrementnewD2lowWORDretainingupper."\n    },\n    {\n      "address": 11624,\n      "ranges": [\n        [\n          11624,\n          11642\n        ]\n      ],\n      "contract": "Exactfillserviceargumentsvalue0,destination0,countWORD31,command40000000."\n    },\n    {\n      "address": 14374,\n      "ranges": [\n        [\n          14374,\n          14380\n        ]\n      ],\n      "contract": "Typeddecodedsource/destinationrestorationfromsavedA2/A3equivalent fullLONGhandles."\n    },\n    {\n      "address": 22174,\n      "ranges": [\n        [\n          22174,\n          22192\n        ]\n      ],\n      "contract": "VersioninputBYTEbit7setsregionflagFFelsereturn0, otherbitsignored."\n    }\n  ],\n  "proof": "Originalinstructionboundaries/registerwidths reviewed. Onefocused native65793cases:allWORDcachedisplay/titlecursor/filllowWORDpatterns andvariedhighhalves, eightpacketorder,256versionflagsand64KiBRAMfillswith4guardbytes,exactfillrequest. CPUinstructionsneverexecuted;handlesdataonly.",\n  "scope": "Local native state/orderedtypedpublication contracts. ClearRAM usesexplicit64KiBspan andopaquecontinuation, notCPUstack/JMPorROMexecutor. Startupdeviceinitialization remains hostservices, noactualVDPregions orCPUregisterbankclaim.26BCcertifiesrequestprefixbefore26C8tail, targetbodyseparate;2D68certifiesarguments,38cursorreturntyped. Notfullstartupfidelity orSDLbinding."\n}')
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
