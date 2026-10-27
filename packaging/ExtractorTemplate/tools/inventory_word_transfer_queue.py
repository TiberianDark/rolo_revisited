"""Shared C434 graphics publication queue producer/drain evidence."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x2674,0x2684,'Reset word-transfer publication queue','FirstLONGatEB56=0; C434=FFFFEB56. Onlyterminatorandcursorreset, notwholeallocation.'),(0x25a8,0x260a,'Drain word-transfer queue','SetDMAenablebit4; auto-increment2. ReadLONG0terminatoror14bytecommand: initialLONG thenLONG then3WORDcontrolpublications. Busywaitbit1eachrecord; clearDMAenable; resetEB56terminator/C434.'),(0x324e,0x328c,'Append final actor sprite table transfer','Append14bytesatA4,zeroLONGterminator,publishC434. CountC476or4WORDminimum; fixedC9BCsource→F400.'),(0x53c6,0x546e,'Append trunk-effect graphics records','Append14bytesforeachoriginalD0+1loopiteration; inputcomeszeroextendedC51Ccount0..3canonical. TerminateandpublishC434; noqueueupperbound.'),(0x5530,0x5680,'Append rescue-counter graphics records','Appendexactly6records14byteseach=84bytes; zeroLONGterminator,C434=A0. Source/destinationsderivedresidentactorandC556decimaldigits.'),(0xfaa0,0xfb72,'Append tile-animation graphics records','Atmost20descriptoriterations; dueanimationwrites10bytesregisterprefixthen4bytecommand. IfmappingWORDFFFF, FB6Crewinds10bytesandcontinueswithoutrecord. ZeroLONGterminatorandpublishC434.'),(0xa4cc,0xa50a,'Append completed-world sprite table','Appendone14byteSATtransferrecord,totalcountBYTE D7*4WORDs;zeroLONGterminator/publishC434. Noqueueupperbound.'))
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
 refs=[];calls=[]
 for at in sorted(accepted):
  i=Decoder(rom,at).decode()
  if any(s in i['operands'] for s in('C434','C436','EB56')):refs.append(i)
  if i.get('target') in(0x2674,0x25a8):calls.append(i)
 schema=json.loads((project/'docs/stage9/ram-schema.json').read_text())
 nextfields=[f['hex'] for f in schema['fields'] if 0xffeb56<f['address']<0xfff270]
 return dict(rom_sha256=ROM_HASH,operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Queueallocatedcapacity,aggregateproducerordering andhardwarecompletioncallercontexts remainexplicit') for s,e,n,c in SPECS],helper_evidence=decode(0x328c,0x330a),accepted_absolute_references=refs,all_accepted_reset_flush_callers=calls,
  layout=dict(cursor='C434LONG',low_word_alias='C436 is lowerWORDofC434cursor, notindependentqueue. NoacceptedabsoluteC436referencefound.',base=0xffffeb56,record_bytes=14,terminator_bytes=4,cursor_rule='CursorpointsatcurrentzeroLONGterminator; nextappendoverwritesit, writesnewterminatorwithoutadvancingcursorpastit.',data_format='WORD9300lengthlo,WORD9400lengthhi,WORD9500sourcelo,WORD9600sourcemid,WORD9700sourcehi, LONGVDPdestinationcommand. Drainwritesfirst2WORDsasLONG, next2WORDsasLONG, then3WORDs.'),
  graphics_actor_append='328C emits14bytesonlywhenactorgraphics28nonnull/differsresident8; updatesresident8beforeappend andleavesA4newterminator. Final31D6wrapperpublishesC434afterprocessinggroups.',
  capacity=dict(proven=None,guards='Noappendpathinthisboundedbatchcomparescursoragainstallocationend. Noresetallocatorlengthorendpointerisdemonstrated.',nearest_schema_fields=nextfields,interpretation='NextknownabsoluteRAMfieldF264doesNOTprovequeueend/capacity; interveningunindexedstorageandaliasesarepossible. Do notderivealimitfromaddressgap.',literal_path_bounds=['Rescuecounter6records84bytes','Tileanimationatmost20records280bytes','Trunkcanonical0..3records0..42bytes','FinalSAT14bytes','Perchangedactor14bytes']),
  failure_paths=['BusyVDPcanblock25A8indefinitely; noerrorcode/timeout.','Terminatorcorruptioncanoverrunqueue; noexplicitrecordcountguard.','MappingFFFFtileanimationrewinds10bytepartialrecord correctly; itisnotcapacityoverflowhandling.','Repeatedorinterleavedproducerinvocationsneedaggregatecapacityproof.'],
  remaining=['ActualEB56allocationextent/ownership cannotbeinferredfromnearestRAMaddress.','Allregisterheldaliasesandinterruptflushinterleavings requireschedulercontracts.','Aggregateperframeproducer/countbounds andfailedpublicationresident8timing remainseparate.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/word-transfer-queue-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified C43414-bytequeueproducers/reset/drain; capacityexplicitlyunproven')
