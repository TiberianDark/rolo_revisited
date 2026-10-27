"""Pinned world pause-camera rabbit allocation, lifecycle and input evidence."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_sprites import sequence_frames,frame_record

SPECS=(
 (0x9f72,0x9fee,'World actor allocation','Allocate13EAA cursor first; clear all three6402 rescued companion pointers, then unconditionally allocate14EDE at zero X/Y/fractions/facing/marker. Publish returnedD0 intoC5BA; reset shared RNG seedC4BE=3. There is no rescue/completion gate on14EDE allocation and no explicit second-allocation failure check.'),
 (0xe7be,0xe83a,'Rabbit integration, clamp and direction dispatch','Integrate prior signed velocities viaCFCE before bounds checks. Signed clamp X to264..F330-264 and Y to272..F332-256; clamping clears corresponding LONG speed and directionBYTE46 but retains coordinate fraction. D0=0x4000 acceleration,D1=0x20000 cap. If F270 nonzero branchE8D6; otherwise decrement signedWORD50, clearBYTE46 if negative, dispatchBYTE46*2 through nine BRA slotsE83A..E84C.'),
 (0xe83a,0xe8d6,'Unpaused rabbit wandering','Direction0 preserves D0/D1, calls716E with[1,9) to setBYTE46 and[40,50) to setWORD50, restores acceleration/cap, then redispatches immediately. Directions1..8 apply up,up-right,right,down-right,down,down-left,left,up-left respectively. Left sets118bit3; right clears118bit3. Diagonals invoke vertical helper before horizontal helper. Random interval upper bounds are exclusive.'),
 (0xe8d6,0xe912,'Paused rabbit held input','Read individual held direction bytesC480/C481/C482/C483. In order up/down/left/right, each nonzero byte invokes acceleration helper; left sets118bit3,right clears it. No collision probes, rescue follow, or animation-selector change occurs. Prior velocity continues to integrate when no direction is held; no friction is applied here.'),
 (0xcfce,0xcffc,'Signed actor position integration','For each axis, directionBYTE121/122 zero skips integration; positive adds LONG58/62 to positionLONG12/16, negative subtracts. Position fractions participate in original LONG arithmetic.'),
 (0xd06c,0xd094,'Accelerate right','Opposing negative direction subtracts acceleration from speed; if result becomes negative negate and set positive direction. Otherwise retain opposing direction while decelerating. Same direction adds acceleration, caps againstD1 and sets direction+1.'),
 (0xd094,0xd0ba,'Accelerate left','Opposing positive direction subtracts acceleration, flips only on negative result. Same direction adds acceleration/caps and sets directionFF.'),
 (0xd0ba,0xd0e2,'Accelerate down','Vertical analogue ofD06C usingBYTE122/LONG62.'),
 (0xd0e2,0xd108,'Accelerate up','Vertical analogue ofD094 usingBYTE122/LONG62.'),
 (0x716e,0x719a,'Shared bounded RNG','Subtract lowerD0 from upperD1; nonpositive width returns0. SeedWORDC4BE defaults3 if0. Unsigned multiply seed*0x4E35; store product lowWORD as next seed. Divide product highWORD by width, add remainder to lowerD0. D2WORD preserved.'),
 (0x1a6e,0x1afe,'World update and pause sequencing','29EE rebuilds lifetime/list state; A808 then dispatches actor callbacks before9E98 camera andFCD4 animation/FAA0 publication. F270 gates world admission after all these services; Startedge C47Cbit0 togglesF270 at end of frame. Therefore paused world continues rabbit movement/animation and camera, while9FEE skips cursor route movement.'),
)

def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
 inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
 accepted={a for r in inventory['routines'] for a in r['blocks']}
 operations=[]
 for start,end,name,contract in SPECS:
  at=start;instructions=[]
  while at<end:
   item=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:06X}')
   instructions.append(item);at+=item['size']
  if at!=end:raise ValueError('Crossed instruction range')
  operations.append(dict(entry=f'{start:04X}',end_exclusive=f'{end:04X}',name=name,contract=contract,instruction_evidence=instructions,sha256=hashlib.sha256(rom[start:end]).hexdigest()))
 table=0x1304c;delay=rom[table];stream=int.from_bytes(rom[table+1:table+4],'big')
 frames,controls=sequence_frames(rom,stream)
 records=[frame_record(rom,f) for f in frames]
 if [r['descriptor'] for r in records]!=[0x13078,0x1308a,0x1309c,0x130ae,0x130c0]:raise ValueError('Unexpected rabbit animation')
 if any(r['graphics'][0]!=0 or r['width']!=16 or r['height']!=16 for r in records):raise ValueError('Unexpected rabbit geometry')
 definition=rom[0x14ede:0x14f00]
 return dict(rom_sha256=ROM_HASH,scope='Bounded static original world rabbit/pause camera evidence; no ROM execution. This actor is allocated independently of rescued companions.',operations=operations,
  actor=dict(definition='14EDE',bytes=definition.hex(),callback='E7BE',grouping_word='32C8',animation_table='1304C',flags_word='C000',resource_units=128,type_word=0,initial_x=0,initial_y=0,pointer='C5BA',allocation_failure='Second allocation return published without explicit check'),
  animation=dict(selector=0,delay=delay,start=stream,frames=records,controls=controls,stream_bytes=rom[0x13050:0x13078].hex(),data_ranges=[['1304C','13050'],['13050','13078'],['13078','130D2']],graphic_hashes=[dict(source=r['graphics'][1],bytes=r['byte_count'],sha256=hashlib.sha256(rom[r['graphics'][1]:r['graphics'][1]+r['byte_count']]).hexdigest()) for r in records]),
  shared_fields=[dict(address=a,bytes=n,meaning=m) for a,n,m in [('C5BA',4,'pause-camera rabbit actor pointer'),('F270',1,'world pause state'),('C480',4,'held up/down/left/right bytes'),('C47C',1,'Start input edge'),('C4BE',2,'shared RNG seed'),('F330',2,'map width'),('F332',2,'map height')]],
  conclusions=['The extra rabbit is unconditional world actor14EDE, not a rescued companion retained in6402 slots.','Its animation is a five-frame16x16 rabbit, independently extracted from original graphics.','Paused9E98 followsC5BA; unpaused9E98 followsC4E0.','Screenshot beside cursor is not a guaranteed follow-position contract: unpaused rabbit wanders independently.'],
  remaining=['Original allocator resource mapping and animated sprite publication order must be reused by binding.','C480 held-byte producer, interruption/publication timing and second-allocation failure caller domain remain outside this bounded report.','Exact screenshot rabbit coordinates cannot be inferred without frame count and shared RNG consumption history.'])

if __name__=='__main__':
 project=Path(__file__).resolve().parents[1];report=catalogue(project)
 (project/'docs/stage9/world-pause-actor-contract.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f"Verified{len(report['operations'])} original world-rabbit operations and5 frames")

