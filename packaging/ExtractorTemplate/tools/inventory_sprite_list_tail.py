"""Bounded3440 sprite-list tail and reached transfer/capacity paths."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x3440,0x3450,'Read next sprite actor word','MOVEQminus1D0 thenWORD(A5)+ reconstructsFFFF actorpointer. Nonzero tailbranches328C; zero clearsWORDF266 andreturns. Entrywrapperis5instructions, nottheentire165instructionreachablegraph.'),(0x3470,0x3478,'Abort full sprite table','ReachedwhenincrementedBYTEC492equals81. Discard8stackbytes, backA3up3partialSATbytes, tailbranch324Efinalpublication. Stackcontextmustbetheoriginalnestedbuilder.'),(0x324e,0x328c,'Finalize sprite transfer queue','ClearlastSATlinkBYTE(A3-5). C476WORDlengthzero substitutes4WORDs, otherwiseusedliterally. Append14byteDMAregister/commandrecordtoA4,writezeroLONGterminator,andpublishA4toC434. Noqueuecapacitytest.'),(0x328c,0x330a,'Per-actor graphics transfer gate','Skipactor125bit1ornullgraphics28backto3440. Ifgraphics28equalsresident8, skipuploadbutcontinuerender. Changedgraphicssetsresident8beforeappending14byteDMArecordtoA4andzeroLONGterminator.'),(0x3366,0x3440,'Reached sprite chunk publication','Subdivideartinto32pixelchunks, originalHVflips andsignedcullboundsX96..448/Y96..352. EachvisiblechunkwritesY,size, incrementsBYTEC492;equal81branches3470beforecompletingslot. OtherwisewriteSATlink/attr/Xandadd4WORDstoC476.'))
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
 operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Callerregister/stack/queueextent andhardwareDMApublication remainexplicit') for s,e,n,c in SPECS]
 routine=next(r for r in inv['routines'] if r['address']==0x3440)
 return dict(rom_sha256=ROM_HASH,operations=operations,entry_instructions=5,inventory_graph_blocks=len(routine['blocks']),
  literal_data=dict(start=0x3450,end_exclusive=0x3470,words=list(struct.unpack_from('>16H',rom,0x3450)),bytes=rom[0x3450:0x3470].hex(),use='342A indexedtileadvance table; literal16WORDs excludedfrominstructiondecode'),
  registers=dict(entry='A5postincrements2;D0highWORDFFFFlowWORDnext. Otherregistersnotmodifiedby5instructionterminalpath; CCRafterCLR.WF266 onterminalreturn.',nonterminal='A2becomesactorpointerat328C; downstreamD0..D7/A0..A4clobbersandoriginalstackcontextapply. Noentry-wrappersave.',overflow='3470isnotstandalonecallablewrapper; stackdiscard8bytesrequiresbuildercontext.'),
  queue=dict(cursor='A4providedbycaller; finalC434publication324E',record_bytes=14,terminator_bytes=4,graphics='DMAWORDcountactor40>>1,sourceactor28>>1,destinationactor2<<5. Residentactor8updatedbeforepublication.',sat='Finalsourcecommands95DE/96E4/977F reconstructsourceC9BC;destination74000083meansVRAMF400. C476tracks4WORDspercompleteSATrecord.',capacity='SAT80completeentriesguardedbyincrementto81. NoqueueA4upperboundtest intheseboundedpaths; allocationextentmustcomefromqueueownership/caller.',zero_case='EvenzeroC476 publishes4WORDs toclearfirstSATentry.'),
  failure_paths=['Nullactorwordterminatesnormally.','Nullgraphics oractor125bit1skipwithoutgraphicsupload.','At81stvisiblechunk overflowtailbacksup3bytesandfinalizescompletepriorrecords.','DMAqueuecapacitynotcheckedhere; noerrorreturnclaim.','NoncanonicalinitialBYTEC492/stackcontext outsideguarddomain remainscallerproof.'],
  remaining=['330A..3366position originandouterbuildercaller handledseparately; notclaimed completeby3440entry.', '14bytequeue hardwaredrain timing andsourceallocationownership.', 'All reachable165graph aliases outsideboundedranges remainseparateassessments.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/sprite-list-tail-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified5instruction3440entry plusboundedqueue/capacitypaths;literal3450tableexcluded')
