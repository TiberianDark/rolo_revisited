"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-common-state-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,C142=524288,C988=524288,D940=524288,EF28=524288,ED66=524288,F3FC=524288,EA06=131072,**{'5CE6':524288,'D558':256,'noop':524288})
sources=['src/core/actor_common_state.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/actor_common_state_verification_tests.cpp'];exe=root/'work/actor_common_state_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xc142,[(0xc142,0xc160)],'Wrapped52WORD+64 clamped only when signed result>128; write52, return zero-extended WORD<<8 as vertical drive. Horizontal component is constantzero.'),(0xc988,[(0xc988,0xc9ae)],'Add LONG input deltas to actorXY, clear only velocity highwords58/62. Then controlledYWORD=actorY-height+1; preserve fractions and original alias order.'),(0xd940,[(0xd940,0xd960)],'Preserve facing other bits; subtraction actorX-controlledX wrapped WORD N sets/clears bit3, not signed endpoint comparison.'),(0xef28,[(0xef28,0xef3c)],'Compare wrapped46WORD+1 to48. On change write48 and return changed=true (original Zclear); otherwise no writes and false.'),(0xed66,[(0xed66,0xed6a),(0xed72,0xed90)],'Phase-change latch, reload50WORD10 and selector0 on entry. Decrement timer every call; negative wrapped timer increments46WORD by4.'),(0xf3fc,[(0xf3fc,0xf400),(0xf410,0xf42e)],'Same phase entry/latch/countdown, reload25 instead of10; negative timer increments phase46 by4.'),(0xea06,[(0xea06,0xea20)],'Negative signed C51E only: actor selector70=4 then linked84 actor125 bit1 set. Positive/zero gate avoids link lookup and all writes.'),(0x5ce6,[(0x5ce6,0x5d08)],'Negative WORD timer disabled. Otherwise decrement; zero input expires toFFFF and invokes music BYTE command with LONG argumentFFFFFFFF.'),(0xd558,[(0xd558,0xd57e)],'Clear exactly seven state bytes C5E4..C5EA: one WORD and five BYTE clears; retain neighbouring bytes.')]
for start in [0x7968,0x796a]:specs.append((start,[(start,start+2)],'Literal RTS: no gameplay state effect.'))
for i in range(9):
 start=0xbebc+i*4;target=0xc85a+i*2;specs.append((start,[(start,start+4),(target,target+2)],'Branch slot to literal RTS: no gameplay state effect; distinct entry alias, not a gameplay feature.'))
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 noop=start in (0x7968,0x796a) or 0xbebc<=start<=0xbedc
 if noop:assert [i['mnemonic'] for i in items] in [['RTS'],['BRA','RTS']]
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,original_bytes=rom[start:max(b for a,b in ranges)].hex(),instruction_evidence=items,verification_status='verified',status='verified green: '+('literal no-op' if noop else 'local shared actor state'),native_sources=[sources[0]],checked_cases=r['noop' if noop else f'{start:04X}'],contract=contract,proof='Independent modular integer/record model across allWORD counters/positions and8 flag/alias fixtures; all130 actor bytes compared. Carry actor/controlled aliases covered. Gate checks compare all48 records with self/separate linked actor. Delayed music callback order/arguments checked; reset has guards. No-op paths mathematically contain only BRA/RTS and share an unchanged-record native test; aliases explicitly counted as entries.',scope='Complete local declared state/value contract for admitted valid actor identities and finite state spans. CPU scratch/CCR ABI replaced by typed values; phase-change returns only its Z predicate, C142 horizontal constantzero implicit in vertical-only API. New helpers available for later caller binding; no claim these alone add playable actor behaviour. Music remains a native service handoff; hardware/scheduling external.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),literal_noop_entries=11,stateful_entries=9)
(p/'docs/stage9/actor-common-state-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Nine stateful and eleven literal no-op local contracts verified.')
