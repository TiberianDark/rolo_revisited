"""Reproducible conservative static conversion inventory; never executes ROM code."""

import argparse

import csv

import hashlib

import json

import re

import struct

from collections import defaultdict

from pathlib import Path

from m68k_static import walk, listing, Decoder

from trace_rolo import NOTES

from rolo_codec import decode_backward_lz, DecodeError



ROM_HASH = '9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'



def definitions(data):

    return [dict(address=a, linked=struct.unpack_from('>I',data,a)[0],

                 handler=struct.unpack_from('>I',data,a+12)[0],

                 selector=struct.unpack_from('>H',data,a+16)[0],

                 animation_table=struct.unpack_from('>I',data,a+18)[0],

                 field_22=struct.unpack_from('>I',data,a+22)[0],

                 field_26=data[a+26],field_27=data[a+27],

                 secondary_definition=struct.unpack_from('>I',data,a+28)[0],

                 secondary_selector=struct.unpack_from('>H',data,a+32)[0],

                 raw=data[a:a+34].hex()) for a in range(0x13eaa,0x1582a,34)]



def sound_assets(data):

    assets=[]

    for kind,base,count in [('effect',0x78926,0x5b),('music',0x78a92,0x21)]:

        for slot in range(count):

            source=struct.unpack_from('>I',data,base+slot*4)[0]

            record=dict(kind=kind,slot=slot,pointer_address=base+slot*4,source=source,

                        status='sequence interpretation pending')

            if kind=='music':

                try:

                    decoded,evidence=decode_backward_lz(data,source)

                    record.update(codec=evidence,decoded_sha256=hashlib.sha256(decoded).hexdigest())

                except DecodeError as error: record['decode_error']=str(error)

            assets.append(record)

    return assets



def object_fields(instructions):

    """Syntactic A5 displacements only; register/object aliasing still needs proof."""

    records=[]

    for i in instructions:

        for match in re.finditer(r'\((?:([+-]?\d+),)?A5\)',i['operands']):

            records.append(dict(offset=int(match.group(1) or 0),address=i['address'],

                mnemonic=i['mnemonic'],operands=i['operands'],

                scope='A5-relative operand candidate; not proof of object identity or read/write semantics'))

    return records



def continuation_candidates(data, contexts):

    """Validate recorded code-pointer producers without claiming a complete caller audit."""

    candidates=set()

    for context in contexts:

        observed=set()

        for producer in context.get('producers',[context.get('producer')]):

            decoded=Decoder(data,int(producer,16)).decode()

            if decoded['mnemonic']!='LEA' or not decoded['operands'].endswith(','+context['register']):

                raise ValueError('Invalid recorded continuation producer')

            observed.update(decoded['references'])

        if observed!={int(target,16) for target in context['targets']}:

            raise ValueError('Recorded continuation targets differ from ROM')

        candidates.update(observed)

    return candidates



def indexed_inline_candidates(data, contexts):

    """Accept explicit non-BRA entries justified by checked immediate call contexts."""

    candidates=set()

    for context in contexts:

        site=int(context['dispatch'],16);decoded=Decoder(data,site).decode()

        match=re.fullmatch(r'\(\+([0-9]+),PC,'+context['register']+r'\.W\)',decoded['operands'])

        if decoded['flow'] not in ('call','jump') or not match:

            raise ValueError('Invalid indexed inline dispatch')

        base=site+2+int(match.group(1))

        if base!=int(context['base'],16):raise ValueError('Indexed inline base differs')

        entry=int(context['forwarding_entry'],16);forward_site=int(context['forwarding_call'],16)

        prefix=Decoder(data,entry).decode();forward=Decoder(data,forward_site).decode()

        if prefix['mnemonic']!='MOVE.W' or prefix['operands']!='D0,-(A7)' or entry+prefix['size']!=forward_site:

            raise ValueError('Inline forwarding prefix differs')

        if forward['flow']!='call' or forward['target']!=site:raise ValueError('Inline forwarding call differs')

        offsets=set()

        for producer in context['producer_contexts']:

            source=Decoder(data,int(producer['producer'],16)).decode()

            call=Decoder(data,int(producer['call'],16)).decode()

            if source['mnemonic']!='MOVEQ' or source['operands']!=f"#{producer['value']},{context['register']}":

                raise ValueError('Inline index immediate differs')

            if source['address']+source['size']!=call['address'] or call['flow']!='call' or call['target']!=entry:

                raise ValueError('Inline index producer call context differs')

            offsets.add(producer['value'])

        for target in context['inline_targets']:

            address=int(target['address'],16)

            if target['offset'] not in offsets or address!=base+target['offset'] or address%2:

                raise ValueError('Indexed inline target not justified by producer')

            Decoder(data,address).decode()

            candidates.add(address)

    return candidates



