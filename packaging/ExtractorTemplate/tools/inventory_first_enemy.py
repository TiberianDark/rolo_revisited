"""Pin the first class04 body routine and its translated shared motion ranges."""
import argparse
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH


def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs');accepted={i['address']:i for i in trace['instructions']}
    specs=[(0xb566,0xb702,'body_link_attack_state_machine','src/core/first_enemy.hpp'),
           (0xcd8e,0xcde4,'shared_magnitude_gravity','src/core/actor_motion.hpp'),
           (0xcfce,0xcffc,'shared_position_integration','src/core/actor_motion.hpp'),
           (0xd042,0xd05a,'integer_x_step_preserving_fractions','src/core/actor_motion.hpp'),
           (0x9012,0x90a0,'player_contact_mixed_word_predicates','src/core/actor_contact.hpp'),
           (0x96c6,0x97ac,'player_contact_damage_and_alternate_action','src/core/actor_contact.hpp'),
           (0x97ac,0x97fe,'hit_counter_zero_animation_and_secondary_spawn','src/core/actor_defeat.hpp'),
           (0x8eaa,0x8f74,'object_list_contact_and_unsigned_overlap','src/core/actor_object_contact.hpp'),
           (0xcf46,0xcfce,'two_probe_floor_landing','src/core/actor_terrain.hpp'),
           (0xd168,0xd1ca,'terrain_and_world_boundary_direction','src/core/actor_terrain.hpp'),
           (0x8680,0x86d6,'floor_shape_query','src/core/actor_terrain.hpp'),
           (0x8728,0x87bc,'ring_lookup_classification_and_floor_descriptor','src/core/actor_terrain.hpp'),
           (0xfeae,0xfebc,'animation_retirement_flags','src/core/actor_animation_effects.hpp'),
           (0x1014c,0x1015a,'animation_sound_request_and_continue','src/core/animation.hpp'),
           (0xfd44,0xfe0a,'actor_sequence_counter_descriptor_and_graphics_fields','src/core/actor_animation.hpp'),
           (0xfea0,0xfeae,'actor_animation_jump_and_preceding_word_repeat','src/core/actor_animation.hpp'),
           (0xffcc,0xffee,'actor_animation_hold_and_saved_return','src/core/actor_animation.hpp'),
           (0x28d8,0x29c0,'selective_actor_initialization_after_resource_allocation','src/core/actor_initialization.hpp'),
           (0x27f0,0x2816,'actor_free_stack_initialization','src/core/actor_allocation.hpp'),
           (0x28b0,0x29ee,'definition_chain_allocation_and_partial_failure','src/core/actor_allocation.hpp'),
           (0x34c2,0x34f0,'graphics_span_allocation_and_return_flags','src/core/actor_allocation.hpp'),
           (0xef68,0xefa8,'generated_score_effect_single_award_wave_and_retirement','src/core/score_effect.hpp'),
           (0xa84c,0xa84e,'inactive_actor_callback_literal_return','src/core/actor_defeat.hpp'),
           (0x3478,0x34c2,'graphics_span_pool_initialization_and_reserved_word_shift','src/core/graphics_pool.hpp'),
           (0x34f0,0x355a,'ordered_graphics_span_release_and_merging','src/core/graphics_pool.hpp'),
           (0x2cbc,0x2d1a,'actor_disposal_links_resources_and_free_stack','src/core/actor_disposal.hpp'),
           (0x2860,0x2888,'deferred_marker_pool_initialization','src/core/actor_markers.hpp'),
           (0x2bce,0x2c4c,'immediate_or_deferred_spawn_marker_restoration','src/core/actor_markers.hpp'),
           (0x2c4c,0x2cbc,'deferred_marker_list_with_literal_lower_x_clobber','src/core/actor_markers.hpp'),
           (0x2ad8,0x2bce,'actor_lifetime_gates_and_saved_spawn_far_bounds','src/core/actor_lifetime.hpp'),
           (0x29ee,0x2ad8,'live_pool_order_active_list_and_visibility','src/core/actor_active_list.hpp'),
           (0x2888,0x28b0,'eight_node_reservation_pool_initialization','src/core/actor_reservations.hpp'),
           (0x8e3a,0x8e6c,'actor_reservation_prepend_duplicate_and_capacity_gates','src/core/actor_reservations.hpp'),
           (0x8e6c,0x8eaa,'reservation_cleanup_old_bit_and_ordered_recycling','src/core/actor_reservations.hpp'),
           (0xc9ae,0xca0a,'priority_actor_list_and_alias_mutation','src/core/actor_scheduler.hpp'),
           (0xa808,0xa84c,'live_priority_then_active_callback_dispatch','src/core/actor_scheduler.hpp')]
    operations=[]
    for start,end,name,source in specs:
        cursor=start;evidence=[]
        while cursor<end:
            i=accepted[cursor];evidence.append(i);cursor+=i['size']
        if cursor!=end:raise ValueError('Enemy range ends inside an instruction')
        if not (project/source).is_file():raise ValueError('Native translation source missing')
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,
            native_source=source,instruction_evidence=evidence,
            known_direct_calls=[c for c in inv['calls'] if start<=c['address']<end]))
    definition=next(d for d in inv['object_definitions'] if d['address']==0x13f98)
    linked=next(d for d in inv['object_definitions'] if d['address']==definition['linked'])
    score=next(d for d in inv['object_definitions'] if d['address']==definition['secondary_definition'])
    if definition['handler']!=0xb566:raise ValueError('First class04 handler differs')
    if score['handler']!=0xef68 or score['secondary_definition']!=100:raise ValueError('Generated score definition differs')
    return dict(rom_sha256=ROM_HASH,body_definition=definition,linked_definition=linked,
        generated_score_definition=score,
        definition_field28_roles=[
            dict(definition='013F98',consumer='97AC',role='Definition key140EC for a generated score object on this caller path'),
            dict(definition='0140EC',consumer='EF68->997E',role='Numeric score100, not a definition pointer on this caller path')],
        initial_outer_animation_gates=[
            dict(definition='013F98',definition_byte7=rom[0x13f98+7],parent_link=False,definition_byte26=rom[0x13f98+26]),
            dict(definition='013FBA',definition_byte7=rom[0x13fba+7],parent_link=True,definition_byte26=rom[0x13fba+26]),
            dict(definition='0140EC',definition_byte7=rom[0x140ec+7],parent_link=False,definition_byte26=rom[0x140ec+26])],
        outer_animation_gate_scope='At documented initial allocations all three definitions have byte7.5 clear, so FCF6 does not call an extra update. Body/score have no parent; linked definition26.6 is set, so FD18 parent-copy is skipped. Later definition/link mutations and other families still need closure.',
        marker_positions=[[672,752,0],[1744,752,1]],operations=operations,
        native_scope='Bounded shared-world SDL integration connects first-family marker spawning, native motion/contact/injury/defeat, streamed terrain collision, animation, score/life arithmetic, lifetime/disposal and deferred-marker services. Three immutable body/link/score definitions and eight programs are exported. Fullframe/transition/companion/HUD/queue/audio bindings, allruntimecaller/mutation/capacitydomains and originalreference verification remain incomplete. See injury-score-contract and FIRST-ENEMY-INTEGRATION scope; not a complete playable1:1 level.',
        pending=['Object-list root/link ownership, low-word actor identities and special-type defeat return domains',
            'Native combat adapter uses sharedcontrolledactor/global updates andsoundcommandword; audio playback/fullconsumerqueue pending',
            'Terrain ring streaming/updates, F268/F330 producers, collision extents and definition26 domains',
            'F264 reserved-pattern producer domains,25-node span capacity/links, definition/RAM-pool mutation and release caller domains, native5998 diagnostics and original-reference allocation/release cases',
            'Outer animation callback/parent-copy processing; eight body/link/score programs and local actor animation fields translated',
            '997E score/extra-life arithmetic andEF68 lifecycle nowbound ininitialnativeworld; originalHUD, reset/resumedscore/tableoffsetmutations andwrappedthresholddomains remainpending',
            'Active-list bounds/scheduling and source-marker producer/alias domains; local restoration/lifetime/disposal helpers translated, original-reference multi-removal clobber and scan ordering pending',
            'All helper register/data preservation assumptions and link/controlled pointer mutations',
            'Original-reference behavior, graphics and sound comparisons'],
        scheduler_scope='Native priority/active traversal assumes callbacks preserve the original A6 list cursor. Callback register-clobber domains, global world binding and independent frame comparisons remain unclosed. Native function lookup must never execute a ROM callback key.',
        complete_mapping=False,complete_playable_enemy=False,original_reference_verified=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    report=catalogue(args.rom.read_bytes(),args.project)
    (args.project/'docs/stage9/first-enemy-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(dict(operations=len(report['operations']),body_handler='B566',playable=False))


if __name__=='__main__':main()
