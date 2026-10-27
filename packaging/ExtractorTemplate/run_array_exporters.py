import subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); py=sys.executable
scripts=['export_audio_bank.py','export_cavern_tile_animation.py','export_desert_tile_animation.py','export_forest_tile_animation.py','export_world_tile_animation.py','export_ending_assets.py','export_forest_level_assets.py','export_level1_companion_menu.py','export_companion_presentation.py','export_level1_completion.py','export_level1_hud.py','export_level1_status_hud.py','export_palette_effects.py','export_world_routes.py','export_spawn_branch_tables.py','export_suction_particles.py','export_world_map_data.py']
for name in scripts:
 r=subprocess.run([py,str(root/'tools'/name)],cwd=root,text=True,capture_output=True)
 print(f'### {name} exit={r.returncode}')
 print((r.stdout+r.stderr)[-2500:])
 if r.returncode: raise SystemExit(r.returncode)
