"""Bounded sprite frame, copied sorter and publication evidence; static only."""
import hashlib,json,collections
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=(
 (0x313e,0x3152,'Install relocated sprite queue sorter','Copy102BYTEs3152..31B8 toC3CC..C432exclusive. Source/destination advance102; D0lowWORDFFFF fromDBF. This copies code data for the original RAM service; native ports must use semantic queues, not execute copied instructions.', 'All code-copy/patch aliases and initializedcaller ancestry remain pending.'),
 (0x3152,0x31b8,'Critical six-queue sort template','SaveSR onrealstack, setSR2700, saveA7 intoUSP. A1..A6 point6D7A/6DDC/6E3E/6EA0/6F02/6F64. A7 relocates to template+64 patchword; A0=98C8,D6trackslistreadcursor,D7=C5B8actualcountN. Eachiteration swapsA7/D6 toreadactorpointer, restorespatchpointer, writes actorWORD0 intoopcode slot, then DBFback executespatchedword before nextread. SixMOVE.WA0,(An)+ forms append lowWORDactoridentity; NOPdrops it. The pipeline readsN+1pointers butexecutesonlyNactoropcodes: finalzero pointer readsROM0WORDFFFF intoC40C thenDBFexitswithout executing it. EmptyN0thereforeexecutesnoactoropcode. Then terminateallqueuesWORD0, A6=C00000,restoreA7fromUSP andoriginalSR.', 'Canonical immutable opcodes are bounded; live actorWORD0 mutation, count/list consistency and interrupt/stack/USP domains are not globally closed.'),
 (0x31b8,0x31d6,'Fixed ancillary sprite graphics transfer','D0=27040,D1=F680,D2=0480WORDcount,D3=40000000; call2468 thenRTS. Literal source spans2304bytes. Returnregisters/devicecompletion inherit2468, not an independent error result.', 'Original resource identity, caller timing and2468 device completion remain pending.'),
 (0x31d6,0x328c,'Ordered sprite frame and final table transfer','CallRAMC3CC sorter. D0WORD=F266 reserved count; C492BYTE=lowcount,C476WORD=4*count wrapped; A3=C9BC+2*signedWORD(4*count), clear8bytes there. A4=C434queuecursor. Call3440 lists6D7A,6DDC,F2D8,6E3E,6EA0,6F02,6F64 in that order. ClearBYTE(A3-5) lastlink evenzero-count case. D0=C476; zero substitutes4WORDs minimumtransfer. Append9300|lowcount,9400|highcount,95DE,96E4,977F,74000083LONG, thenLONG0terminator. C434=A4after14bytes. SourceC9BC→F400 sprite table; no queuecapacity check.', 'F266 reserved count domains, zero-count tail aliasC9B7, complete3440/chunk/overflow service paths, all queue capacity/device/reference fidelity remain pending.'),
)
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};operations=[]
 for start,end,name,contract,pending in SPECS:
  at=start;instructions=[]
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   instructions.append(i);at+=i['size']
  if at!=end:raise ValueError('Instruction extent mismatch')
  operations.append(dict(entry=f'{start:04X}',end_exclusive=f'{end:04X}',name=name,contract=contract,pending=pending,instruction_evidence=instructions))
 domain={0x32c8:1,0x34c8:2,0x36c8:3,0x38c8:4,0x3ac8:5,0x3cc8:6,0x4e71:0}
 definitions=[];counts=collections.Counter()
 for d in inv['object_definitions']:
  key=d['address'];opcode=int.from_bytes(rom[key+8:key+10],'big')
  if opcode not in domain:raise ValueError('Unproved immutable sprite sorter opcode')
  if rom[key:key+34].hex()!=d['raw']:raise ValueError('Definition bytes stale')
  counts[f'{opcode:04X}']+=1;definitions.append(dict(definition=f'{key:06X}',opcode=f'{opcode:04X}',append_queue=domain[opcode]))
 count_sites=[0x2a0c,0x2aba,0x2ac2,0x2ace]
 count_evidence=[]
 for site in count_sites:
  if site not in accepted:raise ValueError('Unaccepted sprite list producer')
  count_evidence.append(Decoder(rom,site).decode())
 return dict(rom_sha256=ROM_HASH,scope='Bounded original sprite frame services and immutable sorter-opcode proof; no native/emulator/fullfidelity completion claim',operations=operations,
  copied_template=dict(source='3152',destination='C3CC',bytes=102,sha256=hashlib.sha256(rom[0x3152:0x31b8]).hexdigest(),patch_rom_offset='3192',patch_relocated_address='C40C',patch_initial_bytes=rom[0x3192:0x3194].hex(),copy_end_exclusive='C432'),
  canonical_definition_opcodes=dict(counts=dict(sorted(counts.items())),definitions=definitions,scope='All192catalogued immutable definitionWORD8 values; actor initialization copies this flags/opcode word. Live actor mutations and exceptional caller ancestry remain separate.',globally_resolved=False),
  active_list_count=dict(producer_evidence=count_evidence,count_field='C5B8',meaning='ActualN, incremented once per survivor append, followed byLONG0 sentinel. Sort pipeline performsN+1reads/Nexecutedopcodes.',terminal_pointer_word=rom[:2].hex(),terminal_patch_executed=False),
  queue_regions=[dict(head=f'{head:04X}',bytes=98,capacity_words=49,scope='48actorlowWORDs plus terminator undercanonicalpool-count bound; allwriters still requireaudit') for head in(0x6d7a,0x6ddc,0x6e3e,0x6ea0,0x6f02,0x6f64)],
  ancillary_graphics=dict(source='27040',bytes=2304,sha256=hashlib.sha256(rom[0x27040:0x27940]).hexdigest()),
  remaining=['Do notexecute copiedRAMcode; translate seven established opcode meanings into typed lists.','CopiedC3CCidentity depends313E initialization andlivepatch aliases; no globalindirect-resolution claim.','FullSAT/chunk/clipping/overflow, graphic/queue publication andF266reserved/header domains requirejoinedcontracts.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/sprite-frame-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified4spriteframe services and192immutable sorter definitions')
