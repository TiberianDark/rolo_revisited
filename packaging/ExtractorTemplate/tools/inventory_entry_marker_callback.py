"""Original conditional entry marker callback and camera followup; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=(
 (0x3e2c,0x3e8a,'Foreground class scan with preserved callback context','F30A+34 suppliesMAP; WORDheight6>>4 rows, offsets fromMAP+8 sign-extendedWORDs. Compare recordBYTE0 withD0BYTEclass; advance4bytes. Onmatch saveall15data/addressregisters, zeroD0 then variantBYTE1; D6WORD=X+8; D7WORD=((row*2+2)<<3)+1. JSR(A4), TST.WD0 BEFORErestoringregisters. Restore doesnotoverwriteCCR: callbackzero resumesrecordscan, nonzero returns. No callback-specific target is implied for other callers.', 'Complete MAPextent/offset/heightzero domains and allA4caller target contexts remain pending.'),
 (0x60a6,0x60f4,'Conditional class5 relocation callback','ClearvariantD0bit0, compareBYTE0x14; onlyoriginalvariants0x14/0x15(decimal20/21)take60B4. Other variantsreturnD0zero. MatchstoresD7WORDC494; C4E0actorXinteger12=D6 and clearsLONG16(Yinteger/fraction), retainingXfraction14. Preparedefinition152B8,D2lowWORD=D6thenSWAP (lowfraction is incomingD2upperWORD), D3=0,D4=0,D7=A2marker; call28B0. Successsetsnewactorcallback42=F046 andWORD54=C494. Failurestillcalls4CB8 camera initializer. BothpathsreturncameraD0; notfixedsuccess1.', 'IncomingD2upperWORD, allocation callback/definition behavior, F046 lifetime, C4E0validity and wrappedcamera return domain remain pending.'),
 (0x4cb8,0x4d54,'Immediate level camera and player window reset','C4E0XWORD-176 lowerclamp0 then signedupperF330-320 (uppermaybelowzero). YWORD-160 negativepath0 SKIPSupperclamp; nonnegativepath signedupperF332-224. PublishF362/F366WORDs only, retainfractions. Call4D54; setF320/F34CFFFF. ResolveC4E0again; window=maxSigned0(X-cameraX-60); F36A=window,F36C=window+120 WORDwrap; F2B0=134,F2B2=154. FinalD0WORD=window+120; CCRfromfinalMOVE.W154, caller3E2CTSTrecomputesD0zero.', '4D54 scrollmode dependency and allcoordinate/mapextent/registerupperWORD/caller domains remain pending; nativecamera helpers do notprove fullentryfidelity.'),
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
  if at!=end:raise ValueError('Extent mismatch')
  operations.append(dict(entry=f'{start:04X}',end_exclusive=f'{end:04X}',name=name,contract=contract,pending=pending,instruction_evidence=instructions))
 producer=Decoder(rom,0x609a).decode()
 if producer['mnemonic']!='LEA' or producer['references']!=[0x60a6] or 0x609a not in accepted:raise ValueError('Callbackproducer differs')
 return dict(rom_sha256=ROM_HASH,scope='Bounded608A initialized A4 path; no allcaller indirect closure or nativefidelity claim',operations=operations,
  indirect_context=dict(dispatch='3E7E',caller='608A',producer=producer,target='60A6',target_scope='UnmutatedA4 between609ALEA and60A0BSR3E2C; scan itself preserves/restoresA4 around callbacks',global_resolved=False))
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/entry-marker-callback-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified entry marker callback, scancontext andcamerafollowup')

