"""Bounded original level rebuild services; static instruction evidence only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=(
 (0x3900,0x3934,'Fixed plane name-table publication','Write8F02 increment and50000003 command. For28rows, read40WORDs from54B22, addE5DD with WORD wrap and publish; then write24copies of incomingD4 WORD. Source length2240bytes, destination1792WORDs. D4 is a caller input, not implicitly zero.', 'A6VDP identity, incomingD4 provenance, source interpretation and renderer publication remain pending.'),
 (0x3bf6,0x3c08,'Clear level lookup scratch','A0=7410,D0=0,D1=19; DBF loop writes20WORDs zero through7438exclusive. Returns A0=7438,D1lowWORDFFFF,D0=0; upperD1zero fromMOVEQ. Flags from finalMOVE.W zero; DBF does not change flags.', 'All scratch aliases and ordered native startup binding remain pending.'),
 (0x608a,0x60a6,'Conditional foreground class5 marker scan','IfBYTEF26Ezero return withoutclearing it. Otherwise clearF26E, D0=5,A4=60A6 then3E2C scans foreground markers. Callback beginsBCLRbit0ofvariantD0, comparesBYTE14; variants14/15continue60B4, other variants returnD0zero. Not a generic player reset.', 'Local60B4/scanner/camera behavior is pinned in entry-marker-callback-contract.json. F26E producer domain, incoming register provenance, actor lifetime/allocation and original-reference behavior remain pending.'),
 (0x5d08,0x5dac,'Level sound and presentation selector','ClearWORDF2C6. Read pair at4AE3A+signedWORD(2*F2F6). FirstBYTEFF or equalF2C0 skips soundchange; otherwise storeF2C0, zeroD1/call78808 with songD0. Reload song, WORDsubtract1B/double, readWORD5DAC+signedindex. IfF2BEnonzero MULU6 thenDIVU5; storelowWORDF2C6. SecondBYTEFF advances(F2C2+1)&0F then reads16BYTE5DB8 table. Ifprior-entryC553nonzero andF26FFF, variants08/0E become09. PublishBYTEF2C1. No audio implementation is claimed.', 'All selector bounds, duration table indices, 78808 clobbers/audio request contract, field consumers and fidelity remain pending. F2BE is original overseas flag, not PAL flag.'),
)
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
 operations=[]
 for start,end,name,contract,pending in SPECS:
  at=start;instructions=[]
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   instructions.append(i);at+=i['size']
  if at!=end:raise ValueError('Code extent mismatch')
  operations.append(dict(entry=f'{start:04X}',end_exclusive=f'{end:04X}',name=name,contract=contract,pending=pending,instruction_evidence=instructions,code_sha256=hashlib.sha256(rom[start:end]).hexdigest()))
 return dict(rom_sha256=ROM_HASH,scope='Bounded original rebuild services; no ROM execution or full caller/native fidelity claim',operations=operations,
  immutable_data=[dict(start='54B22',bytes=2240,sha256=hashlib.sha256(rom[0x54b22:0x54b22+2240]).hexdigest(),scope='Fixed40x28 source words; incomingD4 supplies rowpadding'),dict(start='5DAC',bytes=12,hex=rom[0x5dac:0x5db8].hex(),scope='Six observed literal duration words; global reachable index domain pending'),dict(start='5DB8',bytes=16,hex=rom[0x5db8:0x5dc8].hex(),scope='ExplicitAND0F constrains cyclic presentation selector')])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/level-entry-services-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified4 bounded level-entry services')
