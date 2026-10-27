"""Bounded3C08 storage/display reset services; static ROM analysis only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

SPECS=((0x2d2a,0x2d68,'Reset display planes and scroll state','Call684E,6864,687A; publish9100/929Cwindowregisters;146CplaneVDPregisterlayout; clearWORDsF324/F326/F350/F352;6960retainedF286horizontalmode;6AA6verticalscrollpublication. DoesnotclearF286.'),(0x68ae,0x68d2,'Clear first sprite record immediately','Clear8bytesC9BC..C9C3; D0=FFFFC9BC,D1=F400,D2=40000080,D3WORD4; tail2466 exchangescount/command thenperforms4WORDDMAcopy. Notqueueappend.'),(0x6894,0x68ae,'Zero-count D000 address publication','D0WORD E000,D1LONG D000,D2WORD0,D3LONG40000000;2694 publisheswriteaddress but decrementscount0toFFFF and skipsdatawrites. DoesnotclearD000.'),(0x4020,0x4030,'Zero foreground ring','SaveD0..D7/A0/A1; A1=FFFF4000,D0=31; shared403C zeros32chunks512bytes descending:FFFF0000..FFFF3FFF; restores10LONGregisters.'),(0x4030,0x4096,'Zero background ring','SaveD0..D7/A0/A1; A1=FFFF6000,D0=15; shared403C zeros16chunks512bytes descending:FFFF4000..FFFF5FFF; restores10LONGregisters.'))
RANGES=((0x3c08,0x3c3a),(0x2694,0x26bc),(0x2466,0x250e),(0x687a,0x6894),(0x6960,0x69aa),(0x6aa6,0x6ac6))

def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
 def decode(start,end):
  out=[];at=start
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   out.append(i);at+=i['size']
  if at!=end:raise ValueError('Extent mismatch')
  return out
 operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Hardware publication and inherited selector context remain explicit') for s,e,n,c in SPECS]
 return dict(rom_sha256=ROM_HASH,operations=operations,helper_evidence=[i for s,e in RANGES for i in decode(s,e)],
  call_order=['3C08clearF2F2','2D2A','68AEimmediateSATclear','2674','2684','684E','6864','6894addressonly','4020','4030','36BA','384A'],
  storage=[dict(entry='4020',start=0xffff0000,end_exclusive=0xffff4000,bytes=16384),dict(entry='4030',start=0xffff4000,end_exclusive=0xffff6000,bytes=8192),dict(entry='68AE',start=0xffffc9bc,end_exclusive=0xffffc9c4,bytes=8)],
  selector=dict(source='F286BYTE retained',callee='6960',calculation='MOVEQ0D0;loadBYTE;publish8B00|mode;multiplyWORDmode4;indexedJMP697C',slots=[dict(selector=s,slot=0x6980+4*s,target=t) for s,t in enumerate((0x6990,0x69a8,0x69aa,0x6a0a))],limitation='2D2A does not establish0..3domain. Mode1returns without scrolltable writes; mode0 publishesF324/F350WORDpair. Mode2/3delegated scroll contracts.'),
  registers=dict(ring='RestoreD0..D7,A0,A1;A2..A6untouched;CCR notrestored;40stackbytes required.',address_only='D1LONGD000,D2WORD0,D3LONG40000000;D0WORD E000retainsupper;D4lowWORDFFFFwithconstructedcommandupper retained.',sprite='A0=C9C0;D5preserved;D0source,D1destination,D2WORD4withincomingD3upperretained,D3LONG40000080;D4uppercommand/lowbusy0.',scroll='2D2A returnsD0WORD0fromF326,D1WORD0fromF352after6AA6; upperWORDs depend6960mode. Noall-registerpreservation.'),
  failure_paths=['2468 busywait withouttimeout canblock68AE.','Fixedringfills have nofailurebranch/capacitycheck.','6894 zero-count case explicitly skipsdatawrites; do notinventmemoryclear.','RetainedF286outside0..3 dispatches beyondfourcanonicalslots;2D2Aalone cannot prove domain.'],
  remaining=['Hardware publication and queue/drain interrupt timing.','InheritedF286writer/callerproof andmode2/3scrollsubstrate.','Stack and storage ownership acrossscenecontexts.'])

if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/loader-storage-display-reset-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified five loader storage/display reset contracts')
