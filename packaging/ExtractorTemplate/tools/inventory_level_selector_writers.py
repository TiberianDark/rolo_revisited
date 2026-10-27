"""F2F6 writer census and conditional parallax dispatch domains; static only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};decoded={a:Decoder(rom,a).decode() for a in sorted(accepted)}
 refs=[];writes=[]
 for a,i in decoded.items():
  addresses=[int(v,16)&0xffffff for v in re.findall(r'\(\$([0-9A-F]+)\)\.L',i['operands'])]
  if any(0xfff2f4<=v<=0xfff2f7 for v in addresses):refs.append(i)
  width={'B':1,'W':2,'L':4}.get(i['mnemonic'].split('.')[-1],0)
  m=re.search(r'\(\$([0-9A-F]+)\)\.L$',i['operands'])
  if m and i['mnemonic'].split('.')[0] in('MOVE','CLR','ADD','ADDI','ADDQ','SUB','SUBI','SUBQ','ANDI','ORI','EORI','ST','SF'):
   dest=int(m.group(1),16)&0xffffff
   if dest<0xfff2f8 and dest+(width or 1)>0xfff2f6:writes.append(i)
 def range_evidence(start,end):
  out=[];at=start
  while at<end:
   if at not in decoded:raise ValueError(f'Unaccepted boundary{at:X}')
   i=decoded[at];out.append(i);at+=i['size']
  if at!=end:raise ValueError('Extent mismatch')
  return out
 modes=list(rom[0x4aeda:0x4af2a])
 rewards=[rom[0x4ab1a+s*8+4] for s in range(80)]
 sentinels=[]
 for n in range(-5,0):
  mode=rom[0x4aeda+n];retained=0xff00|mode;offset=(retained*4)&65535
  sentinels.append(dict(selector=n,table_byte=mode,retained_d2=retained,wrapped_dispatch_offset=offset,in_ten_slot_domain=offset<=36 and offset%4==0))
 contexts=[]
 for i in writes:
  addresses=[a for a in decoded if i['address']-16<=a<=i['address']+12]
  contexts.append(dict(writer=i['address'],accepted_local_context=[decoded[a] for a in addresses]))
 return dict(rom_sha256=ROM_HASH,operations=[dict(entry='4EAA',name='Conditional level selector parallax admission',contract='F2F6WORD selectsBYTE4AEDA+signedD2; MOVE.BretainsupperBYTE, thenWORDindexmultiplies4. For0..79upperBYTEzeroandall80modes0..9; negative sentinelretainsFFupperanddoesnotfitten-slotdispatch. Mainstatecallerancestrymustexcludeit.',instruction_evidence=range_evidence(0x4eaa,0x4ef4),pending='Allcallerselectorancestry andregisterheldwriter aliases remainexplicit')],references=refs,overlapping_selector_writers=writes,writer_contexts=contexts,
  census=dict(word_writers=[i['address'] for i in writes if i['mnemonic'].endswith('.W')],byte_writers=[i['address'] for i in writes if i['mnemonic'].endswith('.B')],long_writers=[i['address'] for i in writes if i['mnemonic'].endswith('.L')],neighbor='6926/692CF2F4/F2F5BYTEwrites do notoverlapF2F6. NoacceptedLONGF2F4/WORD F2F5explicitoverlapwritefound. F2F7BYTEF2E4doesoverlapselectorlowBYTE.'),
  domains=dict(negative_screen_sentinels=sentinels,nonnegative_modes80=modes,valid_mode_values=sorted(set(modes)),admission='Canonicallevelselector0..79provestenslotdomain; absenceofboundscheckdoesnotproveallcallers.',reward_bytes80=rewards,reward_domain_values=sorted(set(rewards)),reward_write='F2E4copiesF26FBYTEtoF2F7only, retainingoldF2F6highBYTE.37EAsetsF26FfrombackgroundpackedpointerhighBYTE. CannotassumeresultnonnegativeunlessoldhighBYTE0andselectedrewarddomainvalid.'),
  ancestry=['1B18worldinitializationclearsselector0;worldloopuses9E98camera ratherthan4D54.','1C54worldadmissionwritesA368resolvedselectorandF2F0;1BDCrestartcopiesF2F0whichalsohas6FF0table-drivenproducer.','934Aclass07exitwritesparam&127, proving0..127only untilactualMAPparameterinventorynarrowsit.','Screens/initwriteFFFF/FFFE/FFFD/FFFC/FFFB; theirmainstatesareseparatefromordinary1C6Clevelcamera path.','4D54branches4EAAonfreeze flags;4E80normalcamera branches4EAAaftermovement. Theseareconditionalancestors,notexplicitselectorchecks.'],
  remaining=['A368route/node domains,F2F0level/debugselectiontabledomains,class07paramdomains needactualdata/caller closure.','F2E4priorselectorhighBYTE andrewardselectorvalidity acrossallcallbacks remainrequired.','BulkRAMreset andregisterheldoverlappingaliases areoutsideexplicitabsolute census.','No global4ED6resolution from80tablevaluesalone.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/level-selector-writer-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print(f"Verified{len(r['overlapping_selector_writers'])}explicitselectorwriters; canonical80modeinputs only")

