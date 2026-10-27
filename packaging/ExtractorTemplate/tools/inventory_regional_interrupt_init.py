"""Pinned regional reads and VDP interrupt enable/reset evidence; static only."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
RANGES=((0x200,0x28e),(0x1356,0x13b8),(0x1462,0x146c),(0x569e,0x56b0),(0x7fc02,0x7fc1c),(0x7fc8a,0x7fca0),(0x7fb70,0x7fb9a))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};evidence=[];refs=[]
 for start,end in RANGES:
  at=start
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   evidence.append(i);at+=i['size']
  if at!=end:raise ValueError(f'Extent mismatch {start:X}:{end:X} ended{at:X}')
 for at in sorted(accepted):
  i=Decoder(rom,at).decode()
  if any(s in i['operands'] for s in ('C432','A10001','F2BE','FFE2')):refs.append(i)
 registers=list(rom[0x2a8:0x2c0]);pointers=list(struct.unpack_from('>5I',rom,0x294))
 if registers[:2]!=[4,20] or pointers[-1]!=0xc00004:raise ValueError('Resetliteral mismatch')
 return dict(rom_sha256=ROM_HASH,instruction_evidence=evidence,accepted_register_region_references=refs,
  reset=dict(vector=0x200,table_start=0x28e,pointers=pointers,vdp_register_bytes=registers,table_scope='Literal reset parameters and24VDPregisterbytes; notcode',version_read='21C reads(-4351,A1) withA1=A11100 => A10001.220 masks low0Fhardwareversion forTMSSSEGAwrite, notPALtiming.',loop='238 loads24BYTEs, writesWORDcommandD5, then addsD7=0100 toadvanceVDPregisterselector. InitialD5upper80, firstdata04 =>8004; next register1 command8114.',initial_reg0='04: HBlankinterruptbit4clear',initial_reg1='14: VBlankinterruptbit5clear,displaybit6clear'),
  normal_init=dict(entry=0x1356,sequence=['1462 writes8104 toC432shadow','1364 OR0020intoC432;136C writes8124toVDPcontrol','139E writesSR2500 admittinglevel6interrupts','13A2 OR0040intoC432;13AA writes8164displayenable'],gate='VDPreg1bit5 isinterruptenable,bit6displayenable,bit4DMAenable; these are distinct state gates.',state_rebuild='World1B22/1BBA,level1CF2/1D82,and1D98/1E0E clear/setbit6only. Accepted C432referenceaudit showsDMAservicesbit4toggles; no normalstatebit5clear.1462reinitialization itselfresetsbit5before1364enables.'),
  region=dict(game_read='569E readsA10001;56A4 masks80;56A8 storesoverseasbooleanF2BE. ThisisnotPALbit6.',sound_reads=[0x7fc06,0x7fc8a],sound_field='FFE2 holdsPALbit6boolean',sound_adjustment='7FB70 checksFFE2; PALadds0033toWORDFFF4 thenallregionsadd0100; driverpublisheshigh/selectedBYTEFFF4toA000E6. This adjusts sounddriverclock, notgameVBlankcounter.',game_cadence='14AA incrementsC490 onceperVBlankentry; main713EwaitsonC48C. No50/60softwaregameupdateconversionisdemonstratedbytheseregionreads.'),
  conclusions=['Normal gameplay initialization enablesVDPlevel6interrupts andCPUacceptance beforedisplayenable.','Displayblanking duringworld/levelrebuild preservesVBlankinterruptenable, allowing gatedpalettecompletion.','Regionbit6 is readbyoriginalsounddriver; gameF2BE isoverseasbit7.','Elapsed fade seconds dependactualhardwareVBlankcadence; do notinferuniversal60Hz fromUSA/EuropeROMname.'],
  remaining=['ActualPAL/NTSCline/fieldfrequency requireshardwareconfigurationchosenbyhost; ROMdoesnotsethardwareversionbit6.','Allresetdiagnostic/exceptionwarmentrypaths andVDPstatusacknowledgmentbehavior needseparatehardwarecontracts ifbound.','NumericinterpretationofVDPbits followsGenesisregistersemantics; literalROMwritesareverifiedhere.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/regional-interrupt-init-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified resetregistertable, normalinterruptenable andregionalreads')


