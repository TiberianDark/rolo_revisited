"""Transport fade-in, caller and companion position contracts; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_maps import long
SPECS=((0x66de,0x6750,'Initialize nonblocking palette fade-in','Select4palettepointerLONGs from4B08A+(F2F6WORD<<4 signedaddressdelta); initializefour16colorbanks with2FF6 interval0,currentbank source/currentdestination aliases. Return immediately withoutwaiting orwritingC48D.'),(0x1c6c,0x1cee,'Ordinary level frame trigger caller','925C directcall1CB4 occurs afteractorcallbacks,input/motion/presentation andbeforecamera/animation/spritepublication. Noexplicitconditionalaction/pause/typegate at925Ccall.'),(0xac34,0xaca4,'Reposition companion slots after Rolo warp','Visit3slots6402..640A. AC7A comparescallback42 against2LONGsACA4(A9B0,AA4A). Matches copycontrolledC4E0integerXY tocompanion; others receivehistoryXY at(cursor6000-actorWORD50-16)&1023 from6002. No callback/controlselection/fraction/velocity fields changed.'))
RANGES=((0x925c,0x92f2),(0x937a,0x93fe))
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
 callers=[Decoder(rom,a).decode() for a in sorted(accepted) if Decoder(rom,a).decode().get('target')==0x925c]
 operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Callerstate and sharedhardware/interrupt domains remainexplicit') for s,e,n,c in SPECS]
 sources=[long(rom,0x4b09a+n*4) for n in range(4)]
 return dict(rom_sha256=ROM_HASH,operations=operations,helper_evidence=[i for s,e in RANGES for i in decode(s,e)],direct_925c_callers=callers,
  palette=dict(level1_selector=1,pointer_table=0x4b09a,sources=sources,bank_palettes=[dict(source=p,bytes=rom[p:p+32].hex()) for p in sources],colors_each=16,rate=0,clock='112phase decrement15 =>8eligible3060VBlankupdates;66DE itself doesnotwait. SoftwareC48D maydelayfirsttick.',alias='EachA3=currentbankdestination A1, sofade evolvesinplace fromcurrentpalette towardimmutabletargetA2.'),
  preservation=dict(dispatch='926C savesD0,D6,D7,A0..A4 aroundtriggerhandler; restoresafter937A. OtherDregisters andA5/A6 are notsavedbythisframe.',warp='937A savesdestinationD6/D7WORD only across63FA. Actorpositions receiveD6/D7WORD andfractionWORDS clear. SpeedsLONG58/62 anddirectionBYTE121/122clear.',companion='AC34 preservesouterD0,D7,A0,A4 acrossAC7A only, notwholefunction. AC7A changesA0/D0/D1 andwritescompanionintegerXY for2callbackmatches.'),
  controlled_type='937A performsdestinationlookup/fade/movement forcontrolledC4E0 regardlessC4E8type. Final C4E8WORD==4 controlsAC34 callonly; companioncontrolledwarpdoesnotrunRolo companionrepositionservice.',
  companion_callback_table=dict(start=0xaca4,end_exclusive=0xacac,words=[long(rom,0xaca4),long(rom,0xaca8)],bytes=rom[0xaca4:0xacac].hex(),scope='Literalpointertable excludedfrominstructions'),
  remaining=['Fullinvariantthat1C6Cisnotcalledinmenu/pause states needsmainstate dispatchancestry; noinventedactiongate at925C.', 'SelectorWORD signedshift/wrapoutsidevalidpalettepointerdomain remainscallerproof.','Companionhistorycursor/data aftercamerareset mustpreserveoriginal4CB8 context.','Native resumableblackfade mustresume937A, thennonblockingfadein andremainingframe inoriginalorder.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/transport-fade-companion-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified transport fade-in, original caller and companion positioning')
