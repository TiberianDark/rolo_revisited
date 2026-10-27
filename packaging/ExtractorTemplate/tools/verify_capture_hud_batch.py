"""Register reviewed capture/contact and HUD request batch; static ROM evidence only."""
import hashlib,json,re
from pathlib import Path
from m68k_static import Decoder
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
def span(a,e):
 at=a;instructions=[]
 while at<e:
  assert at in accepted,hex(at)
  i=Decoder(rom,at).decode();instructions.append(i);at+=i['size']
 assert at==e and instructions[-1]['mnemonic']=='RTS'
 return instructions
capture_result=root/'work/trigger-capture-results.json';capture=json.loads(capture_result.read_text(encoding='utf-8-sig'));assert capture=={'passed':True,'8FA4':524288,'989C':51200}
hud_result=root/'work/hud-request-batch-results.json';hud=json.loads(hud_result.read_text(encoding='utf-8-sig'));assert hud=={'passed':True,'5060':196912,'54A0':170496,'51D0':1,'7014':1}
template=(p/'src/core/status_hud_templates.hpp').read_text();template_values=bytes(int(x) for x in re.search(r'status_hud_templates\{([^}]+)\}',template).group(1).split(','));assert template_values==rom[0x5216:0x523e]
art=(p/'src/core/level1_hud_data.hpp').read_text()
for name,a,e in [('label',0x322e0,0x32360),('blank',0x32360,0x323a0),('icon',0x27bc0,0x27c00),('digits',0x27940,0x27bc0)]:
 values=[int(x) for x in re.search(name+r'\{\{(.*?)\}\};',art,re.S).group(1).split(',') if x.strip()];assert bytes(values)==rom[a:e]
reports=[('trigger-capture-verification.json','trigger_capture_verification_tests',capture_result,['src/core/player_trigger_capture.hpp','src/core/actor_state.hpp','tests/trigger_capture_verification_tests.cpp'],[
 (0x8fa4,0x8ff2,'Prior player containment','Unsigned prior-Y<=triggerbottom,wrappedpriortop>=wrappedtriggertop; ASR.Wwidthhalves, wrappedleft/right containment withunsignedBHI/BCS. ReturnboolmapsD6FFFF/0; noactormutation.',capture['8FA4']),
 (0x989c,0x9916,'Contact-triggered Rolo capture state','RequireC520zero,typeWORD4,8FA4true; optional84childBYTE46FF. C520FF,C521/C513zero,C526WORD6000,C524FF; controlled121from118bit3,58LONG40000,122FF,62LONG65E00,YWORDminus4retainsfraction,70WORD0.',capture['989C'])]),
 ('hud-request-batch-verification.json','hud_request_batch_verification_tests',hud_result,['src/core/status_hud_requests.hpp','src/core/status_hud_templates.hpp','src/core/rescue_hud_request.hpp','src/core/level1_hud.hpp','src/core/level1_hud_data.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/hud_request_batch_verification_tests.cpp'],[
 (0x5060,0x51d0,'Status HUD reservation and cached publication','Reserve5SATslots,copyoriginal40BYTEtemplates withincrementedlinkBYTEs. C523zero setsFFbefore51D0. Changedlives updatesC51F; negativeskipsglyphs,otherwise2digitrequests. Invoke719Aformatservice; publishonlychanged8digitBYTEs thenupdatecachedC532/C536. SignedpositiveC550thenC551 latchFF,sound37,iconrequests ordered.',hud['5060']),
 (0x51d0,0x5216,'Fixed HUD resource requests','Ordered2468(1602A,AC80,C0,40000000),2468(27BC0,AE00,20,40000000),26C8(0,AE40,63,40000000). Rawcountsrequests,notdevicecompletion.',hud['51D0']),
 (0x54a0,0x5680,'Rescue HUD allocation refresh and six publications','RejectsignedF26F<-1(128..254),orC552nonzero. NullC4D8 requests1476EatA00000/0,D4/D7zero;failure returns. SuccessstoresD0keyandmutatesreturnedA4:126bit4,48=2,50=50,36=56,38=16,28/8=5854524E,32/34zero. Existingactor50=50; negative48negatesBYTE,49zero,46WORDplus2. Sixorderedoriginalsource/destination/WORDcountrequests appendto consumer; termination/queuepacking external.',hud['54A0']),
 (0x7014,0x702c,'Display region clear request','26C8requestD0zero,D1LONG0D40,D2WORD07FF,D3LONG40000000thenreturn; no inventedextent orD400address.',hud['7014'])])]
for filename,exename,result_path,sources,specs in reports:
 exe=root/f'work/{exename}.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
 records=[]
 for a,e,name,contract,cases in specs:
  instructions=span(a,e)
  records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),verification_status='verified',status='verified green: local '+name,native_sources=[s for s in sources if s.startswith('src/')],instruction_evidence=instructions,checked_cases=cases,contract=contract,proof='Complete originalspansreviewed andbytepinned. Nativebatchcomparesfullactor/state snapshots, signed/unsigned/wrap branchpartitions, allfacingBYTEs, childaliases, allHUDlife/cacheBYTEpairs, everychanged-digitmask/rawBYTE, allkey/piecelatches, everyvalidSATbase, HUDgates/allocationfailure/reversal/resourceWORDwrap. Originaltemplate/artworkbytesindependentlymatched. Repeatedrescuepublicationsretainbothordered6requestsets.',scope='Declared nativeAPI/state/request contracts only. Capture usesvalidstableactoridentities with testedlinked aliases. HUDSATbase0..75,stabletemplates,buffers and rescuecount0..99; 719Ascoreformatting,28B0allocator,2468/26C8requestconsumers, rawC434queuepacking/IRQ/devicecompletion, caller/lifecycle/rawalias/CPUABI domains remainexternal. Helpersstandalone, notnewlivegameplaybindings orfullHUD/capturefeaturecertificates.'))
 report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest())
 (p/'docs/stage9'/filename).write_text(json.dumps(report,indent=2)+'\n')
print('Six capture/HUD local contracts evidence-pinned.')
