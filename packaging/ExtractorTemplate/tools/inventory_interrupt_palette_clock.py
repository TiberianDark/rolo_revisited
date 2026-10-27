"""Original interrupt and fade continuation timing evidence; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
RANGES=((0x149e,0x1522),(0x1074,0x1076),(0x713e,0x7156),(0x2ff6,0x30c6),(0x22a8,0x22ce),(0x63fa,0x6484))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
 evidence=[]
 for start,end in RANGES:
  at=start
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   evidence.append(i);at+=i['size']
  if at!=end:raise ValueError('Instruction extent mismatch')
 specs=[(0x149e,0x1508,'VBlank register preservation and palette gate','Save15LONGs, TRAP0 no-op, setC48C/incrementC490, input/sound then gated four-bank palette updates and single publication; restore/RTE.'),
  (0x1074,0x1076,'TRAP0 immediate exception return','RTE without data/register writes; exception-frame restoration is a native service boundary, not CPU emulation.'),
  (0x1508,0x1522,'Main state interrupt exclusion','Wait713E, setC48DFF duringC444 callback, clearC48D after return, repeat.'),
  (0x713e,0x7156,'Main VBlank wait handshake','ClearC48C then wait for interrupt set; caller continuation must yield rather than busy-loop in the host.'),
  (0x63fa,0x6484,'Four-bank black fade continuation','Initialize four16-colour interval0 black effects; clearC48D while waiting fourth active flag; restoreC48DFF before return. Exactly8eligibleVBlanks for canonical initialization.')]
 operations=[dict(entry=f'{start:04X}',end_exclusive=f'{end:04X}',name=name,contract=contract,
  instruction_evidence=[i for i in evidence if start<=i['address']<end],
  pending='Regional hardware configuration, native scheduler/scene continuation, input/sound and DMA ordering, exceptional caller contexts and independent original-reference fidelity remain pending.') for start,end,name,contract in specs]
 return dict(rom_sha256=ROM_HASH,scope='Original eligible-interrupt timing and synchronous continuation requirements; no ROM execution',instruction_evidence=evidence,operations=operations,
  vectors=[dict(offset=0x78,stored_word=int.from_bytes(rom[0x78:0x7c],'big'),bus24_target=0x149e,meaning='level6 VBlank interrupt'),dict(offset=0x80,stored_word=int.from_bytes(rom[0x80:0x84],'big'),bus24_target=0x1074,meaning='TRAP0 immediatelyRTE')],
  interrupt=dict(prologue='149E savesD0..D7/A0..A6 (15LONGs);14A2 TRAP0 invokes1074RTE;14A4 continues.',order=['SetBYTEC48CFF','IncrementWORDC490','Input2314','Optional sound78920/788B6 gatedF2BF','IfC48D nonzero skipfade/publication','Tick3060 banksC66C/C740/C814/C8E8 in order','22A8 publishes64CRAMwords ifC48B','Restore15registers/RTE'],main_loop='1508 calls713E, which clearsC48C then waitsuntilinterruptsetsit.150C setsC48DFF; invokesC444state;151A clearsC48D;repeat.'),
  clock=dict(unit='Eligible VBlankinterrupt withC48Dzero',delay='3060 decrements BYTE9 and interprets signedresult. Nonnegative returns; negative reloadsBYTE8 and processesonephase.',normal_interval='For initializedBYTE9zero and intervalN0..127, firstphaseoccursfirsteligibleinterrupt then everyN+1eligibleinterrupts.',phase='2FF6 initializesWORD4=112.3060 subtracts15 afterpublication; phases112,97,82,67,52,37,22,7 =>8publications, thenactiveBYTE6clears.',edge_domains='BYTEdelay128..255 signed behavior is literal, notN+1; uninitialized/direct3060 contexts distinct.'),
  publication=dict(flag='Each completedphase setsC48BFF',routine='22A8 clearsC48B before2468 transfer64WORDs fromC5EC toCRAMcommandC0000000. Onepublication afterallfourbankupdates pereligibleinterrupt.',order='C48D gate coversbothfadeupdatesandpublication; partialupdatedpalette is not published throughthispathwhilegateheld.'),
  black_fade=dict(entry=0x63fa,banks=['C66C→C5EC','C740→C60C','C814→C62C','C8E8→C64C'],colors_per_bank=16,interval=0,target_source=0x32360,target_bytes=rom[0x32360:0x32380].hex(),continuation='646A selectsfourthbank;6470 clearsC48D; spinwait6476testsactiveBYTE6untilzero;647C restoresC48DFF beforeRTS. Eachbanktickhasidenticalphase/delay,sofourthbankcompletiontracksallfourcanonicalinitializations.',duration='8eligibleVBlanks fromsetup; elapsedhostseconds dependregionalVBlankclockandgating, not8ordinarySDLupdatecalls.'),
  remaining=['SDL mustmodelinterrupteligibility separatelyfrommainstateupdate andsuspend63FAcalleruntilallfourcanonicalbankscomplete, thenrestoreC48D.', 'Regionalrefresh(PAL/NTSC) andexactVDPinterruptenable/priority needhardware/initializationconfiguration evidence;theseinstructionsalone do notselect50or60Hz.', 'Input/soundhandlercost,nestedinterrupts,DMAcompletion/publicationtiming andexceptionalbyteintervaldomains remainseparatecontracts.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/interrupt-palette-clock-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified interrupt gating,8-phase fade clock and63FA continuation')

