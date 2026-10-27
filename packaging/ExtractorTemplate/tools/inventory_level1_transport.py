"""Pinned Level1 within-level transporter markers and callback evidence."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_maps import long,parse_map
from rolo_codec import decode_backward_lz
from rolo_sprites import sequence_frames,frame_record
RANGES=((0x463c,0x4694),(0x4826,0x4832),(0x4a84,0x4adc),(0x925c,0x92f2),(0x9336,0x933a),(0x937a,0x93fe),(0x3ee4,0x3f34))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};evidence=[]
 for start,end in RANGES:
  at=start
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   evidence.append(i);at+=i['size']
  if at!=end:raise ValueError('Instruction extent mismatch')
 source=long(rom,0x4ab22)&0xffffff
 data=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
 records=parse_map(data)['records'];triggers=[r for r in records if r['type']>>8==8];destinations=[r for r in records if r['type']>>8==17];scenery=[r for r in records if r['type']==0x519]
 links=[]
 for t in triggers:
  target=next((d for d in destinations if d['type']&255==t['type']&255),None)
  links.append(dict(trigger=t,destination=target,actor_destination=None if target is None else dict(x=target['x']+8,y=target['y'])))
 child=int.from_bytes(rom[0x118f0:0x118f4],'big')
 child_frames,child_controls=sequence_frames(rom,0x11904)
 if child!=0x157e6:raise ValueError('Unexpected portal sparkle child')
 return dict(rom_sha256=ROM_HASH,instruction_evidence=evidence,foreground_source=source,trigger_markers=triggers,destination_markers=destinations,paired_scenery=scenery,links=links,
  visual=dict(emitter=0x15808,definition_bytes=rom[0x15808:0x1582a].hex(),resource_units=0,table=0x118e8,stream=0x118ec,controls=sequence_frames(rom,0x118ec)[1],spawned_definition=child,spawn_parameter=16,hold_parameter=0x1e05,child_definition_bytes=rom[child:child+34].hex(),child_frames=[frame_record(rom,f) for f in child_frames],child_controls=child_controls,meaning='15808 is invisible zero-resource emitter withthree animationnodes, notthreeframes. Its157E6child supplies16x16sparklingportalgraphics withpalette3original6000flags.'),
  dispatch='Class08 index(0800-0400)>>6=16 selects467C BRA4826.4826 storesparamBYTE asD4,D0=68,D2=0 andtail4A84 trigger allocation.',
  initialization='4A84 pops68EEfreepointer; empty returns withouttrigger. Links16byte node into6A36 list, writesXWORD4,YWORD6,dispatchoffsetWORD8=68,paramBYTE10,repeatBYTE11=0,MAPrecordlowWORD12 andoldclassBYTE14. ReplacesMAPclassBYTE with17hex sentinel.',
  interaction='925C loadscontrolledactorC4E0integerX/Y intoD6/D7.926C scansnodes, signedcamera-culls; inclusively testsX..X+17,Y..Y+17. dispatchoffset68 routes9336→937A. RepeatBYTE11=0 means trigger remainslinked. No Up/action test in937A.',
  destination_search='3EE4 scansforegroundMAProws in ascendingorder forclassBYTE11hex,parammatchingD0BYTE; firstmatchreturnsD6=X+8,D7=row*16,D0=0; missingreturnsD0=-1 and937Areturnsunchanged.',
  transition_order=['Sound1D','SaveD6/D7WORD','63FAblockingblackfade','RestoreD6/D7','SetC4E0actorX/Yandzero fractions','Clear121/122directionsand58/62LONGspeeds','684E','6864','4CB8camerareset','7292','72A2','6960','6AA6','31D6','25A8','66DEfadein','IfC4E8type4callAC34'],
  findings=['0801teleports to1101at288,1296 => actor296,1296.','0802teleports to1102at128,528 => actor136,528.','Thesearewithin-level destinations, notworldmap/levelselectors.','Class0519 definition15808 visuals areseparatefromclass08triggerrecords; renderingitdoesnotimplementtransport.'],
  remaining=['925C upstreamplayerinteraction gates andnativeactor/list lifetimecapacity needbinding.','Originalblackfade andfadein suspendedcontinuation services mustberespected.','Macro-markerbyte sentinel17 aliasesclass17decimal destination differently: sentinel17hex is23decimal, whiledestinations11hex are17decimal.','Failednodeallocation and missingdestination mustremainexplicit.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/level1-transport-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified Level1 transporter2trigger/destination links and original937A transition')
