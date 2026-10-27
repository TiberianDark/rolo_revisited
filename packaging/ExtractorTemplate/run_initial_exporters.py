import subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); py=sys.executable;rom=root/'local/rolo.md'
commands=[['export_first_enemy.py',str(rom)],['export_actor_patterns.py'],['export_enemy_preview_assets.py']]
for cmd in commands:
 name=cmd[0];r=subprocess.run([py,str(root/'tools'/name),*cmd[1:]],cwd=root,text=True,capture_output=True)
 print(f'### {name} exit={r.returncode}')
 print((r.stdout+r.stderr)[-3500:])
 if r.returncode: raise SystemExit(r.returncode)
