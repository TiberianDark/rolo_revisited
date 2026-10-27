"""Pin local injury branches and valid original phase tables; no ROM execution."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
result=root/'work/actor-injury-dispatch-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,state_cases=1572864,rejected_inputs=262375)
sources=['src/core/actor_injury_dispatch.hpp','src/core/actor_state.hpp','tests/actor_injury_dispatch_verification_tests.cpp'];exe=root/'work/actor_injury_dispatch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
tables={0xea84:[0xea98,0xeb1a,0xeb4a,0xeb9e,0xebc8],0xed66:[0xed72,0xed90,0xee18],0xf054:[0xf060,0xf0e2,0xf12c],0xf1a2:[0xf1ae,0xf25e,0xf2a0],0xba72:[0xbdfc,0xbdd2,0xbd88,0xbd60,0xbd4e,0xbd2c,0xbd0a,0xbcd0,0xbc32,0xbdd2,0xbb8e]}
for base,targets in tables.items():
 for n,t in enumerate(targets):
  i=Decoder(rom,base+n*4).decode();assert i['mnemonic']=='BRA' and i['target']==t
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xecc4,[(0xecc4,0xed18)],'Initial selector20 returns. Gate/contact/negative-result checks; live selector20 after damage invokes D3FE then scene14E78 at A00000/1230000 with context/facing/marker zero. Other negative damage clears F2BA and sets F2B8=10.'),(0xed18,[(0xed18,0xed66),(0xecf8,0xed18)],'Initial selector20 returns. Same damage/reward branch. Otherwise live117 gate; select aligned46offset0/4/8, phase service then gravity, integrate, land on live A5. Reward path bypasses motion.'),(0xea4c,[(0xea2c,0xea84)],'Gate/contact/negative damage; live selector8 invokes reveal plus scene14E78 at1140000/1510000. Other negative damage resets timer/gate. Nonreward clears118bit3 then dispatches live46 aligned0..16, even when117 nonzero.'),(0xf046,[(0xf046,0xf054)],'Clear118bit3 then dispatch live WORD46 aligned0/4/8 to original replacement phase targets.'),(0xf194,[(0xf194,0xf1a2)],'Clear118bit3 then dispatch live WORD46 aligned0/4/8 to original facing phase targets.'),(0xba64,[(0xba64,0xba72)],'Zeroextend BYTE50, multiply by4, dispatch original11slots. No actor writes before service; duplicated BDD2 slots preserved.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),original_bytes=rom[start:max(b for a,b in ranges)].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local injury and phase-dispatch contract',native_sources=[sources[0]],checked_cases=262144,contract=contract,proof='One focused family run: 1572864 state fixtures, full three-actor records and mutable service-entry snapshots, live identity switches, preserved fractions, gate/timer states and service ordering. Independent raw-byte branch oracle; original BRA tables pinned. Every phase WORD and every BYTE50 outside admitted tables checked for explicit rejection, 262375 rejected input cases.',scope='Local valid aligned phase domains and BYTE50 0..10 only. Caller selector production/reachability is not proven by rejection tests. Contact9012/damage96C6/revealD3FE/sceneallocator28B0/phase targets and motion services are explicit boundaries, including mutable live A5. Returned contact Z and damage N are typed bool results, not a complete CPU flag model. Original target bodies, data ancestry and SDL integration remain separate; no full enemy fidelity claim.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,dispatch_tables={f'{a:06X}':t for a,t in tables.items()},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/'docs/stage9/actor-injury-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Six local injury/phase contracts verified.')
