"""Canonical world sprite cardinality and scratch extent; static data only."""
import hashlib,json,collections
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_maps import long,parse_map,initial_selection
from rolo_codec import decode_backward_lz
from rolo_sprites import sequence_frames,frame_record
RANGES=((0xa3b4,0xa50a),(0x9f72,0x9fee),(0x1a6e,0x1afe),(0x1b62,0x1b70),(0x3c08,0x3c3a))
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
  if at!=end:raise ValueError('Extent mismatch')
 source=long(rom,0x4ab1a)&0xffffff;data=decode_backward_lz(rom,source)[0];layout=parse_map(data)
 markers=[dict(**m,node_selector=initial_selection(rom,m['x']+5,m['y']),published_x=m['x']+5) for m in layout['records'] if m['type']>>8==14]
 if len(markers)!=70 or len({m['node_selector'] for m in markers})!=70:raise ValueError('World marker cardinality')
 actors=[]
 for definition,selectors in((0x13eaa,(0,4,8,12)),(0x14ede,(0,))):
  table=long(rom,definition+18);programs=[];chunks=0
  for selector in selectors:
   start=long(rom,table+selector)&0xffffff;frames,controls=sequence_frames(rom,start)
   records=[frame_record(rom,f) for f in frames]
   if any(c['command'] in(92,100) for c in controls):raise ValueError('World animation spawn')
   chunks=max(chunks,max(((f['width']+31)//32)*((f['height']+31)//32) for f in records))
   programs.append(dict(selector=selector,start=start,frames=records,controls=controls))
  actors.append(dict(definition=definition,linked=long(rom,definition),max_chunks=chunks,programs=programs))
 pairs=[v for m in markers for v in(m['published_x'],m['y'])]+[65535]
 xs={224,736}|{max(224,min(736,m['published_x']-336)) for m in markers}
 ys={224,832}|{max(224,min(832,m['y']-240)) for m in markers}
 max_visible=0;best=None
 for x in xs:
  for y in ys:
   count=sum(x-16<=m['published_x']<=x+336 and y-16<=m['y']<=y+240 for m in markers)
   if count>max_visible:max_visible=count;best=[x,y]
 return dict(rom_sha256=ROM_HASH,instruction_evidence=evidence,map_source=source,nonvisual_classes=dict(collections.Counter(str(m['type']>>8) for m in layout['records'] if not m['visual'])),markers=markers,actors=actors,
  all_completed_golden_words=pairs,golden_word_sha256=hashlib.sha256(b''.join(v.to_bytes(2,'big') for v in pairs)).hexdigest(),
  scratch=dict(start=0xffff7188,max_pairs=70,bytes=282,end_exclusive=0xffff72a2,meaning='Actual all-completed XYwordpairs plusFFFFterminator; allocatedscratchcapacity notinferred.'),
  capacity=dict(hud=5,actor_chunks=sum(a['max_chunks'] for a in actors),whole_map_marker_bound=70,conservative_total=77,limit=80,visible_marker_max=max_visible,visible_example_camera=best,visible_total_upper=max_visible+7,guard='A436hasno80guard; safetycomesfromcanonicalpopulation/cardinality,notinventedclamp.'),
  proof=['Originalworldstartup1B62reinitializesactorpool27DAthen3478groups;9F72allocatesexactly13EAA/14EDE,bothlinkeddefinition0.','MAP0nonvisualrecordsareonlyclass0E,whichhandler4904isRTSratherthanactorfactory.','Reachablecursorselectors0/4/8/12andbunnyselector0havenoanimation spawnandmaximumoneSATchunkperactor.','World1A6Ecalls5060HUDonceanddoesnot5348trunkFX;prior3448reservedresetconditionsremaincallercontract.','A3B4appendsonlysubsetof70markersbasedprogressbit1; allcompletedismaximalset.'],
  remaining=['Canonicalstartup/poolreset andvalidcursorselector domains musthold; arbitraryretainedpoolorselectorstate notcovered.','F266priorclear/singleHUDcallercondition fromsprite-origin report remainsrequired.','Scratchallocatedownership282bytes andqueuecapacity notprovenbycardinalityalone.','A436noguardmustremainliteralfornoncanonicalpopulation; no globalSATcapacityclaim.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/world-sprite-capacity-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print(f"World conservativeSATbound77/80; visiblemarkermax{r['capacity']['visible_marker_max']}; scratch282bytes")
