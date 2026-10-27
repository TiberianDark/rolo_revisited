"""Bounded world-control contracts and scene dependencies; never run ROM code."""
import hashlib,json,csv
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    directory=project/'docs/stage9';rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
    inventory=json.loads((directory/'inventory.json').read_text())
    accepted={a for routine in inventory['routines'] for a in routine['blocks']}
    def evidence(ranges):
        rows=[]
        for start,end in ranges:
            at=start
            while at<end:
                item=Decoder(rom,at).decode()
                if at not in accepted:raise ValueError(f'Unaccepted boundary {at:06X}')
                rows.append(item);at+=item['size']
            if at!=end:raise ValueError('Code/data boundary crossed')
        return rows
    specs=[
        (0x9e98,[(0x9e98,0x9f60)],'World camera target and speed table',
         'Unpaused C4E0 or paused C5BA supplies XY. Signed lower224 then upperwidth-544/height-448 clamp writes sharedC494/C498. 63A6 normalizes camera integer-to-target vector into LONG16.16 components and maximum WORD deltaD2. Table9F60 selects shift0 throughdistance10,1 through20,2 through40,3 above40 (80 entry then FFFF retains3). Shifted components add toF362/F366 LONGs; INTEGER words publish to both plane18/20.',
         'C5BA pause actor14EDE lifecycle/input; signed overflow/extent domains and interrupt aliases; full hardware scroll timing and independent camera reference.'),
        (0x63a6,[(0x63a6,0x63fa)],'Normalized signed coordinate vector',
         'WORD target-minus-origin differences record subtractionN inD7/D6 then NEGnegative. Signed larger-axis compare optionally exchangesD2/D3. ZeroD2 returns0/0. MinorWORD shifted16 DIVUmajorWORD; overflow selects10000 elselowquotient. Major10000/minorratio swappedaccordingtoaxis, LONGnegated bysavedN. D2retainsmajorWORD.',
         'All caller upperWORD/register domains, signed8000/overflow cases, zero-vector flags, DIVU overflow and native proof outside valid world coordinate extent.'),
        (0x1a6e,[(0x1a6e,0x1afe)],'World frame ordering',
         'C466 mismatch enters1AFE. Ordered sixteen direct services run before F270 pause gating. Unpaused action bit0 OR(C47D,C47E,C47F) TAIL branches1C46, skipping Start handling even if moving-route admission returns immediately. Otherwise C47C bit0 toggles F270 via NOT.B (00/FF). Pausing skips movement via9FEE but does not skip actor/animation/display services.',
         'Full C466/C444 state mutation ordering; queued transfers, interrupt timing and all called service domains; actual SDL original input/route/fade services remain unbound.'),
        (0x9fee,[(0x9fee,0xa02a)],'World movement two substeps',
         'Resolve C4E0 actor; clear actor70, return when F270 nonzero. Twice subtract2 from integer Y, callA02A, add2 and snapshot integer X/Y into F27C/F27E. Two calls execute even if first reaches a route terminator. Fractions are untouched.',
         'C4E0 lifetime and all actor117 writers; original-reference substep/animation cases and full host service adoption.'),
        (0xa02a,[(0xa02a,0xa092),(0xa09a,0xa0e8)],'World cell transition and availability',
         'Actor117 inhibits update. Compare integer XY alignedFFF0 against F278/F27A. Crossing selects D5 up0/down6/left12/right18 with X priority. A368 reads selector at the CURRENT actor position (including temporary Y-2). Test C558[selector]bit0; absent restores actor XY to old F278/F27A and reverses direction through four literal words atA092. A204 resolves ring tile; invalid returns. Valid descriptor offset plus D5 selects six-byte pointer/negateX/negateY record atA22C into F274/F271/F272.',
         'All reachable signed XY/descriptor boundaries, selector byte aliases, tile/ring producers and route mutation/reference cases. Original has no native guard for out-of-grid memory reads.'),
        (0xa0e8,[(0xa0e8,0xa18a)],'Route pairs and animation hysteresis',
         'Store XY anchors before consuming F274. Zero pointer entersA18A. First byte zero-extends into WORD; its bit7 terminates without reading Y, clearing pointer and actor70/48. Positive X selects animation4 and optional WORD negation/facingbit3 viaF271. Y also zero-extends; there is NO negative-byte terminator for Y. Nonzero Y selects12 or8 throughF272. Advance pointer by2 and add wrapped WORD deltas. If desired animation differs from actor48, keep prior animation in70 until decrement actor46 reaches zero; then accept new48/70 and reload46=2.',
         'Finite byte stream and mid-cell reselection proof for every reachable route; actor46 initialization/underflow and actor118 producers; independent movement/animation comparison.'),
        (0xa18a,[(0xa18a,0xa204)],'World input route admission',
         'C480..C483 priority up/down/left/right. Arithmetic-shift integer XY by4, adjust candidate cell, then shift back. A204 rejects candidate tile outside28..123. Check nonzero descriptor pointer atA22C+tileGroup+direction, but LOAD start pointer/sign flags fromA22C+0090+direction, not the candidate descriptor. This permits the entry route to reach the next cell before actual path reselection.',
         'All C480 byte producers and signed coordinate boundary domains; original start-route overlap and first-step/reference verification.'),
        (0xa204,[(0xa204,0xa22c)],'Ring tile route descriptor domain',
         '8728 supplies tileword. Mask01FF, subtract28 and signed-reject negative or greater95. DIVU8 then SWAP obtains remainder; multiply24 yields descriptor offsets0,24,48,72,96,120,144,168. With direction0/6/12/18 the complete six-byte lookup remains within192-byteA22C..A2EC.',
         '8728 live ring/scroll producer proof, all reaching coordinate wrap cases; accepted tile range does not itself prove route reachability.'),
        (0xa368,[(0xa368,0xa3b4)],'World actor-to-node selector and shared scratch',
         'Copy C4E0 actor integer XY to shared C494/C498; A37E ASR6 Y minus4 gives row. row&FFFC selects descriptor group by doubled byte offset; row modulo4 times descriptor width plus ASR6 X minus descriptor base indexes node byte. Mask returned selector to00FF. The supplied three groups span80 nodes; external callers can pass shared scratch throughA37E without C4E0 refresh.',
         'Global C494/C498 writers, all caller signed XY domains and adjacent descriptor/node reads outside the three checked groups.'),
    ]
    operations=[]
    for entry,ranges,name,contract,pending in specs:
        operations.append(dict(entry=f'{entry:04X}',name=name,contract=contract,pending=pending,
            native_sources=['src/core/world_route.hpp'] if entry in (0x9fee,0xa02a,0xa0e8,0xa18a,0xa204) else ['src/core/world_camera.hpp'] if entry in (0x9e98,0x63a6) else [],
            instruction_evidence=evidence(ranges),code_ranges=[dict(start=a,end_exclusive=b,sha256=hashlib.sha256(rom[a:b]).hexdigest()) for a,b in ranges]))
    fields=[('C4E0',4,'world controlled actor key'),('C466',4,'current initialized main state'),('C494',2,'shared selector X scratch'),('C498',2,'shared selector Y scratch'),('C480',4,'four direction byte gates'),('C558',80,'puzzle and rescue flags; bit0 route availability'),('F270',1,'world pause flag'),('F271',1,'route X negation'),('F272',1,'route Y negation'),('F274',4,'next route byte-pair pointer'),('F278',2,'last integer X route anchor'),('F27A',2,'last integer Y route anchor'),('F27C',2,'post-substep integer X snapshot'),('F27E',2,'post-substep integer Y snapshot')]
    calls=[dict(owner=o['entry'],address=i['address'],target=i.get('target'),mnemonic=i['mnemonic'],operands=i['operands']) for o in operations for i in o['instruction_evidence'] if i['mnemonic'] in ('BSR','JSR')]
    shared_fields=[]
    for address,size,meaning in fields:
        references=[dict(entry=op['entry'],instruction=f"{item['address']:06X}",mnemonic=item['mnemonic'],operands=item['operands'])
            for op in operations for item in op['instruction_evidence'] if '$FFFF'+address in item['operands']]
        shared_fields.append(dict(address=address,bytes=size,meaning=meaning,direct_references=references,
            pending='Direct absolute references within these ranges only; pointer aliases, array element accesses and external readers/writers require separate proof.'))
    return dict(rom_sha256=ROM_HASH,scope='Bounded static control contracts. Native development map shortcut is not the original world frame. No instruction execution or full fidelity claim.',operations=operations,
        immutable_data=[dict(start='A092',end_exclusive='A09A',words=[int.from_bytes(rom[a:a+2],'big') for a in range(0xa092,0xa09a,2)],scope='direction reversal table, excluded from instructions'),dict(start='9F60',end_exclusive='9F72',words=[int.from_bytes(rom[a:a+2],'big') for a in range(0x9f60,0x9f72,2)],scope='camera exponent/threshold pairs andFFFFsentinel; excluded from instructions')],
        shared_fields=shared_fields,calls=calls,
        ordered_roadmap=['Bind original9F72 actor allocation and route/global init from1BF2/9E3A.', 'Bind8728 live world-plane tile lookup and verified signed coordinate domains.', 'Translate9FEE/A02A/A0E8/A18A with exact two-substep call order and pointer reselection.', 'Connect originalA436/9DD6/1C46 selection, pause/input gates, actor cursor graphics and scene changes.', 'Bind original1AFE queues/palette/fades/music ordering; compare independent original scenes and routes.'])

