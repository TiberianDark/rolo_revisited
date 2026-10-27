"""Reviewed branch slots, never interpreted as independent gameplay routines."""
import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN

# table, stride, count, dispatcher, reviewed selector expression
TABLES=[
 (0x1f6c,4,6,0x1e44,'Six companion-menu branch slots. Selector producer and menu state closure remain open.'),
 (0xba72,4,11,0xba64,'Zero-extended actor BYTE50 multiplied by four. Legal phase range is not yet closed.'),
 (0xca48,2,8,0xca0a,'Signed WORD D0 arithmetic shift right three, then doubled; low three bits separately select vector offset. D1 selects pointer table. Input domains remain open.'),
 (0xe390,4,4,0xe342,'Zero-extended actor BYTE46 multiplied by four, reached after status, collision and selector70 gates. Legal phase range remains open.'),
 (0xe83a,2,9,0xe7be,'Zero-extended actor BYTE46 doubled, after integration, signed world clamps, timer and F270 gate. Legal phase range remains open.'),
 (0xea84,4,5,None,'Five contiguous word-displacement BRA slots. Producer and legal selector range require further caller tracing.'),
 (0xf054,4,3,0xf046,'Actor WORD46 used as signed indexed displacement, after clearing actor118 bit3. Legal offsets remain open.'),
 (0xf1a2,4,3,0xf194,'Actor WORD46 used as signed indexed displacement, after clearing actor118 bit3. Legal offsets remain open.'),
]

def generate(p):
 rom=(p/'local/rolo.md').read_bytes()
 assert hashlib.sha256(rom).hexdigest()==PIN
 records=[]
 for table,stride,count,dispatcher,selector in TABLES:
  for n in range(count):
   a=table+n*stride;i=Decoder(rom,a).decode()
   assert i['mnemonic']=='BRA' and i['size']==stride and i['flow']=='jump'
   records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=a+stride,
    original_bytes=rom[a:a+stride].hex(),instruction_evidence=[i],
    table=table,slot=n,dispatcher=dispatcher,target=i['target'],
    selector_contract=selector,subsystem='Shared actor dispatch branch slots',
    status='partially assessed: reviewed dispatch branch slot; selector and handler closure pending',
    scope='Exact branch bytes and target reviewed; not an independently returning routine, native verification or proof of Level 1 reachability.'))
 return dict(rom_sha256=PIN,records=records,scope='Static branch-table assessment; no ROM execution.')

if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=generate(p)
 (p/'docs/stage9/shared-dispatch-slot-assessment.json').write_text(json.dumps(r,indent=2)+'\n')
 print(f"Reviewed {len(r['records'])} branch slots; selector/handler closure remains partial.")
