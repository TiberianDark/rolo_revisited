"""Refresh the current authored Level1 evidence batch and verify it, static only.

This orchestrates analysis utilities; it does not solve unassessed routines,
execute ROM instructions, build gameplay, or establish original-game fidelity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from inventory_rom import ROM_HASH


def refresh(rom_path):
    project=Path(__file__).resolve().parents[1]
    if hashlib.sha256(rom_path.read_bytes()).hexdigest()!=ROM_HASH:
        raise ValueError('Supplied ROM revision differs from the pinned project')
    directory=project/'docs/stage9'; completion=directory/'level1-batch-refresh.json'
    completion.unlink(missing_ok=True)
    plan=[('inventory_sprite_origin_reserved.py',[]),('inventory_sprite_frame.py',[]),('inventory_sprite_list_tail.py',[]),('inventory_player_frame_history.py',[]),('export_level1_indexed_background.py',[]),('audit_level1_actor_patterns.py',[]),('inventory_transport_fade_companions.py',[]),('inventory_level1_transport.py',[]),('inventory_loader_storage_display_reset.py',[]),('inventory_entry_marker_callback.py',[]),('inventory_level_entry_storage_reset.py',[]),('inventory_level_entry_services.py',[]),('inventory_player_startup.py',[]),('inventory_level1_collectibles.py',[]),
          ('inventory_level1_companion.py',[]),('inventory_level1_enemy_dependencies.py',[]),
          ('inventory_world_selection.py',[]),('inventory_world_pause_actor.py',[]),('inventory_world_bunny_domain.py',[]),('inventory_world_bunny_callers.py',[]),('export_palette_effects.py',[]),('inventory_interrupt_palette_clock.py',[]),('inventory_world_control.py',[]),('link_player_frame_contracts.py',[]),('inventory_rom.py',[str(rom_path)]),
          ('inventory_regional_interrupt_init.py',[]),('inventory_dispatch_domains.py',[str(rom_path)]),('inventory_level_restart.py',[]),('inventory_states.py',[str(rom_path)]),
          ('inventory_worklist.py',[]),('inventory_actor_contracts.py',[]),
          ('inventory_contract_index.py',[]),('inventory_level1_batch.py',[]),
          ('verify_inventory.py',[str(rom_path)])]
    plan.insert(0,('inventory_world_sprite_capacity.py',[]))
    plan.insert(0,('inventory_sorter_installation.py',[]))
    plan.insert(0,('inventory_live_sorter_words.py',[]))
    plan.insert(0,('inventory_scroll_mode_producers.py',[]))
    plan.insert(0,('inventory_word_transfer_queue.py',[]))
    plan.insert(0,('inventory_transporter_readiness.py',[]))
    plan.insert(0,('inventory_display_utilities.py',[]))
    plan.insert(0,('inventory_campaign_statistics.py',[]))
    plan.insert(0,('inventory_palette_resources.py',[]))
    plan.insert(0,('inventory_ending_sequence.py',[]))
    plan.insert(0,('inventory_scrolling_text.py',[]))
    plan.insert(0,('inventory_text_control.py',[]))
    plan.insert(0,('inventory_text_sources.py',[]))
    plan.insert(0,('inventory_scripted_player_exit.py',[]))
    plan.insert(0,('inventory_terrain_bank_domain.py',[]))
    plan.insert(0,('inventory_terrain_streaming.py',[]))
    plan.insert(0,('inventory_level_selector_writers.py',[]))
    plan.insert(0,('inventory_connected_actor_callbacks.py',[]))
    plan.insert(0,('inventory_player_collision_bindings.py',[]))
    plan.insert(0,('inventory_spawned_actor_callbacks.py',[]))
    plan.insert(next(i for i,item in enumerate(plan) if item[0]=='inventory_worklist.py'),('inventory_subsystems.py',[]))
    results=[]
    for index,(script,args) in enumerate(plan,1):
        print(f'{index}/{len(plan)}: {script}',flush=True)
        result=subprocess.run([sys.executable,str(project/'tools'/script),*args],
                              cwd=project,capture_output=True,text=True)
        if result.returncode:
            raise RuntimeError(f'{script} failed; no success marker saved.\n{result.stdout}\n{result.stderr}')
        results.append(dict(tool=script,sha256=hashlib.sha256((project/'tools'/script).read_bytes()).hexdigest(),exit_code=0))
    inventory=json.loads((directory/'inventory.json').read_text())
    work=json.loads((directory/'research-worklist.json').read_text())
    batch=json.loads((directory/'level1-batch.json').read_text())
    report=dict(rom_sha256=ROM_HASH,steps=results,batch_counts=batch['counts'],
        global_counts=inventory['counts'],research_counts=work['counts'],
        verification_sha256=hashlib.sha256((directory/'verification.json').read_bytes()).hexdigest(),
        scope='Authored static reports regenerated in dependency order and full inventory verification passed. Unknown tasks remain unsolved; no ROM execution or gameplay completion claimed.')
    completion.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['batch_counts']))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path)
    refresh(parser.parse_args().rom.resolve())