def main():
    project=Path(__file__).resolve().parents[1];directory=project/'docs/stage9';report=catalogue(project)
    (directory/'world-control-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    links_path=directory/'routine-contract-links.json';links=json.loads(links_path.read_text())
    links=[r for r in links if r.get('generated_by')!='inventory_world_control.py']
    for op in report['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='world-control-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded static evidence; native world frame and independent fidelity pending',generated_by='inventory_world_control.py'))
    selection=json.loads((directory/'world-selection-contract.json').read_text())
    for row in selection['recommended_assessments']:
        links.append(dict(row,generated_by='inventory_world_control.py'))
    pause_actor=json.loads((directory/'world-pause-actor-contract.json').read_text())
    for op in pause_actor['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='world-pause-actor-contract.json',scope=op['contract']+' Pending: '+ '; '.join(pause_actor['remaining']),status='bounded static instruction evidence; native rabbit bound; full scene/device/reference domains pending',generated_by='inventory_world_control.py'))
    interrupt_clock=json.loads((directory/'interrupt-palette-clock-contract.json').read_text())
    for op in interrupt_clock['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='interrupt-palette-clock-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded original interrupt/continuation evidence; native scheduler and fidelity pending',generated_by='inventory_world_control.py'))
    entry_services=json.loads((directory/'level-entry-services-contract.json').read_text())
    for op in entry_services['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='level-entry-services-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded original entry service; caller/native fidelity pending',generated_by='inventory_world_control.py'))
    storage_reset=json.loads((directory/'level-entry-storage-reset-contract.json').read_text())
    for op in storage_reset['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='level-entry-storage-reset-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded original storage reset; caller/native fidelity pending',generated_by='inventory_world_control.py'))
    marker_callback=json.loads((directory/'entry-marker-callback-contract.json').read_text())
    for op in marker_callback['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='entry-marker-callback-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded original marker callback; fullcaller/native fidelity pending',generated_by='inventory_world_control.py'))
    loader_reset=json.loads((directory/'loader-storage-display-reset-contract.json').read_text())
    for op in loader_reset['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='loader-storage-display-reset-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded original loader reset; fullcaller/native fidelity pending',generated_by='inventory_world_control.py'))
    transport=json.loads((directory/'level1-transport-contract.json').read_text())
    links.append(dict(address='3EE4',name='First matching class11 transporter destination',path='level1-transport-contract.json',scope=transport['destination_search']+' Pending: '+'; '.join(transport['remaining']),native_sources=['src/core/trigger_destination.hpp'],status='bounded static and native lookup; full transition and reference fidelity pending',generated_by='inventory_world_control.py'))
    links.append(dict(address='937A',name='Resumable original within-level transport',path='level1-transport-contract.json',scope='Ordered937A phases: '+', '.join(transport['transition_order'])+' Connected nativeclass8/SDL paths; pending fullSAT/device queue timing, audio and independent original reference.',native_sources=['src/core/level1_transport_world.hpp','src/core/player_trigger_continuation.hpp','src/core/transporter_continuation.hpp','src/core/transporter_companions.hpp','src/core/palette_effect.hpp','src/core/actor_palette_raster.hpp'],status='bounded native activation and SDL fade connected; full device/reference fidelity pending',generated_by='inventory_world_control.py'))
    fade_companions=json.loads((directory/'transport-fade-companion-contract.json').read_text())
    for op in fade_companions['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='transport-fade-companion-contract.json',scope=op['contract']+' Pending: '+op['pending'],status='bounded original transition followup; fullcaller/native fidelity pending',generated_by='inventory_world_control.py'))
    for path in ('sprite-frame-contract.json','sprite-list-tail-contract.json','sprite-origin-reserved-contract.json','sorter-installation-contract.json','live-sorter-word-contract.json','scroll-mode-producer-contract.json','word-transfer-queue-contract.json','display-utility-contract.json','campaign-statistics-contract.json','palette-resource-contract.json','ending-sequence-contract.json'):
        sprite_contract=json.loads((directory/path).read_text())
        subsystem={
            'scroll-mode-producer-contract.json':'camera and scroll',
            'word-transfer-queue-contract.json':'graphics transfer publication',
            'display-utility-contract.json':'text and tile presentation',
            'campaign-statistics-contract.json':'campaign score and progression',
            'palette-resource-contract.json':'palette resources',
            'ending-sequence-contract.json':'ending scenes and state transitions',
        }.get(path,'sprite ordering and publication')
        for op in sprite_contract['operations']:
            group=subsystem
            if op['entry'].upper()=='63A6':group='camera and scroll'
            if op['entry'].upper()=='B1C6':group='actor callbacks and control'
            if op['entry'].upper() in ('8C06','879A','8BB0','38C2','8770','87BC','87DC','87F6'):group='terrain coordinate queries'
            if op['entry'].upper() in ('6980','6984','6988','698C'):group='camera and scroll'
            if op['entry'].upper()=='5CE6':group='sound command timing'
            if op['entry'].upper()=='51D0':group='graphics transfer publication'
            links.append(dict(address=op['entry'],name=op['name'],path=path,subsystem=group,scope=op['contract']+' Pending: '+op['pending'],status='bounded original '+group+'; full caller/native fidelity pending',generated_by='inventory_world_control.py'))
    for text_path in ('scrolling-text-contract.json','text-control-contract.json'):
        text_contract=json.loads((directory/text_path).read_text())
        for op in text_contract['operations']:
            links.append(dict(address=op['entry'],name=op['name'],path=text_path,subsystem='text and tile presentation',scope=op['contract']+' Pending: '+op['pending'],status='bounded original text; full caller/native fidelity pending',generated_by='inventory_world_control.py'))
    scene_contract=json.loads((directory/'scripted-player-exit-contract.json').read_text())
    for op in scene_contract['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='scripted-player-exit-contract.json',subsystem='scripted scene and player transitions',scope=op['contract']+' Pending: '+op['pending'],status='bounded original scripted scene; full caller/native fidelity pending',generated_by='inventory_world_control.py'))
    terrain_contract=json.loads((directory/'terrain-bank-domain-contract.json').read_text())
    for op in terrain_contract['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='terrain-bank-domain-contract.json',subsystem='terrain loading and metadata',scope=op['contract']+' Pending: '+op['pending'],status='bounded original terrain loading; full caller/native fidelity pending',generated_by='inventory_world_control.py'))
    for source_path,group in (('terrain-streaming-contract.json','terrain streaming'),('level-selector-writer-contract.json','camera and selector domains'),('connected-actor-callback-contract.json','actor contact and callback transitions'),('spawned-actor-callback-contract.json','spawned actor callback transitions')):
        source_contract=json.loads((directory/source_path).read_text())
        for op in source_contract['operations']:
            links.append(dict(address=op['entry'],name=op['name'],path=source_path,subsystem=group,scope=op['contract']+' Pending: '+op['pending'],status='bounded original '+group+'; full caller/native fidelity pending',generated_by='inventory_world_control.py'))
    collision_contract=json.loads((directory/'player-collision-binding-contract.json').read_text())
    for op in collision_contract['operations']:
        links.append(dict(address=op['entry'],name=op['name'],path='player-collision-binding-contract.json',subsystem='player collision bindings',scope=op['contract']+' Pending: '+op['pending'],native_sources=[op['native_source']],status='bounded original/native collision helper; full caller/reference fidelity pending',generated_by='inventory_world_control.py'))
    # Attach current bindings to pre-existing jigsaw contracts, preserving partial status.
    for row in links:
        if row.get('path')=='world-jigsaw-contract.json':
            row['native_sources']=['src/core/world_map.hpp','src/core/world_map_raster.hpp']
            row['status']='bounded static contract; native jigsaw helpers bound; full scene/caller/fidelity domains pending'
    links_path.write_text(json.dumps(links,indent=2)+'\n')
    with (directory/'world-control-calls.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['owner','address','target','mnemonic','operands']);writer.writeheader();writer.writerows(report['calls'])
    print(f"World control: {len(report['operations'])} contracts, {len(report['calls'])} direct call records")
if __name__=='__main__':main()
