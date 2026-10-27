"""Accepted-boundary progress flag references and bounded context, static only."""
import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());owners={}
for routine in inv['routines']:
 for a in routine['blocks']:owners.setdefault(a,[]).append(routine['hex'])
contexts=[]
for address in sorted(owners):
 instruction=Decoder(rom,address).decode()
 if not any((v&0xffffff)==0xffc558 for v in instruction.get('references',[])):continue
 at=address;window=[]
 for _ in range(20):
  if at not in owners:break
  i=Decoder(rom,at).decode();window.append(i);at+=i['size']
  if i['flow'] in ('return','call','indirect_call','indirect_jump','jump'):break
 contexts.append(dict(address=address,hex=f'{address:06X}',routine_candidates=owners[address],anchor=instruction,bounded_context=window,status='explicit C558 address reference; indexed access identity/alias closure requires review'))
known=[dict(entry='523E',role='startup samples bit1 intoC552, samples oldbit2 intoC553 then setsbit2',ordering='before3E8Acensus; retained campaign state'),dict(entry='3E8A',role='zero companion census sets current bit1',ordering='does not update previously sampled C552'),dict(entry='D32A',role='last rescued companion setscurrentbit1/3 and spawnselectorbit0',ordering='sound thenlinked score/request services; failures do not rollback flags'),dict(entry='9A1A',role='piece collection setscurrentbit3 and rewardselectorbit0',ordering='sound64 before progresswrite; BYTEselector preserves previous highWORDbyte'),dict(entry='6236',role='read-only campaign percentage counts bit1 for70 immutable nodes',ordering='completionpercentage distinct from jigsaw reveal bit0')]
report=dict(rom_sha256=ROM_HASH,inventory_sha256=hashlib.sha256((p/'docs/stage9/inventory.json').read_bytes()).hexdigest(),scope='Explicit accepted-boundary references, not exhaustive indirect/overlapping writer proof',contexts=contexts,reviewed_roles=known,gaps=['Cached address registers can access C558 without another explicit reference.','Bulk clears/copies and neighboring indexed writes may alias campaign flags.','All signedWORDselector producers and highBYTE preservation domains need closure.','Menu/reset/ending caller paths and CPU ABI remain outside local certificates.'])
(p/'docs/stage9/progress-flag-ownership.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
lines=['# Campaign progress flag ownership','',f'{len(contexts)} explicit references found at accepted instruction boundaries. Context windows stop at calls or exits; this is not an exhaustive writer certificate.','', '| Routine | Reviewed role |','|---|---|']
lines += [f"| {r['entry']} | {r['role']} |" for r in known]
lines += ['', 'Required closure: cached pointer aliases, bulk clear/copy overlaps, selector domains and original startup/reset ordering. See progress-flag-ownership.json for original instruction windows.']
(p/'docs/stage9/PROGRESS-FLAG-OWNERSHIP.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'{len(contexts)} explicit C558 references catalogued with accepted original boundaries')
