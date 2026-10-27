"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "campaign_node_completion",\n  "title": "campaign node and score initialization",\n  "sources": [\n    "src/core/campaign_node_completion.hpp",\n    "tests/campaign_node_completion_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 202752\n  },\n  "cases": 202752,\n  "specs": [\n    {\n      "address": 24820,\n      "ranges": [\n        [\n          24820,\n          24870\n        ]\n      ],\n      "contract": "Markcurrentflags bits1and3, rewardbit0 through mixedselector highBYTE; scan type5 placementcallback."\n    },\n    {\n      "address": 24870,\n      "ranges": [\n        [\n          24870,\n          24932\n        ]\n      ],\n      "contract": "Same live flag mutations then type11reveal scan followed by type5placement; service mutations remain live."\n    },\n    {\n      "address": 24932,\n      "ranges": [\n        [\n          24932,\n          24948\n        ]\n      ],\n      "contract": "SignedWORD admitted flag index, setbit0 retaining allother flags; scalar0 return represented by voidcallback convention."\n    },\n    {\n      "address": 24948,\n      "ranges": [\n        [\n          24948,\n          24984\n        ]\n      ],\n      "contract": "Clearbit0of incomingcode then lowBYTEcompare10; rejectunchanged/return0, accept wraps lowWORDXminus32 preservinghighWORD and storesactorX/Y, returnsFFFFFFFF."\n    },\n    {\n      "address": 25422,\n      "ranges": [\n        [\n          25422,\n          25476\n        ]\n      ],\n      "contract": "Reset lives3,gate0,sentinelFF, two scorebackupLONGsFFFFFFFF,total0, then thresholdinitializer."\n    },\n    {\n      "address": 39366,\n      "ranges": [\n        [\n          39366,\n          39382\n        ]\n      ],\n      "contract": "Clear threshold WORDoffset, load exact originaltable firstLONG1000000; totalretained."\n    }\n  ],\n  "data_pins": [\n    [\n      39382,\n      "000f4240"\n    ]\n  ],\n  "proof": "One focused native assertion run: all80x80node/rewardindices across fourinitialflag masks andbothcompletion entries, including current/rewardaliases and live mutationbetween11/5services;65536scoreinitialstates;65536callback codes/XWORDs withfull130BYTEactorpreservation;all80indicesx256flagbytes. Original instruction branches and boundaries reviewed, thresholdtable pinned. NoROMexecution.",\n  "scope": "Local typed state contracts:80flagindices and valid controlledactor. Scan3E2C remains explicit callable service with ordered types/callback roles; complete scanproducer and original aliasdomains outside flags remain external. CPUvolatile register/CCR values not exposed except typedplacementreturn/X. RewardhighBYTEmixpreserved before indexadmission. No SDLintegration orwholecampaign fidelity claim."\n}')
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
