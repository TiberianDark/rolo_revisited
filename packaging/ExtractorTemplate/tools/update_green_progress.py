"""Refresh local-contract progress graphic and checkpoint statistics only."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import date
today=date.today()
from inventory_level1_batch import catalogue
p=Path(__file__).resolve().parents[1];docs=p/'docs/stage9';batch=catalogue(p);(docs/'level1-current-candidates.json').write_text(json.dumps(batch,indent=2)+'\n',encoding='utf-8')
inv=json.loads((docs/'inventory.json').read_text(encoding='utf-8'));rows=inv['routines'];green=sum(r.get('verification_status')=='verified' for r in rows);ids=set(batch['candidate_addresses']);local=[r for r in rows if r['address'] in ids];lg=sum(r.get('verification_status')=='verified' for r in local)
report=dict(global_green=green,global_total=len(rows),global_percent=round(100*green/len(rows),1),level1_green=lg,level1_total=len(local),level1_percent=round(100*lg/len(local),1),scope='Scoped local native contracts, not whole-level or whole-game completion.')
platform_ids={0x1074,0x149e}
report['native_platform_substitutions']=sum(r['address'] in platform_ids and r.get('verification_status')=='verified' for r in rows)
report['payload_contracts']=green-report['native_platform_substitutions']
audio=[r for r in local if r.get('subsystem')=='68000 sound interface'];non_audio=[r for r in local if r not in audio]
report.update(level1_audio_total=len(audio),level1_audio_green=sum(r.get('verification_status')=='verified' for r in audio),level1_non_audio_total=len(non_audio),level1_non_audio_green=sum(r.get('verification_status')=='verified' for r in non_audio))
report['level1_non_audio_percent']=round(100*report['level1_non_audio_green']/len(non_audio),1)
report['denominator_correction']='The historical 434-candidate set includes 12 sound-interface routines; previous excluding-sound label was incorrect. Preserve historical totals and report sound separately.'
(docs/'green-progress-current.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
im=Image.new('RGB',(1100,560),'#111820');d=ImageDraw.Draw(im)
def txt(y,s,size=24,color='#ecf2f8'):d.text((25,y),s,font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',size),fill=color)
txt(18,f"Rolo native verification - {today:%d %B %Y}",30);txt(68,f'Whole inventory: {green}/{len(rows)} local greens ({report["global_percent"]}%)');txt(105,f'Level 1 conservative candidates: {lg}/{len(local)} ({report["level1_percent"]}%)')
txt(135,f"Includes {report['native_platform_substitutions']} reviewed native platform substitutions",17,'#b9c8d6')
for i,r in enumerate(rows):
 x=25+i%60*17;y=157+i//60*17;d.rectangle((x,y,x+13,y+13),fill='#36b768' if r.get('verification_status')=='verified' else '#b78137')
txt(390,f'Excluding sound: {report["level1_non_audio_green"]}/{report["level1_non_audio_total"]} ({report["level1_non_audio_percent"]}%) | sound interface: {report["level1_audio_green"]}/{len(audio)}',23,'#64d58a');txt(430,'Green = scoped payload or reviewed native platform substitution.',22);txt(478,'Not whole-game completion: integration, sound playback and fidelity remain pending.',20)
im.save(p.parent/('rolo-green-progress-'+today.isoformat()+'.png'));print(json.dumps(report))