def stack_continuation_candidates(data, contexts):

    candidates=set()

    for context in contexts:

        producer=Decoder(data,int(context['producer'],16)).decode()

        target=int(context['target'],16)

        if producer['mnemonic']!='PEA' or producer['references']!=[target]:

            raise ValueError('Stack continuation producer differs')

        if target%2 or not 0x200<=target<0x1015a:

            raise ValueError('Stack continuation target outside accepted code window')

        first=Decoder(data,target).decode()

        if [first['mnemonic'],first['operands']]!=context['target_instruction']:

            raise ValueError('Stack continuation target instruction differs')

        candidates.add(target)

    return candidates



def inventory(data, docs):

    if hashlib.sha256(data).hexdigest() != ROM_HASH:

        raise ValueError('Inventory requires the documented ROM revision')

    roots = defaultdict(set)

    stack_path=docs/'stage9'/'stack-continuation-contexts.json'

    stack_contexts=json.loads(stack_path.read_text(encoding='utf-8')) if stack_path.exists() else []

    for target in stack_continuation_candidates(data,stack_contexts):

        roots[target].add('Recorded stack-return continuation candidate; full caller/stack audit pending')

    inline_path=docs/'stage9'/'indexed-inline-targets.json'

    inline_contexts=json.loads(inline_path.read_text(encoding='utf-8')) if inline_path.exists() else []

    for target in indexed_inline_candidates(data,inline_contexts):

        roots[target].add('Indexed inline code target from checked immediate producer/call contexts')

    context_path=docs/'stage9'/'indirect-contexts.json'

    if context_path.exists():

        for target in continuation_candidates(data,json.loads(context_path.read_text(encoding='utf-8'))):

            roots[target].add('Recorded LEA continuation candidate; complete caller context pending')

    source_path=docs/'stage9'/'callback-sources.json'

    callback_sources=json.loads(source_path.read_text(encoding='utf-8')) if source_path.exists() else []

    for item in callback_sources:

        roots[int(item['target'],16)].add('Register-held callback from '+item['producer']+' to write '+item['write'])

    for p in sorted((docs/'disassembly').glob('*.json')):

        # Historical control seeds FE42/46/4A/4E are mid-instruction.

        if p.stem == 'player-animation-controls': continue

        old=json.loads(p.read_text(encoding='utf-8'))

        if old.get('rom_sha256') != ROM_HASH: continue

        for a in old.get('seeds',[]): roots[a].add('existing listing: '+p.name)

    for d in definitions(data): roots[d['handler']].add(f"definition ${d['address']:06X} +12")

    for d in definitions(data):

        # B702 explicitly loads definition+22 and JSR(A0), at B70C/B710.

        if d['handler']==0xb702:

            a=struct.unpack_from('>I',data,d['address']+22)[0]&0xffffff

            if 0x200<=a<0x1015a and a%2==0: roots[a].add(f"definition ${d['address']:06X} +22 via B710")

    for n in range(1,64):

        a=struct.unpack_from('>I',data,n*4)[0]&0xffffff

        if 0x200 <= a < 0x1015a and a%2==0: roots[a].add(f'ROM vector {n}')

    # Conservative hold-out for the asset region, not proof it contains no code.

    excluded=[(0x28e,0x2fa),(0x1015a,0x787f6)]

    for a in range(0xfe28,0xfe68,4):

        if data[a:a+2] != b'\x60\x00': raise ValueError('Animation dispatch slot is not BRA.W')

        roots[a].add('animation command branch table FE28..FE68')

    for a in range(0x7e764,0x7e7a0,4):

        if data[a:a+2]!=b'\x60\x00': raise ValueError('Sound API slot is not BRA.W')

        roots[a].add('15-slot sound API branch table E764..E7A0')

    tables={}

    for _ in range(12):

        trace=walk(data, sorted(roots), limit=50000, excluded=excluded)

        added=False

        for i in trace['instructions']:

            callback=re.fullmatch(r'#\$([0-9A-Fa-f]+),\(\+42,A[0-7]\)',i['operands']) if i['mnemonic']=='MOVE.L' else None

            dynamic_definition=i['address']==0x49b6 and i['mnemonic']=='MOVE.L'

            if callback or dynamic_definition:

                m=callback or re.match(r'#\$([0-9A-Fa-f]+),',i['operands'])

                if m:

                    a=int(m.group(1),16)&0xffffff

                    if 0x200<=a<len(data) and a%2==0:

                        if a not in roots: added=True

                        roots[a].add(f"callback pointer write ${i['address']:06X}: {i['operands']}")

            if i['flow'] in ('call','jump') and i['target'] is None:

                m=re.fullmatch(r'\(\+([0-9]+),PC,D[0-7]\.W\)',i['operands'])

                if m:

                    base=i['address']+2+int(m.group(1)); slots=[]

                    a=base

                    while a<min(base+512,len(data)-4) and data[a]==0x60:

                        branch=Decoder(data,a).decode()

                        slots.append(dict(address=a,target=branch['target'],size=branch['size']))

                        if a not in roots: added=True

                        roots[a].add(f"candidate indexed branch slot from ${i['address']:06X}; selector range unproved")

                        a+=branch['size']

                    if slots: tables[i['address']]=dict(dispatch=i['address'],base=base,slots=slots,

                        status='branch slots verified; selector bounds require data-flow trace')

            if i['flow']=='call' and i['target'] is not None:

                a=i['target']

                if a not in roots: added=True

                roots[a].add(f"direct call ${i['address']:06X}")

            if i['mnemonic']=='MOVE.L' and i['operands'].endswith(',($FFFFC444).L'):

                m=re.match(r'#\$([0-9A-Fa-f]+),',i['operands'])

                if m:

                    a=int(m.group(1),16)&0xffffff

                    if a not in roots: added=True

                    roots[a].add(f"main state pointer write ${i['address']:06X}")

        if not added: break

    for context in inline_contexts:

        table=tables.get(int(context['dispatch'],16))

        if table is None:raise ValueError('Indexed inline branch table missing')

        table['inline_targets']=[dict(offset=row['offset'],address=int(row['address'],16),scope=context['scope']) for row in context['inline_targets']]

    instructions={i['address']:i for i in trace['instructions']}

    possible_callbacks={d['handler'] for d in definitions(data)}|{0xa8bc,0xbe4e}

    for a,evidence in roots.items():

        if any('callback' in note.lower() for note in evidence):possible_callbacks.add(a)

    entries=set(roots)&set(instructions)

    edges=defaultdict(list)

    for e in trace['edges']:

        if e['kind']!='call': edges[e['source']].append(e['destination'])

    owners=defaultdict(set)

    routines=[]

    ledger_path=docs/'stage9'/'coverage-ledger.json'

    ledger=json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []

    context_path=docs/'stage9'/'indirect-contexts.json'

    contexts=json.loads(context_path.read_text(encoding='utf-8')) if context_path.exists() else []

    contract_path=docs/'stage9'/'routine-contract-links.json'

    contracts=json.loads(contract_path.read_text(encoding='utf-8')) if contract_path.exists() else []

    from verify_inactive_actor import verify as verify_inactive_actor
    verified_inactive=verify_inactive_actor(docs.parent)
    verified_leaf={}
    for report_name in ('native-event-boundary-verification.json','cold-boot-initialization-verification.json','startup-animation-scene-verification.json','fatal-diagnostic-verification.json','startup-image-scene-verification.json','startup-logo-raster-verification.json','startup-image-codec-verification.json','screen-text-dispatch-verification.json','startup-reset-entries-verification.json','player-presentation-entry-verification.json','scripted-player-scene-verification.json','choreography-creation-verification.json','map-publication-entries-verification.json','front-end-frame-entries-verification.json','startup-pixel-range-verification.json','animation-spawn-entries-verification.json','text-palette-entries-verification.json','screen-asset-entries-verification.json','enemy-phase-entries-verification.json','game-over-text-verification.json','startup-layout-entries-verification.json','music-selection-verification.json','sound-stream-loading-verification.json','actor-capture-phases-verification.json','scene-actor-factories-verification.json','menu-palette-transitions-verification.json','startup-pattern-publication-verification.json','sound-effect-submission-verification.json','renderer-checksum-contracts-verification.json','actor-lifecycle-stage-entries-verification.json','debug-menu-music-entries-verification.json','graphic-actor-shared-entries-verification.json','frame-input-setup-entries-verification.json','background-font-entries-verification.json','map-record-scan-verification.json','ending-scene-entries-verification.json','scene-control-entries-verification.json','entrance-actor-entries-verification.json','audio-interface-state-verification.json','actor-choreography-chain-verification.json','indexed-shared-access-verification.json','companion-return-entries-verification.json','startup-display-contracts-verification.json','actor-phase-ending-verification.json','text-numeric-sprites-verification.json','screen-text-controls-verification.json','campaign-node-completion-verification.json','text-tile-publication-verification.json','text-strip-publication-verification.json','level-menu-publication-verification.json','sprite-bucket-entries-verification.json','macro-graphics-entries-verification.json','linked-actor-families-verification.json','actor-remaining-motion-verification.json','macro-reward-entries-verification.json','level-map-entries-verification.json','actor-graphic-phases-verification.json','actor-phase-emitters-verification.json','input-transfer-entries-verification.json','palette-entry-contracts-verification.json','companion-entry-contracts-verification.json','controlled-actor-transition-verification.json','player-side-entries-verification.json','actor-facing-emitter-verification.json','actor-rescue-presentation-verification.json','actor-orbit-leap-verification.json','actor-probe-patrol-verification.json','actor-phase-mechanism-verification.json','actor-injury-dispatch-verification.json','leaf-routine-verification.json', 'terrain-query-verification.json', 'integer-y-verification.json', 'anchor-step-verification.json', 'floor-probe-verification.json', 'actor-land-verification.json', 'actor-chain-flag-verification.json', 'graphics-span-verification.json', 'object-overlap-verification.json', 'player-contact-verification.json', 'companion-query-verification.json', 'checkpoint-verification.json', 'random-range-verification.json', 'bounce-motion-verification.json', 'trunk-pull-verification.json', 'rescue-counter-verification.json', 'vertical-direction-verification.json', 'horizontal-direction-verification.json', 'companion-slots-verification.json', 'anchor-follow-offset-verification.json','sprite-frame-publication-verification.json','actor-scene-rewards-verification.json','actor-pursuit-family-verification.json','player-startup-followup-verification.json','backward-asset-codec-verification.json','display-port-publication-verification.json','platform-surface-verification.json','actor-platform-dispatch-verification.json','actor-bounce-chain-platforms-verification.json','actor-triggered-platforms-verification.json','direct-player-contact-verification.json','level-frame-orchestration-verification.json','actor-contact-family-verification.json','shared-frame-services-verification.json','actor-platform-family-verification.json','actor-wave-motion-verification.json','spawn-branch-family-verification.json','actor-anchor-follow-verification.json','actor-displacement-verification.json','animation-extra-controls-verification.json','animation-sound-control-verification.json','display-resource-reset-verification.json','phase-decimal-descriptor-verification.json','platform-contact-verification.json','actor-corner-motion-verification.json','collision-entries-verification.json','actor-common-callbacks-verification.json','actor-common-state-verification.json','quad-mapping-verification.json','menu-control-verification.json','bounce-spawn-verification.json','direction-vector-verification.json','visual-effects-verification.json','terrain-stream-batch-verification.json','companion-modes-verification.json','companion-follow-verification.json','companion-waiting-verification.json','transporter-alignment-verification.json','acceleration-bunny-verification.json','held-release-verification.json','player-presentation-verification.json','input-impact-scroll-verification.json','actor-allocation-verification.json','post-motion-verification.json','terrain-camera-verification.json','terrain-macro-verification.json','trigger-dispatch-verification.json','terrain-response-verification.json','player-contact-resolution-verification.json','world-jigsaw-verification.json','world-route-verification.json','world-shared-verification.json','camera-batch-verification.json','animation-controls-verification.json','actor-schedule-verification.json','actor-lifecycle-verification.json','graphics-pool-verification.json','marker-queues-verification.json','palette-batch-verification.json','player-floor-verification.json','player-ceiling-verification.json','collision-followups-verification.json','collision-phase-verification.json','movement-phase-verification.json','player-slope-verification.json','player-physics-batch-verification.json','input-phase-verification.json','direction-handler-verification.json','player-jump-verification.json','action-dispatch-verification.json','companion-wall-verification.json','player-wall-verification.json','enemy-wall-verification.json','wall-probe-verification.json','thrown-rest-verification.json','retirement-timer-verification.json','enemy-update-batch-verification.json','captured-actor-verification.json', 'container-update-verification.json', 'companion-flags-verification.json', 'companion-collision-verification.json', 'companion-follow-speed-verification.json', 'actor-pool-reset-verification.json', 'player-history-verification.json', 'reservation-pool-verification.json', 'companion-history-target-verification.json', 'actor-defeat-verification.json', 'player-damage-verification.json', 'object-contact-state-verification.json', 'exit-contact-verification.json', 'level-exit-verification.json', 'first-enemy-verification.json', 'reward-curve-verification.json', 'key-actor-verification.json', 'piece-collection-verification.json', 'rescue-progress-verification.json', 'pickup-callbacks-verification.json', 'score-batch-verification.json', 'powerup-pickups-verification.json', 'companion-attachment-verification.json', 'destination-verification-evidence.json', 'campaign-percentage-verification-evidence.json', 'companion-census-verification-evidence.json', 'level-reset-verification.json', 'entry-marker-verification.json', 'terrain-publication-verification.json', 'tile-metadata-verification.json', 'trigger-capture-verification.json', 'hud-request-batch-verification.json', 'companion-jump-verification.json', 'companion-pursuit-verification.json', 'collected-motion-verification.json', 'collected-update-verification.json','actor-rider-platforms-verification.json'):
        leaf_path=docs/'stage9'/report_name
        if not leaf_path.exists():continue
        leaf=json.loads(leaf_path.read_text(encoding='utf-8-sig'))
        if leaf['rom_sha256']!=ROM_HASH:raise ValueError('Verified leaf ROM revision mismatch')
        for path,digest in leaf['source_sha256'].items():
            if hashlib.sha256((docs.parent/path).read_bytes()).hexdigest()!=digest:raise ValueError('Stale leaf routine verification: '+path)
        for record in leaf['records']:
            if data[record['address']:record['end_exclusive']].hex()!=record['original_bytes']:raise ValueError('Verified leaf instruction bytes changed')
            record=dict(record,verification_evidence=report_name)
            verified_leaf[record['address']]=record
    from assess_shared_dispatch_slots import generate as assess_shared_dispatch_slots
    shared_slots={r['address']:r for r in assess_shared_dispatch_slots(docs.parent)['records']}
    from assess_level1_wrappers import generate as assess_level1_wrappers
    assessed_wrappers={r['address']:r for r in assess_level1_wrappers(docs.parent)['records']}
    assessed_slots={}
    slot_path=docs/'stage9/actor-selector54-slot-assessment.json'
    if slot_path.exists():
        slot_report=json.loads(slot_path.read_text())
        if slot_report['rom_sha256']!=ROM_HASH:raise ValueError('Slot assessment ROM mismatch')
        for record in slot_report['records']:
            if data[record['address']:record['address']+4].hex()!=record['original_bytes']:raise ValueError('Slot instruction bytes changed')
            assessed_slots[record['address']]=record
    reviewed_actor_operations={}
    remaining_path=docs/'stage9/remaining-level1-actor-assessment.json'
    if remaining_path.exists():
        remaining=json.loads(remaining_path.read_text())
        if remaining['rom_sha256']!=ROM_HASH:raise ValueError('Remaining actor ROM mismatch')
        for operation in remaining['operations']:
            for evidence_range in operation['code_ranges']:
                if data[evidence_range['start']:evidence_range['end_exclusive']].hex()!=evidence_range['bytes']:raise ValueError('Remaining actor bytes changed')
            reviewed_actor_operations[int(operation['entry'],16)]=operation

    for a in sorted(entries):

        pending=[a]; seen=set()

        while pending:

            v=pending.pop()

            if v in seen or v not in instructions or (v in entries and v!=a): continue

            seen.add(v); owners[v].add(a); pending.extend(edges[v])

        coverage=[item for item in ledger if any(int(lo,16)<=a<int(hi,16) for lo,hi in item.get('ranges',[]))]

        routines.append(dict(address=a,hex=f'{a:06X}',evidence=sorted(roots[a]),

            note=NOTES.get(a,''),instruction_count=len(seen),

            status='; '.join(item['status'] for item in coverage) or 'unassessed',

            subsystem='; '.join(item['name'] for item in coverage) or 'unassigned',

            native_sources=[p for item in coverage for p in item.get('native_sources',[])],blocks=sorted(seen)))

        linked=[row for row in contracts if int(row['address'],16)==a]

        roles=[]
        if any(a==slot['address'] for table in tables.values() for slot in table['slots']):roles.append('indexed branch slot candidate')
        if any('direct call' in note for note in roots[a]):roles.append('direct call entry')
        if any('main state pointer' in note for note in roots[a]):roles.append('main state entry')
        if any('callback' in note or 'definition' in note for note in roots[a]):roles.append('callback or definition candidate')
        routines[-1]['entry_roles']=roles or ['other recorded entry candidate']
        routines[-1]['contract_links']=linked

        if linked:

            from inventory_subsystems import CONTRACT_SUBSYSTEM

            groups=sorted({row.get('subsystem',CONTRACT_SUBSYSTEM.get(row['path'])) for row in linked} - {None})

            if groups:

                existing=[] if routines[-1]['subsystem']=='unassigned' else [routines[-1]['subsystem']]

                routines[-1]['subsystem']='; '.join(existing+groups)

            routines[-1]['native_sources']=sorted(set(routines[-1]['native_sources'])|{p for row in linked for p in row.get('native_sources',[])})

            routines[-1]['note']='; '.join(filter(None,[routines[-1]['note']]+[row['name'] for row in linked]))

            assessed=[row['status'] for row in linked if 'status' in row]

            if assessed:routines[-1]['status']='; '.join(assessed)

        if a in reviewed_actor_operations:
            operation=reviewed_actor_operations[a]
            routines[-1]['status']='partially assessed: '+operation['name']+'; caller/native/state closure pending'
            routines[-1]['subsystem']='Reviewed actor-state and phase candidates'
            routines[-1]['assessment_evidence']='remaining-level1-actor-assessment.json'
            routines[-1]['note']='; '.join(filter(None,[routines[-1]['note'],operation['contract'],operation['pending']]))
        for mapping,artifact in ((assessed_wrappers,'level1-wrapper-assessment.json'),(shared_slots,'shared-dispatch-slot-assessment.json'),(assessed_slots,'actor-selector54-slot-assessment.json')):
            if a in mapping:
                routines[-1]['status']=mapping[a]['status']
                routines[-1]['subsystem']=mapping[a]['subsystem']
                routines[-1]['assessment_evidence']=artifact
        if a==verified_inactive['address']:
            routines[-1].update(status=verified_inactive['status'],verification_status='verified',verification_evidence='inactive-actor-verification.json',native_sources=verified_inactive['native_sources'])
        if a in verified_leaf:
            record=verified_leaf[a]
            routines[-1].update(status=record['status'],verification_status='verified',verification_evidence=record['verification_evidence'],native_sources=record['native_sources'])

    calls=[dict(address=i['address'],source_owners=sorted(owners[i['address']]),

                target=i['target'],operands=i['operands'],resolved=i['target'] in instructions)

           for i in trace['instructions'] if i['flow']=='call']

    state_targets={a for a,evidence in roots.items() if any('main state pointer' in note for note in evidence)}

    for call in calls:

        a=call['address'];targets=[];evidence=''

        if call['target'] is not None:targets=[call['target']];evidence='direct encoded target'

        elif a in tables:

            targets=[s['address'] for s in tables[a]['slots']]+[s['target'] for s in tables[a]['slots']]+[s['address'] for s in tables[a].get('inline_targets',[])]

            evidence='candidate indexed slot entries and branch bodies, plus checked inline entries where recorded; selector bounds unproved'

        elif a in (0xa822,0xa83e,0xfcfa):targets=sorted(possible_callbacks);evidence='observed definition/runtime callback sources; computed aliases still require audit'

        elif a==0xb710:

            targets=sorted({d['field_22'] for d in definitions(data) if d['handler']==0xb702});evidence='B702 definition+22 pointer sources'

        elif a==0x1518:targets=sorted(state_targets);evidence='observed immediate main-state pointer writes'

        else:

            for context in contexts:

                if a in [int(s,16) for s in context['sites']]:

                    targets=[int(s,16) for s in context['targets']];evidence='documented caller-supplied continuation contexts'

        call.update(possible_targets=sorted(set(targets)),target_evidence=evidence or 'unresolved')

    for routine in routines:

        dependencies=sorted({target for call in calls if routine['address'] in call['source_owners']

                             for target in call['possible_targets']})

        routine['possible_dependencies']=dependencies

        routine['dependency_scope']='direct calls plus documented candidate indirect targets; not proof all targets execute'

        tags=[]

        for target,name in [(0x716e,'shared RNG'),(0x28b0,'object allocation'),(0x788ae,'sound request'),

                            (0x78808,'music selection'),(0xa75a,'asset decompression'),(0x4d54,'level camera'),

                            (0x8728,'terrain lookup'),(0x97ac,'selector/handler change')]:

            if target in dependencies:tags.append(name)

        routine['observed_services']=tags

    callback_writes=[dict(address=i['address'],operands=i['operands'],

                        status=('Immediate' if i['operands'].startswith('#') else 'Register/field-held')+' object+42 write candidate; aliases require context audit')

                     for i in trace['instructions'] if i['mnemonic']=='MOVE.L'

                     and re.fullmatch(r'.+,\(\+42,A[0-7]\)',i['operands'])]

    refs=defaultdict(set)

    for i in trace['instructions']:

        for a in i['references']: refs[a].add(i['address'])

    transfers=[dict(source=e['source'],destination=e['destination'],kind=e['kind'],

                    source_owners=sorted(owners[e['source']])) for e in trace['edges']

               if e['kind']!='call' and e['destination'] in entries

               and any(a!=e['destination'] for a in owners[e['source']])]

    for routine in routines:

        dependency_edges=[]

        for call in calls:

            if routine['address'] in call['source_owners']:

                dependency_edges.extend(dict(site=call['address'],target=target,kind='call',evidence=call['target_evidence']) for target in call['possible_targets'])

        for transfer in transfers:

            if routine['address'] in transfer['source_owners'] and routine['address']!=transfer['destination']:

                dependency_edges.append(dict(site=transfer['source'],target=transfer['destination'],kind=transfer['kind'],evidence='accepted non-call control-flow transfer between entry candidates'))

        for site in routine['blocks']:

            instruction=instructions[site]

            if instruction['flow']!='jump' or instruction['target'] is not None:continue

            if site in tables:

                targets=[s['address'] for s in tables[site]['slots']]+[s['address'] for s in tables[site].get('inline_targets',[])]

                evidence='candidate indexed jump entries; complete selector domain pending'

            else:

                context=next((c for c in contexts if site in [int(s,16) for s in c['sites']]),None)

                targets=[int(target,16) for target in context['targets']] if context else []

                evidence='checked continuation producer targets; complete caller/clobber audit pending'

            dependency_edges.extend(dict(site=site,target=target,kind='candidate indirect jump',evidence=evidence) for target in targets)

        for context in stack_contexts:

            site=int(context['producer'],16)

            if site in routine['blocks']:

                dependency_edges.append(dict(site=site,target=int(context['target'],16),kind='candidate stack return continuation',evidence=context['scope']))

        routine['dependency_edges']=sorted(dependency_edges,key=lambda e:(e['site'],e['target'],e['kind']))

        routine['possible_dependencies']=sorted({edge['target'] for edge in dependency_edges})

        routine['dependency_scope']='direct calls, accepted non-call entry transfers and candidate indirect call/jump targets; not proof all paths execute'

    for stop in trace['stops']:

        a=stop['address']

        context=next((c for c in contexts if a in [int(s,16) for s in c['sites']]),None)

        if context:
            stop['assessment']='Known context targets: '+', '.join('$'+s for s in context['targets'])+'; '+context['scope']+'; full context/clobber audit pending'
            if context.get('caller_audit_summary'):stop['assessment']+='; '+context['caller_audit_summary']

        elif a in tables: stop['assessment']='Candidate branch table catalogued; index bounds unproved'

        elif a==0x1518: stop['assessment']='Main RAM dispatcher; immediate C444 writes seeded; computed writes still require audit'

        elif a in (0xa822,0xa83e,0xfcfa): stop['assessment']='Object+42 callback; definition+12 and allocator override A8BC seeded; later callback writes require audit'

        elif a==0xb710: stop['assessment']='Definition+22 callback for B702 records seeded'

        elif a==0xb724: stop['assessment']='Restored definition+12 callback; ROM definitions and observed RAM definition handler seeded; alias and later definition writes need audit'

        elif a==0x1428: stop['assessment']='Manual return after RAM clearing; target popped into A0 at 1414'

        elif a==0xffc3cc: stop['assessment']='Relocated 102-byte routine, source 3152; self-modifying slot at source 3192'

        elif a==0x1042c: stop['assessment']='Historical player-selectors seed lies in held-out asset region; not accepted as code'

        else: stop['assessment']='Needs register/selector data-flow trace'

        linked=[contract for contract in contracts if int(contract['address'],16) in owners[a]]

        if linked:

            stop['contract_links']=linked

            stop['assessment']+='; related local contracts: '+', '.join(sorted({row['path'] for row in linked}))+' (global target/domain audit remains open)'



    return dict(rom_sha256=ROM_HASH,scope='Static reachable candidates, not proof of execution or complete code coverage',

        object_definitions=definitions(data),routines=routines,calls=calls,

        references=[dict(address=a,sites=sorted(v)) for a,v in sorted(refs.items())],

        dispatch_tables=list(tables.values()),

        sound_assets=sound_assets(data),

        inter_entry_transfers=transfers,

        coverage_ledger=ledger,

        indirect_contexts=contexts,

        indexed_inline_contexts=inline_contexts,

        stack_continuation_contexts=stack_contexts,

        object_field_references=object_fields(trace['instructions']),

        callback_writes=callback_writes,

        callback_sources=callback_sources,

        ram_references=[dict(address=a,sites=sorted(v)) for a,v in sorted(refs.items()) if 0xff0000<=a<=0xffffff],

        unresolved=trace['stops'],root_candidates=[dict(address=a,evidence=sorted(v)) for a,v in sorted(roots.items())],

        counts=dict(instructions=len(instructions),routines=len(routines),calls=len(calls),verified_routines=sum(r.get('verification_status')=='verified' for r in routines),

                    unresolved=len(trace['stops']),object_definitions=192,

                    distinct_object_handlers=len({d['handler'] for d in definitions(data)})),

        limit_reached=trace['limit_reached']),trace



