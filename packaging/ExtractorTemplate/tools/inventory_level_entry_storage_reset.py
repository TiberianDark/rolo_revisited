"""Bounded1CEE queue reset and VRAM name-table clear services."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x2674,0x2684,'Reset word-transfer queue','A0=FFFFEB56; clear firstLONG terminator; C434=A0. No traversal, drain or allocated-buffer check. Other queue storage remains untouched.'),(0x2684,0x2694,'Reset byte-transfer queue','A0=FFFFE448; clear firstLONG terminator; C438=A0. Does not reset WORD E444, unlike260A drain. Other queue storage remains untouched.'),(0x684e,0x6864,'Clear VRAM C000 plane','D0=C000,D1=0,D2=40000080,D3=1000; tailBRA26BC nativeDMAfill prepares zero byte fill4096bytes atVRAM C000.'),(0x6864,0x687a,'Clear VRAM E000 plane','D0=E000,D1=0,D2=40000080,D3=1000; same tailfill4096bytes atVRAM E000.'))
RANGES=((0x26bc,0x2746),(0x25a8,0x2674),(0x1cee,0x1d12))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
 def decode(start,end):
  at=start;out=[]
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   out.append(i);at+=i['size']
  if at!=end:raise ValueError('Extent mismatch')
  return out
 operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Exact storage capacity/hardware timing remains caller domain; bounded literal state writes established') for s,e,n,c in SPECS]
 return dict(rom_sha256=ROM_HASH,operations=operations,helper_evidence=[i for s,e in RANGES for i in decode(s,e)],
  call_order=['63FAblockingblackfade','1CF2displaybit6clear','2674wordqueue reset','2684bytequeue reset','523Elevelstate reset','684EclearC000','6864clearE000'],
  queues=[dict(cursor='C434',base='FFFFEB56',format='LONG0termination, otherwise14bytecommand: initialLONGVDPcommand plus LONG,threeWORDregisterpublications',drain='25A8 auto-increment2; iteratecommandsuntilzero, busywaitVDPstatusbit1 aftereachcommand, thenclearfirstLONG/resetcursor.',reset_registers='2674A0=base; Dregistersunmodified; CCRresultofMOVEpointer; RTS'),dict(cursor='C438',base='FFFFE448',format='Same14bytecommandandLONGterminator',drain='260A auto-increment1, resetscursor/base andE444=0080 afterdrain.',reset_registers='2684A0=base; Dregistersunmodified; noE444write; RTS')],
  fill=dict(helper='26BC swapsD0/D1 andD2/D3; duplicateBYTEzerointoWORDD0; subtract1fromWORDcountD2 (1000→0FFF), then26C8DMAfill.',publications=['SetshadowC432bit4andwriteVDPreg1','VDPautoincrement1 via8F01','Lengthregisters9300|FF and9400|0F','DMAfillmode9780','BuilddestinationcommandusingD1integeraddressandD3=40000080; writeviaC462/C464','WritezeroWORDD0toVDPdata','Pollcontrolstatusbit1untilclear','ClearshadowC432bit4andwriteVDPreg1'],destinations=['C000..CFFF','E000..EFFF'],registers='ReturnsD0LONG0,D1LONGdestination,D2WORD0FFFwithincomingD3upperWORDretained,D3LONG40000080,D4upperWORDfrombuiltcommandandlowWORD0 afterbusyAND; A6mustalreadybeC00000. NoAregisterchangesinhelper. CCRlastMOVEshadowpublication, noterrorindicator.',state='C462LONGholdsbuiltVDPcommand; C432bit4isclearedunconditionally ratherthanrestoredtoincomingstate.',failures='Noerrorbranch/capacitycheck. Busywait272A..2732neverreturnsifVDPbusybitneverclears. Countzeroexceptionnotreachedbyliteral1000callers.'),
  remaining=['Queue allocation capacities andproduceroverflowchecks cannotbeinferredfromreset/drainonly.','DMAfill exactVDPhardwarecount/seed-writecompletionsemantics neednative hardwarecontract ratherthansyntheticinstructionexecution.','Callerinterrupt/softwaregatepublicationinterleavings andspecial incomingDMAenabledstate remainintegrationdomains.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/level-entry-storage-reset-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified four1CEE queue/plane resetservices andDMAfillhelper')

