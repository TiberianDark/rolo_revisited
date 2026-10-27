"""Bounded sprite origin and reserved-count writer evidence; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x330a,0x3366,'Compute sprite hardware origin','X=actor12 plusactor32 negatedwhen118bit3, minus arithmetic-halfwidth36, minusF362unless126bit4, plus128. Y=actor16 plusactor34 negatedwhen119bit4, minusheight38, minusF366unless126bit4, plus128. AllWORDarithmeticwraps. OutputD2width,D3height.'),(0x31dc,0x3208,'Initialize reserved sprite count','LoadF266WORD; publishlowBYTEtoC492; multiplyWORDcount4toC476; addtwiceit toA3=C9BC (8bytesperrecord); zero8bytesnextslot. Noreservedcountboundscheck.'),(0x5060,0x507c,'Reserve five HUD sprites','UseexistingF266WORDoffsettoC9BC; add5toF266; subsequenttemplatecopiesappendfiveSATrecords. No80recordtesthere.'),(0x5348,0x5382,'Reserve trunk-effect sprite count','SkipifC519+C51A+C51B BYTEsum nonzero orbaseactor52BYTEzero. OtherwisezeroextendC51C intoD0 andaddWORDtoF266; appendtrunkrecords later. CanonicalC51Czero..3comesfromreset76D2andguardedincrement980E.'))
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
 refs=[]
 for at in sorted(accepted):
  i=Decoder(rom,at).decode()
  if any(s in i['operands'] for s in('F266','C492','C51C')):refs.append(i)
 return dict(rom_sha256=ROM_HASH,operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Canonicalcallerreservedcount andhardwarepublicationdomains remainexplicit') for s,e,n,c in SPECS],accepted_field_references=refs,
  helper_evidence=decode(0x980e,0x9826)+decode(0x76d2,0x76d8)+decode(0x3448,0x3450),
  origin=dict(fixed_screen='actor126bit4 suppressesbothcameraWORDsubtractions; hardwarebias128stillapplies.',flips='Horizontaloriginnegationreads118bit3; laterchunkflipreads119bit3. Verticalorigin/chunkflip bothuse119bit4. Do notcollapse118and119.',culling='3366chunkpath uses signedBLT/BGT checksD0X96..448,D1Y96..352 inclusive, correspondinghardwarebias128 toscreen margins-32..320/-32..224. Notunsignedbounds.',dimensions='widthWORD36 arithmetic-half signed; heightWORD38subtractliteral. Noncanonicalgeometry remainsdata/callerdomain.'),
  counts=dict(reserved_initialization='F266WORD mayarbitrarilyexceed80;31D6doesnotclamp. C492getsBYTE truncation whileA3/C476usewrappedWORDmultiplication.',canonical_level='Followingprevious3448clear andsingle5060HUDreservationplus5348trunkcount0..3, reserved5..8. Thisleaves72..75actorSATrecords beforeincrementto81guard.',tail='3448clearF266 occursontheendofeach3440group;C492/C476retaincurrentframecounts.',world='A436appendscompleted-nodeSATrecordsafteractorbuilderandupdatesC492viaA4C6; no80guarddemonstratedthere.',all_accepted_absolute_writers='F266:5060+5,5348+C51C,3448clear. C492:31E2initialize andA4C6completedmarkers;chunkincrementsarethroughA1alias3378.'),
  remaining=['InitialbulkRAMclear/firstframe reserved invariant andmultipleHUDcall contexts needcallerproof.','C51Cguardrejectsonlyequal3; arbitraryretainedvaluesabove3 arenotclamped.','A436completedmarker capacity andfullSATqueueownership remainsseparate.','Reachedorigin doesnotproveall165graph orallactorpresentationframes.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/sprite-origin-reserved-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified spriteorigin andallacceptedabsolute reserved-count references')
