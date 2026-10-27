"""Render each unique pinned music stream and publish original assignment index."""
from pathlib import Path
import hashlib,json,math,subprocess,html

def main():
    p=Path(__file__).resolve().parents[1];audio=p/'assets/extracted/audio'
    bank=json.loads((audio/'bank.json').read_text())
    assignments=json.loads((audio/'music-assignments.json').read_text())
    renderer=p/'build-suction/rolo_audio_render.exe'
    out=audio/'music';out.mkdir(exist_ok=True)
    unique={};tracks=[]
    for track in bank['music']:
        key=track['sha256']
        if key not in unique:
            trace=json.loads((audio/track['trace']).read_text())
            seconds=math.ceil(sum(e.get('delay_byte',0) for e in trace['records'])/60)+1
            destination=out/f"music-{track['id']:02d}.wav"
            result=subprocess.run([str(renderer),str(audio/track['file']),str(destination),str(seconds)],capture_output=True,text=True,check=True)
            unique[key]=dict(file='music/'+destination.name,seconds=seconds,
                             render=result.stdout.strip(),sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
        tracks.append(dict(id=track['id'],**unique[key]))
    report=dict(unique_tracks=len(unique),music_ids=33,tracks=tracks,
                status='Native FM music only; original instruments and sequence data. Effects/percussion pending. Loop-boundary timing provisional.',assignments=assignments)
    (audio/'music-catalog.json').write_text(json.dumps(report,indent=2)+'\n')
    page=['<!doctype html><meta charset="utf-8"><title>Rolo music catalogue</title>',
          '<style>body{font:16px system-ui;background:#101923;color:#e5edf6;max-width:1100px;margin:32px auto;padding:16px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #405369;padding:9px;text-align:left}a{color:#79c7ff}audio{height:32px}h2{margin-top:36px}</style>',
          '<h1>Rolo music: 33 IDs / 31 unique tracks</h1>',
          '<p>Original music extracted and assigned from ROM tables and native scene routines. FM playback is connected. Sound effects and percussion/sample paths remain unfinished. Exact loop-boundary timing and mix still require reference comparison.</p>',
          '<h2>Screen music</h2><table><tr><th>Screen</th><th>Music ID</th><th>Playback</th></tr>']
    for name,scene in assignments['scenes'].items():
        ids=scene['music'] if isinstance(scene['music'],list) else [scene['music']]
        page.append(f'<tr><td>{html.escape(name.replace("_"," "))}</td><td>{", ".join(map(str,ids))}</td><td>{"loop requested" if scene["loop"] else "single cue"}</td></tr>')
    page.append('</table><h2>Tracks</h2><table><tr><th>ID</th><th>Duration</th><th>Listen</th></tr>')
    for track in tracks:
        page.append(f'<tr><td>{track["id"]}</td><td>{track["seconds"]} s</td><td><audio controls preload="none" src="{track["file"]}"></audio> <a href="{track["file"]}">WAV</a></td></tr>')
    page.append('</table><h2>Level assignments</h2><p>The entry cue plays only when different from the preceding cue. Playlist slots advance across level entries; the tune is therefore not always fixed to a level number. A cue of “none” means no new entry cue, not a silent level.</p><table><tr><th>Selector</th><th>Entry cue</th><th>Delay at 60 Hz</th><th>Tune</th></tr>')
    for level in assignments['levels']:
        cue=level['entry_cue'];delay=level['cue_delay_frames']
        page.append(f'<tr><td>{level["selector"]}</td><td>{cue if cue is not None else "none"}</td><td>{str(delay)+" frames" if delay is not None else "next update"}</td><td>{level["tune"]}</td></tr>')
    page.append('</table><p>Playlist: '+', '.join(map(str,assignments['cycle']))+'. Revisited/reward branch replaces tunes 8/14 with 9.</p>')
    (audio/'music-catalog.html').write_text('\n'.join(page),encoding='utf-8')
    print(f'Rendered {len(unique)} unique tracks for 33 IDs; catalogue contains 80 selector assignments.')

if __name__=='__main__':main()
