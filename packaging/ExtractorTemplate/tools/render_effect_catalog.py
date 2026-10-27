"""Render all original effect envelopes through the same native engine as SDL."""
from pathlib import Path
import json,math,subprocess,hashlib,html

def main():
    p=Path(__file__).resolve().parents[1];audio=p/'assets/extracted/audio'
    bank=json.loads((audio/'bank.json').read_text());out=audio/'effects';out.mkdir(exist_ok=True)
    labels={13:'Jump',84:'Bunny jump',23:'Suction action',56:'Spit action',15:'Menu / scored pickup',
            27:'Companion container release',32:'Slope impact',64:'Pickup / jigsaw reward'}
    tracks=[]
    for effect in bank['effects']:
        sound_id=effect['id'];data=bytes.fromhex(effect['payload_hex']);ticks=0
        for at in range(2,23,2):
            if not data[at]:break
            ticks+=data[at]
        seconds=math.ceil(ticks/60)+1;file=out/f'effect-{sound_id:02d}.wav'
        result=subprocess.run([str(p/'build-suction/rolo_audio_render.exe'),'--effect',str(sound_id),str(file),str(seconds)],capture_output=True,text=True)
        tracks.append(dict(id=sound_id,label=labels.get(sound_id,'Original effect'),frames=ticks,
                           file='effects/'+file.name,passed=result.returncode==0,
                           result=(result.stdout+result.stderr).strip(),
                           sha256=hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None))
    report=dict(effects=91,passed=sum(t['passed'] for t in tracks),tracks=tracks,
                scope='Native original FM envelopes; not a reference audio comparison or guarantee every gameplay trigger is reached.')
    (audio/'effect-catalog.json').write_text(json.dumps(report,indent=2)+'\n')
    page=['<!doctype html><meta charset="utf-8"><title>Rolo sound effects</title>',
          '<style>body{font:16px system-ui;background:#101923;color:#e5edf6;max-width:1000px;margin:32px auto;padding:16px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #405369;padding:9px;text-align:left}a{color:#79c7ff}audio{height:32px}</style>',
          '<h1>Rolo: 91 original sound effects</h1>',
          '<p>Original 23-byte effect descriptors, pitch envelopes and FM instruments. Uses the live demo sound engine. Gameplay and companion-menu sound commands are connected. Percussion/sample paths and reference listening comparisons remain separate.</p>',
          '<table><tr><th>ID</th><th>Known use</th><th>Envelope</th><th>Listen</th></tr>']
    for t in tracks:
        page.append(f'<tr><td>{t["id"]}</td><td>{html.escape(t["label"])}</td><td>{t["frames"]} frames</td><td><audio controls preload="none" src="{t["file"]}"></audio> <a href="{t["file"]}">WAV</a>{"" if t["passed"] else " — review required"}</td></tr>')
    page.append('</table>');(audio/'effect-catalog.html').write_text('\n'.join(page),encoding='utf-8')
    print(f'{report["passed"]}/91 full effect renders passed; effect-catalog.html/json saved.')
    if report['passed']!=91:raise SystemExit(1)

if __name__=='__main__':main()
