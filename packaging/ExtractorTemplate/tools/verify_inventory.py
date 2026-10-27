"""Check inventory integrity and report coverage without claiming game fidelity."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH
from m68k_static import Decoder

def verify(project,rom):
    from inventory_spawned_actor_callbacks import catalogue as spawned_actor_callbacks_catalogue
    if spawned_actor_callbacks_catalogue(project)!=json.loads((project/'docs/stage9/spawned-actor-callback-contract.json').read_text()):
        raise ValueError('Spawned actor callback contracts do not reproduce')
    from inventory_player_collision_bindings import catalogue as player_collision_bindings_catalogue
    if player_collision_bindings_catalogue(project)!=json.loads((project/'docs/stage9/player-collision-binding-contract.json').read_text()):
        raise ValueError('Player collision binding contracts do not reproduce')
    from inventory_connected_actor_callbacks import catalogue as connected_actor_callbacks_catalogue
    if connected_actor_callbacks_catalogue(project)!=json.loads((project/'docs/stage9/connected-actor-callback-contract.json').read_text()):
        raise ValueError('Connected actor callback contracts do not reproduce')
    from inventory_level_selector_writers import catalogue as level_selector_writers_catalogue
    if level_selector_writers_catalogue(project)!=json.loads((project/'docs/stage9/level-selector-writer-contract.json').read_text()):
        raise ValueError('Level selector writer contract does not reproduce')
    from inventory_terrain_bank_domain import catalogue as terrain_bank_domain_catalogue
    if terrain_bank_domain_catalogue(project)!=json.loads((project/'docs/stage9/terrain-bank-domain-contract.json').read_text()):
        raise ValueError('Terrain bank domain does not reproduce')
    from inventory_scripted_player_exit import catalogue as scripted_player_exit_catalogue
    if scripted_player_exit_catalogue(project)!=json.loads((project/'docs/stage9/scripted-player-exit-contract.json').read_text()):
        raise ValueError('Scripted player exit contract does not reproduce')
    from inventory_text_sources import catalogue as text_sources_catalogue
    if text_sources_catalogue(project)!=json.loads((project/'docs/stage9/text-source-contract.json').read_text()):
        raise ValueError('Text source catalogue does not reproduce')
    from inventory_text_control import catalogue as text_control_catalogue
    if text_control_catalogue(project)!=json.loads((project/'docs/stage9/text-control-contract.json').read_text()):
        raise ValueError('Text control contract does not reproduce')
    from inventory_scrolling_text import catalogue as scrolling_text_catalogue
    if scrolling_text_catalogue(project)!=json.loads((project/'docs/stage9/scrolling-text-contract.json').read_text()):
        raise ValueError('Scrolling text contract does not reproduce')
    from inventory_ending_sequence import catalogue as ending_sequence_catalogue
    if ending_sequence_catalogue(project)!=json.loads((project/'docs/stage9/ending-sequence-contract.json').read_text()):
        raise ValueError('Ending sequence contract does not reproduce')
    from inventory_subsystems import catalogue as subsystem_catalogue
    if subsystem_catalogue(project)!=json.loads((project/'docs/stage9/subsystem-inventory.json').read_text()):
        raise ValueError('Subsystem inventory does not reproduce')
    from inventory_palette_resources import catalogue as palette_resources_catalogue
    if palette_resources_catalogue(project)!=json.loads((project/'docs/stage9/palette-resource-contract.json').read_text()):
        raise ValueError('Palette resource contract does not reproduce')
    from inventory_campaign_statistics import catalogue as campaign_statistics_catalogue
    if campaign_statistics_catalogue(project)!=json.loads((project/'docs/stage9/campaign-statistics-contract.json').read_text()):
        raise ValueError('Campaign statistic contract does not reproduce')
    from inventory_display_utilities import catalogue as display_utilities_catalogue
    if display_utilities_catalogue(project)!=json.loads((project/'docs/stage9/display-utility-contract.json').read_text()):
        raise ValueError('Display utility contract does not reproduce')
    from inventory_transporter_readiness import catalogue as transporter_readiness_catalogue
    if transporter_readiness_catalogue(project)!=json.loads((project/'docs/stage9/transporter-readiness-contract.json').read_text()):
        raise ValueError('Transporter readiness audit does not reproduce')
    from inventory_word_transfer_queue import catalogue as word_transfer_queue_catalogue
    if word_transfer_queue_catalogue(project)!=json.loads((project/'docs/stage9/word-transfer-queue-contract.json').read_text()):
        raise ValueError('Word transfer queue contract does not reproduce')
    from inventory_scroll_mode_producers import catalogue as scroll_mode_producers_catalogue
    if scroll_mode_producers_catalogue(project)!=json.loads((project/'docs/stage9/scroll-mode-producer-contract.json').read_text()):
        raise ValueError('Scroll mode producer contract does not reproduce')
    from inventory_live_sorter_words import catalogue as live_sorter_words_catalogue
    if live_sorter_words_catalogue(project)!=json.loads((project/'docs/stage9/live-sorter-word-contract.json').read_text()):
        raise ValueError('Live sorter word contract does not reproduce')
    from inventory_sorter_installation import catalogue as sorter_installation_catalogue
    if sorter_installation_catalogue(project)!=json.loads((project/'docs/stage9/sorter-installation-contract.json').read_text()):
        raise ValueError('Sorter installation contract does not reproduce')
    from inventory_world_sprite_capacity import catalogue as world_sprite_capacity_catalogue
    if world_sprite_capacity_catalogue(project)!=json.loads((project/'docs/stage9/world-sprite-capacity-contract.json').read_text()):
        raise ValueError('World sprite capacity contract does not reproduce')
    from inventory_sprite_origin_reserved import catalogue as sprite_origin_reserved_catalogue
    if sprite_origin_reserved_catalogue(project)!=json.loads((project/'docs/stage9/sprite-origin-reserved-contract.json').read_text()):
        raise ValueError('Sprite origin/reserved-count contract does not reproduce')
    from inventory_sprite_frame import catalogue as sprite_frame_catalogue
    if sprite_frame_catalogue(project)!=json.loads((project/'docs/stage9/sprite-frame-contract.json').read_text()):
        raise ValueError('Sprite frame contract does not reproduce')
    from inventory_sprite_list_tail import catalogue as sprite_list_tail_catalogue
    if sprite_list_tail_catalogue(project)!=json.loads((project/'docs/stage9/sprite-list-tail-contract.json').read_text()):
        raise ValueError('Sprite list/chunk tail contract does not reproduce')
    from export_level1_indexed_background import catalogue as indexed_background_catalogue
    if indexed_background_catalogue(project)!=json.loads((project/'docs/stage9/level1-indexed-background-export.json').read_text()):
        raise ValueError('Level1 indexed background does not reproduce')
    from audit_level1_actor_patterns import catalogue as level1_actor_patterns_catalogue
    actor_pattern_audit=level1_actor_patterns_catalogue(project)
    if actor_pattern_audit!=json.loads((project/'docs/stage9/level1-actor-pattern-audit.json').read_text()):
        raise ValueError('Level1 indexed actor artwork audit does not reproduce')
    if actor_pattern_audit['source_mismatches'] or actor_pattern_audit['missing_unique_frames'] or actor_pattern_audit['rgba_differences']:
        raise ValueError('Level1 indexed actor artwork differs from original assets')
    from inventory_transport_fade_companions import catalogue as transport_fade_companions_catalogue
    if transport_fade_companions_catalogue(project)!=json.loads((project/'docs/stage9/transport-fade-companion-contract.json').read_text()):
        raise ValueError('Transport fade/companion contract does not reproduce')
    from inventory_level1_transport import catalogue as level1_transport_catalogue
    if level1_transport_catalogue(project)!=json.loads((project/'docs/stage9/level1-transport-contract.json').read_text()):
        raise ValueError('Level1 transporter contract does not reproduce')
    from inventory_loader_storage_display_reset import catalogue as loader_storage_display_reset_catalogue
    if loader_storage_display_reset_catalogue(project)!=json.loads((project/'docs/stage9/loader-storage-display-reset-contract.json').read_text()):
        raise ValueError('Loader storage/display reset contract does not reproduce')
    from inventory_entry_marker_callback import catalogue as entry_marker_callback_catalogue
    if entry_marker_callback_catalogue(project)!=json.loads((project/'docs/stage9/entry-marker-callback-contract.json').read_text()):
        raise ValueError('Entry marker callback contract does not reproduce')
    from inventory_level_entry_storage_reset import catalogue as level_entry_storage_reset_catalogue
    if level_entry_storage_reset_catalogue(project)!=json.loads((project/'docs/stage9/level-entry-storage-reset-contract.json').read_text()):
        raise ValueError('Level entry storage reset contract does not reproduce')
    from inventory_level_entry_services import catalogue as level_entry_services_catalogue
    if level_entry_services_catalogue(project)!=json.loads((project/'docs/stage9/level-entry-services-contract.json').read_text()):
        raise ValueError('Level entry services contract does not reproduce')
    from inventory_regional_interrupt_init import catalogue as regional_interrupt_init_catalogue
    if regional_interrupt_init_catalogue(project)!=json.loads((project/'docs/stage9/regional-interrupt-init-contract.json').read_text()):
        raise ValueError('Regional interrupt initialization contract does not reproduce')
    from inventory_interrupt_palette_clock import catalogue as interrupt_palette_clock_catalogue
    if interrupt_palette_clock_catalogue(project)!=json.loads((project/'docs/stage9/interrupt-palette-clock-contract.json').read_text()):
        raise ValueError('Interrupt palette clock contract does not reproduce')
    from inventory_world_bunny_callers import catalogue as world_bunny_callers_catalogue
    if world_bunny_callers_catalogue(project)!=json.loads((project/'docs/stage9/world-bunny-caller-contract.json').read_text()):
        raise ValueError('World bunny caller contract does not reproduce')
    from inventory_world_bunny_domain import catalogue as world_bunny_domain_catalogue
    if world_bunny_domain_catalogue(project)!=json.loads((project/'docs/stage9/world-bunny-domain-contract.json').read_text()):
        raise ValueError('World bunny dispatch domain does not reproduce')
    from export_palette_effects import catalogue as palette_effect_catalogue
    if palette_effect_catalogue(project)!=json.loads((project/'docs/stage9/palette-effect-export.json').read_text()):
        raise ValueError('Palette effect data does not reproduce')
    from inventory_world_pause_actor import catalogue as world_pause_actor_catalogue
    if world_pause_actor_catalogue(project)!=json.loads((project/'docs/stage9/world-pause-actor-contract.json').read_text()):
        raise ValueError('World pause rabbit contract does not reproduce')
    from inventory_world_control import catalogue as world_control_catalogue
    if world_control_catalogue(project)!=json.loads((project/'docs/stage9/world-control-contract.json').read_text()):
        raise ValueError('World control contract is stale')
    from inventory_world_selection import catalogue as world_selection_catalogue
    if world_selection_catalogue(project)!=json.loads((project/'docs/stage9/world-selection-contract.json').read_text()):
        raise ValueError('World selection contract is stale')
    from inventory_level1_enemy_dependencies import verify as verify_enemy_dependencies
    verify_enemy_dependencies(project)
    from inventory_level1_companion import verify as verify_companion
    verify_companion(project)
    from inventory_level1_collectibles import verify as verify_collectibles
    verify_collectibles(project)
    from inventory_level1_batch import verify as verify_level1_batch
    verify_level1_batch(project)
    from inventory_player_startup import verify as verify_player_startup
    verify_player_startup(project)
    from inventory_level_restart import verify as verify_level_restart
    verify_level_restart(project)
    from inventory_injury_score import verify as verify_injury_score
    verify_injury_score(project)
    from inventory_spawn_placement import verify as verify_spawn_placement
    verify_spawn_placement(project)
    from export_level1_world import generate as generate_world_definitions
    if (project/'src/core/level1_world_data.hpp').read_text()!=generate_world_definitions(project):
        raise ValueError('Level1 world definitions are stale')
    from inventory_player_frame_history import catalogue as history_catalogue
    if json.loads((project/'docs/stage9/player-frame-history-contract.json').read_text(encoding='utf-8'))!=history_catalogue(project):
        raise ValueError('Player frame history evidence is stale')
    from export_level1_terrain import verify as verify_level1_terrain
    verify_level1_terrain(project)
    from inventory_terrain_streaming import catalogue as streaming_catalogue
    if json.loads((project/'docs/stage9/terrain-streaming-contract.json').read_text(encoding='utf-8'))!=streaming_catalogue(project):
        raise ValueError('Terrain streaming evidence is stale')
    from inventory_player_presentation import catalogue as presentation_catalogue
    from audit_actor_cursor import audit as cursor_audit
    for filename,current in (
        ('player-presentation-contract.json',presentation_catalogue(project)),
        ('actor-cursor-audit.json',cursor_audit(project))):
        if json.loads((project/'docs/stage9'/filename).read_text(encoding='utf-8'))!=current:
            raise ValueError('Stale presentation/cursor evidence: '+filename)
    from export_first_enemy import verify_export
    verify_export(rom,project)
    from inventory_first_enemy import catalogue as first_enemy_catalogue
    if json.loads((project/'docs/stage9/first-enemy-contract.json').read_text(encoding='utf-8'))!=first_enemy_catalogue(rom,project):
        raise ValueError('First enemy evidence is stale')
    from inventory_level_selectors import catalogue as level_selector_catalogue
    if json.loads((project/'docs/stage9/level-selector-domains.json').read_text(encoding='utf-8'))!=level_selector_catalogue(rom,project):
        raise ValueError('Level selector evidence is stale')
    from inventory_progress_domains import catalogue as progress_catalogue
    if json.loads((project/'docs/stage9/progress-selector-domains.json').read_text(encoding='utf-8'))!=progress_catalogue(rom,project):
        raise ValueError('Progress selector evidence is stale')
    from inventory_bulk_writes import catalogue as bulk_catalogue
    if json.loads((project/'docs/stage9/bulk-write-evidence.json').read_text(encoding='utf-8'))!=bulk_catalogue(rom,project):
        raise ValueError('Bulk writer evidence is stale')
    from inventory_menu_domain import catalogue as menu_catalogue
    if json.loads((project/'docs/stage9/menu-selector-domain.json').read_text(encoding='utf-8'))!=menu_catalogue(rom,project):
        raise ValueError('Menu selector evidence is stale')
    from inventory_contract_index import catalogue, render
    contract_directory=project/'docs/stage9'
    contract_index=catalogue(contract_directory)
    if json.loads((contract_directory/'contract-index.json').read_text(encoding='utf-8'))!=contract_index:
        raise ValueError('Contract index is stale')
    if (contract_directory/'contract-index.html').read_text(encoding='utf-8')!=render(contract_index):
        raise ValueError('Contract search page is stale')
    result,trace=inventory(rom,project/'docs')
    published=json.loads((project/'docs/stage9/inventory.json').read_text(encoding='utf-8'))
    if result!=published: raise ValueError('Published inventory is stale')
    occupied=set()
    for i in trace['instructions']:
        a,n=i['address'],i['size']
        if i['bytes']!=rom[a:a+n].hex(): raise ValueError('Instruction bytes differ from ROM')
        span=set(range(a,a+n))
        if occupied&span: raise ValueError('Instruction overlap')
        occupied.update(span)
    addresses={i['address'] for i in trace['instructions']}
    defs=result['object_definitions']; definition_addresses={d['address'] for d in defs}
    for d in defs:
        if d['handler'] not in addresses: raise ValueError('Definition handler not decoded')
        if d['linked'] and d['linked'] not in definition_addresses: raise ValueError('Linked definition outside table')
    for routine in result['routines']:
        if not set(routine['blocks'])<=addresses: raise ValueError('Invalid routine ownership')
        for contract in routine.get('contract_links',[]):
            target=(project/'docs/stage9'/contract['path']).resolve()
            if not target.is_relative_to((project/'docs/stage9').resolve()) or not target.is_file():
                raise ValueError('Missing or out-of-scope routine contract')
        for path in routine['native_sources']:
            if not (project/path).is_file(): raise ValueError('Missing native source '+path)
    for context in result['indirect_contexts']:
        producers=context.get('producers',[context.get('producer')])
        targets={int(a,16) for a in context['targets']}
        observed=set()
        for site in producers:
            i=Decoder(rom,int(site,16)).decode()
            if i['mnemonic']!='LEA' or not i['operands'].endswith(','+context['register']):
                raise ValueError('Incorrect continuation producer')
            observed.update(i['references'])
        if observed!=targets: raise ValueError('Continuation target mismatch')
        for site in context['sites']:
            i=Decoder(rom,int(site,16)).decode()
            if i['operands']!='('+context['register']+')' or i['flow']!=context.get('flow','jump'):
                raise ValueError('Incorrect indirect continuation site')
    for source in result['callback_sources']:
        i=Decoder(rom,int(source['producer'],16)).decode()
        if i['mnemonic']!='MOVE.L' or i['operands']!=('#$%08X,'%int(source['target'],16))+source['register']:
            raise ValueError('Register-held callback producer differs from ROM')
        write=Decoder(rom,int(source['write'],16)).decode()
        if not write['operands'].startswith(source['register']+',') or ',(+42,' not in write['operands']:
            raise ValueError('Register-held callback write differs from ROM')
        if 'call' in source:
            call=Decoder(rom,int(source['call'],16)).decode()
            if call['flow']!='call' or call['target']!=int(source['callee'],16):
                raise ValueError('Callback caller differs from ROM')
            if i['address']+i['size']!=call['address']:
                raise ValueError('Callback caller has unaccounted intervening instructions')
    commands=json.loads((project/'docs/stage9/animation-command-spec.json').read_text(encoding='utf-8'))
    if [c['command'] for c in commands]!=list(range(0,120,4)):raise ValueError('Animation command coverage differs')
    for command in commands:
        branch=Decoder(rom,0xfe28+command['command']).decode()
        if branch['target']!=int(command['handler'],16):raise ValueError('Animation command handler mismatch')
    music=[a for a in result['sound_assets'] if a['kind']=='music']
    if len(music)!=33 or any('decode_error' in a for a in music): raise ValueError('Music decode coverage differs')
    if result['limit_reached']: raise ValueError('Static walker stopped at instruction limit')
    catalog_path=project/'assets/extracted/catalog'
    catalog=json.loads((catalog_path/'manifest.json').read_text(encoding='utf-8'))
    if catalog['rom_sha256']!=ROM_HASH or catalog['unresolved']:raise ValueError('Incomplete or wrong asset catalogue')
    from inventory_terrain import catalogue as terrain_catalogue
    terrain=terrain_catalogue(rom,catalog)
    terrain_path=catalog_path/'terrain'
    if terrain!=json.loads((terrain_path/'manifest.json').read_text(encoding='utf-8')):
        raise ValueError('Terrain reference catalogue is stale')
    for site in terrain['evidence_sites']:
        if int(site,16) not in addresses:raise ValueError('Terrain evidence not at instruction boundary')
    terrain_artifacts=[terrain['shape_profiles'],terrain['common_quads']]+[bank['collision_prefix'] for bank in terrain['banks']]
    for artifact in terrain_artifacts:
        path=(terrain_path/artifact['path']).resolve()
        if not path.is_relative_to(terrain_path.resolve()):raise ValueError('Terrain artifact path escapes catalogue')
        payload=path.read_bytes()
        if len(payload)!=artifact['size'] or hashlib.sha256(payload).hexdigest()!=artifact['sha256']:
            raise ValueError('Terrain artifact differs')
    from inventory_spawns import catalogue as spawn_catalogue,SPAWN_HANDLERS
    spawns=spawn_catalogue(rom,catalog)
    if spawns!=json.loads((project/'docs/stage9/spawn-inventory.json').read_text(encoding='utf-8')):
        raise ValueError('Spawn ledger is stale')
    for index,target in enumerate(SPAWN_HANDLERS):
        branch=Decoder(rom,0x466c+index*4).decode()
        if branch['mnemonic']!='BRA' or branch['target']!=target:
            raise ValueError('Spawn class branch association differs from ROM')
    macro=json.loads((project/'docs/stage9/macro-dispatch.json').read_text(encoding='utf-8'))
    if any(int(site,16) not in addresses for site in macro['evidence_sites']):
        raise ValueError('Macro evidence not at instruction boundary')
    macro_rows=[row for row in spawns['markers'] if 'mode' in row]
    if macro['dispatch_path']['observed_initial_offsets']!=sorted({row['dispatch_offset'] for row in macro_rows}):
        raise ValueError('Macro initial selector domain differs')
    if macro['dispatch_path']['observed_macro_markers']!=len(macro_rows):
        raise ValueError('Macro marker count differs')
    for offset in range(0,128,4):
        branch=Decoder(rom,0xbe60+offset).decode()
        if branch['mnemonic']!='BRA' or branch['size']!=4 or branch['target'] not in addresses:
            raise ValueError('Macro branch slot differs')
    artifacts=[r['artifact'] for r in catalog['layouts']+catalog['music_sources']]
    artifacts.extend(row['palette_artifact'] for row in catalog['selectors'])
    for bank in catalog['graphics_banks']:
        artifacts.extend(bank[k] for k in ('artifact','macro_artifact') if k in bank)
    for artifact in artifacts:
        path=(catalog_path/artifact['path']).resolve()
        if not path.is_relative_to(catalog_path.resolve()):raise ValueError('Artifact path escapes catalogue')
        payload=path.read_bytes()
        if len(payload)!=artifact['size'] or hashlib.sha256(payload).hexdigest()!=artifact['sha256']:
            raise ValueError('Extracted asset differs from manifest')
    animations_path=catalog_path/'animations'
    animations=json.loads((animations_path/'manifest.json').read_text(encoding='utf-8'))
    from inventory_actor_contracts import catalogue as actor_catalogue
    actors=actor_catalogue(result,spawns,animations)
    if actors!=json.loads((project/'docs/stage9/actor-contracts.json').read_text(encoding='utf-8')):
        raise ValueError('Actor cross-reference catalogue is stale')
    for frame in animations['frames']:
        for variant in frame['variants']:
            path=(animations_path/variant['path']).resolve()
            if not path.is_relative_to(animations_path.resolve()):raise ValueError('Animation path escapes catalogue')
            data=path.read_bytes()
            if data!=rom[variant['source']:variant['source']+variant['size']] or hashlib.sha256(data).hexdigest()!=variant['sha256']:
                raise ValueError('Animation graphics differ from ROM')
    from z80_static import walk as z80_walk
    z80=json.loads((project/'docs/stage9/z80-driver.json').read_text(encoding='utf-8'))
    repeat=z80_walk(rom[0x7e7a0:0x7f8c0],z80['seeds'])
    if repeat['instructions']!=z80['instructions'] or repeat['stops']!=z80['stops']:
        raise ValueError('Z80 static listing is stale')
    handoff=json.loads((project/'docs/stage9/sound-handoff.json').read_text(encoding='utf-8'))
    for operation in handoff['operations']:
        if int(operation['entry'],16) not in addresses:
            raise ValueError('Sound operation entry not decoded')
        if any(int(site,16) not in addresses for site in operation['evidence']):
            raise ValueError('Sound handoff evidence not at instruction boundary')
    z80_addresses={i['address'] for i in z80['instructions']}
    for mailbox in handoff['driver_mailboxes']:
        if any(int(site,16) not in z80_addresses for site in mailbox['reads']+mailbox['writes']):
            raise ValueError('Sound mailbox evidence not at instruction boundary')
    from inventory_states import catalogue as state_catalogue
    state_report=state_catalogue(rom,project)
    if state_report!=json.loads((project/'docs/stage9/state-inventory.json').read_text(encoding='utf-8')):
        raise ValueError('Main state inventory is stale')
    from inventory_worklist import catalogue as worklist_catalogue
    worklist=worklist_catalogue(result,state_report)
    if worklist!=json.loads((project/'docs/stage9/research-worklist.json').read_text(encoding='utf-8')):
        raise ValueError('Research worklist is stale')
    from inventory_object_schema import catalogue as object_catalogue
    objects=object_catalogue(rom,project)
    if objects!=json.loads((project/'docs/stage9/object-schema.json').read_text(encoding='utf-8')):
        raise ValueError('Object storage inventory is stale')
    for pool in objects['pools']:
        if any(int(site,16) not in addresses for site in pool['evidence']):
            raise ValueError('Pool evidence not at instruction boundary')
        if pool['free_stack']+(pool['count']+1)*4>pool['base']:
            raise ValueError('Pool pointer stack overlaps resources')
    lifecycle=json.loads((project/'docs/stage9/object-lifecycle.json').read_text(encoding='utf-8'))
    for operation in lifecycle['operations']:
        if any(int(site,16) not in addresses for site in [operation['entry']]+operation['evidence']):
            raise ValueError('Lifecycle evidence not at instruction boundary')
    input_contract=json.loads((project/'docs/stage9/input-contract.json').read_text(encoding='utf-8'))
    for name in ('derived_update','hardware_poll','replay'):
        block=input_contract[name]
        if any(int(site,16) not in addresses for site in [block['entry']]+block['evidence']):
            raise ValueError('Input evidence not at instruction boundary')
    for button in input_contract['raw_button_bits']:
        write=Decoder(rom,int(button['write'],16)).decode()
        mapping=Decoder(rom,int(button['mapping_read'],16)).decode()
        field=button['field_offset']
        if write['mnemonic']!='MOVE.B' or write['operands']!='D2,(+%d,A1)'%field:
            raise ValueError('Button field write differs')
        if mapping['mnemonic']!='MOVE.B' or mapping['operands']!='(+%d,A2),D3'%field:
            raise ValueError('Button mapping lookup differs')
    selectors=json.loads((project/'docs/stage9/player-selector-contract.json').read_text(encoding='utf-8'))
    selector_range=[i for i in trace['instructions'] if 0x8934<=i['address']<0x8a0c]
    jump_sites={int(row['site'],16) for row in selectors['selector_exits']}
    if any(i['flow']=='call' or ('A2' in i['operands'] and i['address'] not in jump_sites) for i in selector_range):
        raise ValueError('Selector range can clobber continuation register')
    for exit in selectors['selector_exits']:
        producer=Decoder(rom,int(exit['producer'],16)).decode()
        jump=Decoder(rom,int(exit['site'],16)).decode()
        if producer['mnemonic']!='MOVEQ' or producer['operands']!='#%d,D2'%exit['selector']:
            raise ValueError('Selector result producer differs')
        if jump['mnemonic']!='JMP' or jump['operands']!='(A2)':
            raise ValueError('Selector continuation jump differs')
    if Decoder(rom,0x8852).decode()['target']!=0x8934:
        raise ValueError('Selector caller transfer differs')
    if Decoder(rom,0x884e).decode()['references']!=[0x8856]:
        raise ValueError('Selector continuation producer differs')
    from inventory_ram_schema import catalogue as ram_catalogue
    from inventory_animation_effects import catalogue as animation_effect_catalogue
    animation_effects=animation_effect_catalogue(rom,animations)
    if animation_effects!=json.loads((project/'docs/stage9/animation-effects.json').read_text(encoding='utf-8')):
        raise ValueError('Animation effect cross-reference is stale')
    if any(row['spawn_definition'] not in definition_addresses for row in animation_effects['controls'] if 'spawn_definition' in row):
        raise ValueError('Animation spawn points outside inspected definition table')
    ram_schema=ram_catalogue(rom,project)
    if ram_schema!=json.loads((project/'docs/stage9/ram-schema.json').read_text(encoding='utf-8')):
        raise ValueError('Explicit RAM schema is stale')
    from inventory_ram_aliases import catalogue as alias_catalogue
    aliases=alias_catalogue(rom,project)
    if aliases!=json.loads((project/'docs/stage9/ram-alias-hints.json').read_text(encoding='utf-8')):
        raise ValueError('RAM alias hints are stale')
    from inventory_dispatch_domains import catalogue as dispatch_domain_catalogue
    domains=dispatch_domain_catalogue(rom,project)
    if domains!=json.loads((project/'docs/stage9/dispatch-domains.json').read_text(encoding='utf-8')):
        raise ValueError('Dispatch domain catalogue is stale')
    from inventory_dynamic_macros import catalogue as dynamic_macro_catalogue
    dynamic_macros=dynamic_macro_catalogue(rom,catalog,spawns)
    if dynamic_macros!=json.loads((project/'docs/stage9/dynamic-macro-inventory.json').read_text(encoding='utf-8')):
        raise ValueError('Dynamic macro inventory is stale')
    if any(int(site,16) not in addresses for site in dynamic_macros['evidence_sites']):
        raise ValueError('Dynamic macro evidence boundary missing')
    mutations=json.loads((project/'docs/stage9/callback-mutation-contract.json').read_text(encoding='utf-8'))
    for operation in mutations['operations']:
        if any(int(site,16) not in addresses for site in operation['evidence']):
            raise ValueError('Callback mutation evidence is not on accepted instruction boundaries')
    if Decoder(rom,0x97ca).decode()['operands']!='A5/D2/D1,-(A7)' or Decoder(rom,0x97de).decode()['operands']!='(A7)+,D1/D2/A5':
        raise ValueError('Linked-handler argument preservation differs')
    marker=json.loads((project/'docs/stage9/marker-search-contract.json').read_text(encoding='utf-8'))
    for context in marker['caller_contexts']:
        producer=Decoder(rom,int(context['producer'],16)).decode()
        call=Decoder(rom,int(context['call'],16)).decode()
        if producer['references']!=[int(context['target'],16)] or not producer['operands'].endswith(',A4'):
            raise ValueError('Marker search callback producer differs')
        if producer['address']+producer['size']!=call['address'] or call['flow']!='call' or call['target']!=0x3e2c:
            raise ValueError('Marker callback call context differs')
    marker_handoff={0x3e66:('MOVEM.L','A6/A5/A4/A3/A2/A1/A0/D7/D6/D5/D4/D3/D2/D1/D0,-(A7)'),
                    0x3e7e:('JSR','(A4)'),0x3e80:('TST.W','D0'),
                    0x3e82:('MOVEM.L','(A7)+,D0/D1/D2/D3/D4/D5/D6/D7/A0/A1/A2/A3/A4/A5/A6')}
    for site,expected in marker_handoff.items():
        decoded=Decoder(rom,site).decode()
        if site not in addresses or (decoded['mnemonic'],decoded['operands'])!=expected:
            raise ValueError('Marker callback register/flag handoff differs')
    rng=json.loads((project/'docs/stage9/rng-contract.json').read_text(encoding='utf-8'))
    if any(int(site,16) not in addresses for site in rng['evidence']):
        raise ValueError('RNG evidence instruction boundary missing')
    rng_calls=[dict(site=f"{row['address']:X}",owners=[f'{owner:X}' for owner in row['source_owners']]) for row in result['calls'] if row['target']==0x716e]
    if rng_calls!=rng['observed_direct_calls']:
        raise ValueError('RNG caller evidence is stale')
    seed_refs=next(field['accesses'] for field in ram_schema['fields'] if field['address']==0xffc4be)
    if seed_refs!=rng['explicit_seed_accesses']:
        raise ValueError('RNG seed reference evidence is stale')
    scheduler=json.loads((project/'docs/stage9/actor-scheduler-contract.json').read_text(encoding='utf-8'))
    for operation in scheduler['operations']:
        if any(int(site,16) not in addresses for site in operation['evidence']):
            raise ValueError('Actor scheduler evidence is not on accepted boundaries')
    phase_save=Decoder(rom,0xfcf2).decode()
    phase_restore=Decoder(rom,0xfcfc).decode()
    if phase_save['operands']!='A6/A5/A4,-(A7)' or phase_restore['operands']!='(A7)+,A4/A5/A6':
        raise ValueError('Animation-phase definition/list preservation differs')
    motion=json.loads((project/'docs/stage9/shared-motion-contract.json').read_text(encoding='utf-8'))
    for operation in motion['operations']:
        if any(int(site,16) not in addresses for site in operation['evidence']):
            raise ValueError('Shared motion evidence is not on accepted boundaries')
    contacts=json.loads((project/'docs/stage9/actor-contact-contract.json').read_text(encoding='utf-8'))
    for operation in contacts['operations']:
        if any(int(site,16) not in addresses for site in operation['evidence']):
            raise ValueError('Actor contact evidence is not on accepted boundaries')
    if Decoder(rom,0x29f6).decode()['target']!=0x8e6c:
        raise ValueError('Contact retirement/lifetime scan ordering differs')
    ceiling=json.loads((project/'docs/stage9/ceiling-contact-contract.json').read_text(encoding='utf-8'))
    allowed_calls={int(a,16):int(b,16) for a,b in ceiling['allowed_calls'].items()}
    ranges=[(int(ceiling['entry'],16),int(ceiling['end_exclusive'],16))]
    ranges += [(int(r['start'],16),int(r['end_exclusive'],16)) for r in ceiling['preserved_register_ranges']]
    observed_calls={}
    producers={int(c['producer'],16):int(c['target'],16) for c in ceiling['continuations']}
    for lo,hi in ranges:
        cursor=lo
        while cursor<hi:
            if cursor not in addresses: raise ValueError('Ceiling contract instruction boundary missing')
            instruction=Decoder(rom,cursor).decode()
            if instruction['flow']=='call': observed_calls[cursor]=instruction['target']
            if 'A2' in instruction['operands']:
                if cursor in producers:
                    if instruction['mnemonic']!='LEA' or instruction['references']!=[producers[cursor]] or not instruction['operands'].endswith(',A2'):
                        raise ValueError('Ceiling continuation producer differs')
                elif cursor!=int(ceiling['indirect_site'],16) or instruction['mnemonic']!='JMP' or instruction['operands']!='(A2)':
                    raise ValueError('Unaccounted ceiling A2 reference')
            cursor+=instruction['size']
        if cursor!=hi: raise ValueError('Ceiling contract range ends inside instruction')
    if observed_calls!=allowed_calls: raise ValueError('Ceiling contract call closure differs')
    rider=json.loads((project/'docs/stage9/macro-rider-contract.json').read_text(encoding='utf-8'))
    if rider['rom_sha256']!=ROM_HASH:raise ValueError('Macro rider revision differs')
    for operation in rider['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Macro rider full-range instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Macro rider range incomplete')
    factory=json.loads((project/'docs/stage9/macro-factory-contract.json').read_text(encoding='utf-8'))
    if factory['rom_sha256']!=ROM_HASH:raise ValueError('Macro factory revision differs')
    for operation in factory['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Macro factory instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Macro factory range incomplete')
    contexts=json.loads((project/'docs/stage9/selector-contexts.json').read_text(encoding='utf-8'))['contexts']
    for context in contexts:
        for expected in context['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Selector writer context evidence differs')
    height=json.loads((project/'docs/stage9/replacement-height-contract.json').read_text(encoding='utf-8'))
    if height['rom_sha256']!=ROM_HASH:raise ValueError('Height callback ROM revision differs')
    for operation in height['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Height callback instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Height callback range incomplete')
    relocated=json.loads((project/'docs/stage9/relocated-operation-contract.json').read_text(encoding='utf-8'))
    if relocated['rom_sha256']!=ROM_HASH:raise ValueError('Relocation revision differs')
    if next(field['accesses'] for field in ram_schema['fields'] if field['address']==0xfff266)!=relocated['explicit_preexisting_count_accesses']:
        raise ValueError('Preexisting sprite count access evidence stale')
    if next(field['accesses'] for field in ram_schema['fields'] if field['address']==0xffc51c)!=relocated['explicit_variable_count_accesses']:
        raise ValueError('Variable sprite count access evidence stale')
    size_table=relocated['sprite_size_table'];size_start=int(size_table['address'],16)
    size_bytes=bytes.fromhex(size_table['bytes'])
    if rom[size_start:size_start+len(size_bytes)]!=size_bytes or hashlib.sha256(size_bytes).hexdigest()!=size_table['sha256']:
        raise ValueError('Sprite size table bytes differ')
    if [int.from_bytes(size_bytes[n:n+2],'big',signed=True) for n in range(0,len(size_bytes),2)]!=size_table['words']:
        raise ValueError('Sprite size table words differ')
    for operation in relocated['operations']:
        if 'source_start' in operation:
            start=int(operation['source_start'],16)
            if hashlib.sha256(rom[start:start+operation['source_length']]).hexdigest()!=operation['source_sha256']:
                raise ValueError('Relocated source bytes differ')
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Relocation instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Relocation range incomplete')
    from inventory_render_operations import catalogue as render_operation_catalogue
    render_operations=render_operation_catalogue(rom,project)
    if render_operations!=json.loads((project/'docs/stage9/initial-render-operations.json').read_text(encoding='utf-8')):
        raise ValueError('Initial render operations differ')
    copied_word=Decoder(rom,0x28ea).decode()
    if copied_word['mnemonic']!='MOVE.W' or copied_word['operands']!='(+8,A2),(+0,A3)':
        raise ValueError('Allocator operation-word provenance differs')
    from inventory_actor_state import catalogue as actor_state_catalogue
    actor_state=actor_state_catalogue(rom,project)
    if actor_state!=json.loads((project/'docs/stage9/actor-state-accesses.json').read_text(encoding='utf-8')):
        raise ValueError('Actor state field/byte-overlap inventory differs')
    startup=json.loads((project/'docs/stage9/startup-ram-clear-contract.json').read_text(encoding='utf-8'))
    if startup['rom_sha256']!=ROM_HASH:raise ValueError('Startup clear revision differs')
    for operation in startup['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Startup clear instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Startup clear range incomplete')
        calls=[dict(site=row['address'],target=row['target'],owners=row['source_owners']) for row in result['calls'] if row['target']==0x1414]
        if calls!=operation['known_direct_calls']:raise ValueError('Startup clear direct call contexts stale')
        caller=Decoder(rom,0x1064).decode()
        if caller['flow']!='call' or caller['target']!=0x1414 or 0x1064+caller['size']!=0x1068:
            raise ValueError('Startup clear canonical return context differs')
    spawn_factory=json.loads((project/'docs/stage9/spawn-factory-contract.json').read_text(encoding='utf-8'))
    if spawn_factory['rom_sha256']!=ROM_HASH:raise ValueError('Spawn factory revision differs')
    for operation in spawn_factory['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Spawn factory instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Spawn factory range incomplete')
    from inventory_spawn_domains import catalogue as spawn_domain_catalogue
    spawn_domains=spawn_domain_catalogue(rom,project)
    if spawn_domains!=json.loads((project/'docs/stage9/spawn-selector-domains.json').read_text(encoding='utf-8')):
        raise ValueError('Spawn selector domains differ')
    triggers=json.loads((project/'docs/stage9/trigger-action-contract.json').read_text(encoding='utf-8'))
    if triggers['rom_sha256']!=ROM_HASH:raise ValueError('Trigger action revision differs')
    for operation in triggers['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Trigger action instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Trigger action range incomplete')
    if rom[0x9472:0x9476].hex()!=triggers['phase_table']['bytes']:raise ValueError('Trigger phase bytes differ')
    disposal_calls=[dict(site=f"{c['address']:06X}",target=f"{c['target']:06X}",owners=c['source_owners']) for c in result['calls'] if c['target'] in (0x4adc,0x4af4)]
    if disposal_calls!=triggers['disposal_call_contexts']:raise ValueError('Trigger disposal call contexts stale')
    from inventory_continuation_paths import catalogue as continuation_path_catalogue
    continuation_paths=continuation_path_catalogue(rom,project)
    if continuation_paths!=json.loads((project/'docs/stage9/continuation-path-proofs.json').read_text(encoding='utf-8')):
        raise ValueError('Continuation path proofs differ')
    world_jigsaw=json.loads((project/'docs/stage9/world-jigsaw-contract.json').read_text(encoding='utf-8'))
    if world_jigsaw['rom_sha256']!=ROM_HASH:raise ValueError('Jigsaw contract revision differs')
    for operation in world_jigsaw['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Jigsaw contract instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Jigsaw contract range incomplete')
    from inventory_world_progression import catalogue as world_jigsaw_catalogue
    world_jigsaw_data=world_jigsaw_catalogue(rom,project)
    if world_jigsaw_data!=json.loads((project/'docs/stage9/world-jigsaw-data.json').read_text(encoding='utf-8')):
        raise ValueError('Jigsaw cell/edge data differs')
    responses=json.loads((project/'docs/stage9/shared-response-contract.json').read_text(encoding='utf-8'))
    if responses['rom_sha256']!=ROM_HASH:raise ValueError('Shared response revision differs')
    for operation in responses['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Shared response instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Shared response range incomplete')
        if [c for c in result['calls'] if c['target']==int(operation['entry'],16)]!=operation['known_direct_calls']:
            raise ValueError('Shared response direct caller catalogue stale')
    if spawn_domains['marker_class12_counts']!=json.loads((project/'docs/stage9/marker-class12-counts.json').read_text(encoding='utf-8')):
        raise ValueError('Marker class12 counts do not reproduce')
    from inventory_plane_extents import catalogue as plane_catalogue
    if plane_catalogue(rom,project)!=json.loads((project/'docs/stage9/level-plane-extents.json').read_text(encoding='utf-8')):
        raise ValueError('Level plane extents do not reproduce')
    from inventory_global_domains import catalogue as global_catalogue
    if global_catalogue(rom,project)!=json.loads((project/'docs/stage9/global-domain-evidence.json').read_text(encoding='utf-8')):
        raise ValueError('Global overlap evidence does not reproduce')
    from inventory_world_routes import catalogue as route_catalogue
    if route_catalogue(rom)!=json.loads((project/'docs/stage9/world-route-data.json').read_text(encoding='utf-8')):
        raise ValueError('World route data does not reproduce')
    vector=json.loads((project/'docs/stage9/vector-table-evidence.json').read_text(encoding='utf-8'))
    from inventory_vector_table import catalogue as vector_catalogue
    if vector!=vector_catalogue(rom,project):raise ValueError('Vector evidence does not reproduce')
    raw=rom[0x1582a:0x15c2a]
    words=[int.from_bytes(raw[i:i+2],'big',signed=True) for i in range(0,1024,2)]
    if vector['rom_sha256']!=ROM_HASH or vector['signed_words']!=words or vector['sha256']!=hashlib.sha256(raw).hexdigest():
        raise ValueError('Vector table evidence differs')
    if [c for c in result['calls'] if c['target']==0xccf8]!=[c['call'] for c in vector['caller_contexts']]:
        raise ValueError('Vector caller catalogue differs')
    for context in vector['caller_contexts']:
        for expected in context['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Vector caller evidence differs')
    transitions=json.loads((project/'docs/stage9/frame-transition-contract.json').read_text(encoding='utf-8'))
    if transitions['rom_sha256']!=ROM_HASH:raise ValueError('Frame transition revision differs')
    for operation in transitions['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Frame transition instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Frame transition range incomplete')
    descriptor=json.loads((project/'docs/stage9/map-descriptor-contract.json').read_text(encoding='utf-8'))
    if descriptor['rom_sha256']!=ROM_HASH:raise ValueError('Map descriptor revision differs')
    for operation in descriptor['operations']:
        cursor=int(operation['entry'],16)
        for expected in operation['instruction_evidence']:
            site=int(expected['address'],16);decoded=Decoder(rom,site).decode()
            if site!=cursor or site not in addresses or any(decoded[key]!=expected[key] for key in ('bytes','mnemonic','operands')):
                raise ValueError('Map descriptor instruction evidence differs')
            cursor+=decoded['size']
        if cursor!=int(operation['end_exclusive'],16):raise ValueError('Map descriptor range incomplete')
    for context in result.get('indexed_inline_contexts',[]):
        sites=[int(context[key],16) for key in ('dispatch','forwarding_entry','forwarding_call')]
        sites += [int(p[key],16) for p in context['producer_contexts'] for key in ('producer','call')]
        sites += [int(p['address'],16) for p in context['inline_targets']]
        if any(site not in addresses for site in sites):raise ValueError('Inline dispatch context not on accepted boundaries')
    for context in result.get('stack_continuation_contexts',[]):
        if any(int(context[key],16) not in addresses for key in ('producer','target')):
            raise ValueError('Stack continuation context not on accepted boundaries')
    inline_dispatch=next(r for r in result['routines'] if r['address']==0xa66e)
    if not {0xa672,0xa674,0xa676,0xa678}<=set(inline_dispatch['possible_dependencies']):
        raise ValueError('Jigsaw dependency graph loses branch/inline entries')
    stack_dispatch=next(r for r in result['routines'] if r['address']==0x9642)
    if 0x966a not in stack_dispatch['possible_dependencies']:raise ValueError('Manual stack-return dependency lost')
    from inventory_selector_writes import catalogue as selector_catalogue
    selectors=selector_catalogue(rom,project)
    if selectors!=json.loads((project/'docs/stage9/selector-accesses.json').read_text(encoding='utf-8')):
        raise ValueError('Selector alias inventory differs')
    from inventory_macro_handlers import catalogue as macro_handler_catalogue
    macro_handlers=macro_handler_catalogue(rom,project)
    if macro_handlers!=json.loads((project/'docs/stage9/macro-handler-inventory.json').read_text(encoding='utf-8')):
        raise ValueError('Macro handler inventory is stale')
    if any(field['site'] not in addresses for mode in macro_handlers['modes'] for field in mode['field_access_candidates']):
        raise ValueError('Macro handler field evidence boundary missing')
    return dict(rom_sha256=ROM_HASH,counts=result['counts'],instruction_bytes=len(occupied),
        indexed_dispatch_tables=len(result['dispatch_tables']),
        unique_stop_sites=len({s['address'] for s in result['unresolved']}),
        unassessed_entries=sum(r['status']=='unassessed' for r in result['routines']),
        music_slots=len(music),distinct_music_sources=len({a['source'] for a in music}),
        sound_effect_slots=91,published_inventory_reproduces=True,instruction_bytes_and_no_overlap=True,
        z80_counts=z80['counts'],asset_counts=catalog['counts'],verified_asset_artifacts=len(artifacts),
        animation_counts=animations['counts'],animation_command_handlers_verified=30,
        sound_handoff_evidence_boundaries_verified=True,
        state_inventory_reproduces=True,state_counts=state_report['counts'],
        research_worklist_reproduces=True,research_worklist_counts=worklist['counts'],
        spawn_ledger_reproduces=True,macro_dispatch_evidence_verified=True,
        object_schema_reproduces=True,object_schema_counts=objects['counts'],
        lifecycle_evidence_boundaries_verified=True,lifecycle_operations=len(lifecycle['operations']),
        input_contract_evidence_verified=True,
        player_selector_context_verified=True,player_selector_exit_sites=len(jump_sites),
        ceiling_continuation_context_verified=True,routine_contract_links_exist=True,
        ram_schema_reproduces=True,ram_schema_counts=ram_schema['counts'],
        ram_alias_hints_reproduce=True,ram_alias_counts=aliases['counts'],
        animation_effects_reproduce=True,animation_effect_counts=animation_effects['counts'],
        dispatch_domains_reproduce=True,dispatch_domain_counts=domains['counts'],
        actor_state_accesses_reproduce=True,actor_state_counts=actor_state['counts'],
        selector_accesses_reproduce=True,selector_access_counts=selectors['counts'],
        spawn_factory_full_instruction_ranges_verified=True,
        spawn_factory_operations=len(spawn_factory['operations']),
        spawn_selector_domains_reproduce=True,spawn_selector_counts=spawn_domains['counts'],
        trigger_action_full_instruction_ranges_verified=True,trigger_action_operations=len(triggers['operations']),
        continuation_path_proofs_reproduce=True,continuation_path_counts=continuation_paths['counts'],
        world_jigsaw_contract_ranges_verified=True,world_jigsaw_operations=len(world_jigsaw['operations']),
        world_jigsaw_data_reproduce=True,world_jigsaw_counts=world_jigsaw_data['counts'],
        shared_response_contract_ranges_verified=True,shared_response_operations=len(responses['operations']),
        frame_transition_contract_ranges_verified=True,frame_transition_operations=len(transitions['operations']),
        indexed_inline_context_boundaries_verified=True,stack_continuation_boundaries_verified=True,
        non_call_dependency_contexts_verified=True,
        macro_factory_full_instruction_range_verified=True,
        macro_rider_full_instruction_range_verified=True,
        macro_handlers_reproduce=True,macro_handler_counts=macro_handlers['counts'],
        dynamic_macros_reproduce=True,dynamic_macro_counts=dynamic_macros['counts'],
        callback_mutation_evidence_boundaries_verified=True,callback_mutation_operations=len(mutations['operations']),
        marker_search_context_verified=True,
        rng_call_and_seed_evidence_verified=True,
        actor_scheduler_evidence_boundaries_verified=True,
        shared_motion_evidence_boundaries_verified=True,shared_motion_operations=len(motion['operations']),
        actor_contact_evidence_boundaries_verified=True,actor_contact_operations=len(contacts['operations']),
        terrain_catalogue_reproduces=True,terrain_counts=terrain['counts'],
        actor_contracts_reproduce=True,actor_contract_counts=actors['counts'],
        definition_links_and_handler_targets=True,native_source_links_exist=True,
        scope='Integrity of static inventory only; no runtime execution or original-game comparison',
        complete_rom_mapping=False,full_native_gameplay_ported=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=verify(a.project,Path(a.rom).read_bytes())
    (a.project/'docs/stage9/verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