def main():

    p=argparse.ArgumentParser(description=__doc__)

    p.add_argument('rom');p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1])

    args=p.parse_args(); out=args.project/'docs'/'stage9';out.mkdir(parents=True,exist_ok=True)

    result,trace=inventory(Path(args.rom).read_bytes(),args.project/'docs')

    (out/'inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

    (out/'reachable.asm').write_text(listing(trace),encoding='utf-8')

    for name,fields in [('routines',['hex','note','subsystem','instruction_count','status','native_sources','contract_links','observed_services','possible_dependencies','evidence']),

                        ('calls',['address','source_owners','target','operands','resolved','possible_targets','target_evidence']),

                        ('unresolved',['address','reason','assessment']),

                        ('object_definitions',['address','linked','handler','selector','animation_table']),

                        ('sound_assets',['kind','slot','pointer_address','source','status','decode_error'])]:

        with (out/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:

            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(result[name])

    for name,fields in [('object_field_references',['offset','address','mnemonic','operands','scope']),

                        ('ram_references',['address','sites']),('callback_writes',['address','operands','status'])]:

        with (out/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:

            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(result[name])

    print(json.dumps(result['counts']));print('instruction limit reached:',result['limit_reached'])

    payload=json.dumps(result).replace('<','\\u003c')

    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Rolo Stage 9 conversion inventory</title>

<style>body{font:16px system-ui;margin:24px;background:#151b23;color:#eef3fa}input,select{padding:10px;margin:8px;background:#263342;color:white;border:1px solid #718196}table{border-collapse:collapse;width:100%}td,th{padding:9px;border-bottom:1px solid #435164;text-align:left;vertical-align:top}code{color:#93d4ff}a{color:#93d4ff}#summary{padding:16px;background:#263342}small{color:#bbc7d5}</style>

<h1>Rolo: Stage 9 conversion inventory</h1><p>Static ROM evidence. Routine candidates are not completed ports. Selector bounds and execution reachability remain unverified.</p>

<p><a href="../STAGE9.md">Conversion roadmap</a> · <a href="actor-state-accesses.html">Actor state accesses</a> · <a href="sound-handoff.json">Sound handoff evidence</a> · <a href="spawn-inventory.csv">Spawn ledger</a> · <a href="research-worklist.csv">Research worklist</a> · <a href="state-inventory.json">Main states</a> · <a href="animation-command-spec.json">Animation command rules</a></p><div id="summary"></div><label>View <select id="view"><option>routines</option><option>calls</option><option>object_definitions</option><option>unresolved</option><option>dispatch_tables</option><option>sound_assets</option><option>coverage_ledger</option></select></label>

<label>Search <input id="q" placeholder="Address, note, evidence"></label><p id="count"></p><table><thead id="head"></thead><tbody id="rows"></tbody></table>

<script>const data=PAYLOAD;const $=id=>document.getElementById(id);const hex=n=>n==null?'indirect':'$'+n.toString(16).toUpperCase().padStart(6,'0');

const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

$('summary').textContent=Object.entries(data.counts).map(([k,v])=>k.replaceAll('_',' ')+': '+v).join(' · ');

function render(){let type=$('view').value;let fields={routines:['address','entry_roles','note','subsystem','instruction_count','status','native_sources','contract_links','observed_services','possible_dependencies','evidence'],calls:['address','source_owners','target','operands','resolved','possible_targets','target_evidence'],object_definitions:['address','linked','handler','selector','animation_table'],unresolved:['address','reason','assessment'],dispatch_tables:['dispatch','base','status','slots'],sound_assets:['kind','slot','source','status','decode_error'],coverage_ledger:['name','ranges','status','native_sources','next']}[type];let query=$('q').value.toLowerCase();let records=data[type].filter(r=>JSON.stringify(r).toLowerCase().includes(query)||fields.some(k=>typeof r[k]==='number'&&hex(r[k]).toLowerCase().includes(query)));$('count').textContent=records.length+' matching records';$('head').innerHTML='<tr>'+fields.map(k=>'<th>'+esc(k.replaceAll('_',' '))+'</th>').join('')+'</tr>';$('rows').innerHTML=records.map(r=>'<tr>'+fields.map(k=>{let v=r[k];if(['address','target','linked','handler','animation_table','dispatch','base','source'].includes(k))v=hex(v);else if(['source_owners','possible_targets','possible_dependencies'].includes(k))v=v.map(hex).join(', ');else if(k==='contract_links')v=v.map(c=>c.name+' ['+c.path+']: '+c.scope).join('; ');else if(k==='ranges')v=v.map(pair=>'$'+pair.join('..$')).join('; ');else if(Array.isArray(v))v=typeof v[0]==='object'?v.map(s=>hex(s.address)+' → '+hex(s.target)).join('; '):v.join('; ');return '<td>'+esc(v??'')+'</td>'}).join('')+'</tr>').join('')};$('q').oninput=render;$('view').onchange=render;render();</script></html>'''

    (out/'inventory.html').write_text(page.replace('PAYLOAD',payload),encoding='utf-8')
    if (args.project/'assets/extracted/all-levels/manifest.json').exists():
        from refresh_all_level_coverage import refresh
        refresh(args.project)



if __name__=='__main__': main()

