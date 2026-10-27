"""Offline Level 1 asset/connection audit. Data inspection only; no ROM execution.
A structural pass is never a gameplay-fidelity pass. No compiler or internet needed.
"""
import argparse,hashlib,html,json,re,sys,subprocess,shutil
from collections import Counter
from pathlib import Path
ROM_HASH="9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9"

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def array(text,name):
 m=re.search(r"std::array<[^,>]+,\s*(\d+)>\s+"+re.escape(name)+r"\s*\{\{(.*?)\}\};",text,re.S)
 if not m:raise ValueError("Unsupported or missing native array: "+name)
 values=[int(v,0) for v in re.findall(r"0x[0-9a-fA-F]+|\b\d+\b",m[2])]
 if len(values)!=int(m[1]):raise ValueError("Native array size mismatch: "+name)
 return values

def records(data):
 def word(at):
  if at<0 or at+2>len(data):raise ValueError("MAP word outside file")
  return int.from_bytes(data[at:at+2],"big")
 if data[:3]!=b"MAP" or len(data)<10:raise ValueError("Invalid MAP signature/header")
 width,height=word(4),word(6)
 if not width or not height or height%16:raise ValueError("Invalid MAP dimensions")
 out=[];rows=height//16;minimum=8+(rows+1)*2
 previous=word(8)
 if previous<minimum:raise ValueError("MAP row table overlaps records")
 for row in range(rows):
  start,end=word(8+row*2),word(10+row*2)
  if start!=previous or end<start or end>len(data) or (end-start)%4:raise ValueError("Invalid MAP row extent")
  for at in range(start,end,4):out.append(dict(offset=at,x=word(at+2),y=row*16,type=word(at)))
  previous=end
 return out

def check_macro(index,macros,tiles,quads,bank,common):
 problems=[]
 if index>=len(macros):return ["Macro index outside native table"]
 w,h,start,count=macros[index]
 if not w or not h or w*h!=count or start+count>len(tiles):return ["Macro dimensions/tile extent mismatch"]
 for tile in tiles[start:start+count]:
  quad=tile&511
  if quad*4+4>len(quads):problems.append("Quad index outside artwork table: "+str(quad));continue
  for word in quads[quad*4:quad*4+4]:
   pattern=word&2047;limit=len(common)//32 if quad<28 else len(bank)//32
   if pattern>=limit:problems.append("Pattern outside "+("common" if quad<28 else "bank")+" artwork: "+str(pattern))
 return sorted(set(problems))

def native_inputs(p):
 pending=[p/"tests/level1_macro_audit.cpp"];seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f)
  for child in re.findall(r'#include "(core/[^"\n]+)"',f.read_text()):pending.append(p/"src"/child)
 return {str(f.relative_to(p)):digest(f) for f in sorted(seen)}

def native_check(p,run):
 evidence=p/"docs/stage9/level1-macro-native-evidence.json";pins=native_inputs(p)
 if evidence.exists():
  cached=json.loads(evidence.read_text())
  if cached.get("input_sha256")==pins:
   return dict(status="CURRENT",**cached)
 if not run:return dict(status="NOT RUN OR STALE",scope="Use --run-native to run the reviewed native viewport stress check.")
 shell=shutil.which("pwsh") or shutil.which("powershell")
 if not shell:return dict(status="BLOCKED",error="PowerShell not found; static checks remain available")
 proc=subprocess.run([shell,"-NoProfile","-File",str(p/"tools/run_level1_macro_native.ps1")],capture_output=True,text=True)
 resultfile=p/"local/macro-audit/result.json"
 if proc.returncode or not resultfile.exists():return dict(status="BLOCKED OR FAILED",error=(proc.stderr+proc.stdout)[-3000:])
 result=json.loads(resultfile.read_text(encoding="utf-8-sig"));proof=dict(input_sha256=pins,result=result,executable_sha256=digest(p/"local/macro-audit/level1_macro_audit.exe"),scope=result["scope"])
 evidence.write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
 return dict(status="CURRENT",**proof)

def render(report,path):
 esc=lambda v:html.escape(str(v));rows=[]
 for r in report["macros"]:
  where=", ".join(f'{v["layer"]} ({v["x"]},{v["y"]})' for v in r["occurrences"])
  rows.append("<tr><td>"+esc(r["macro"])+"</td><td>"+esc(r["dimensions_pixels"])+"</td><td>"+esc(r["data_check"])+"</td><td>"+esc(r["connection"])+"</td><td>"+esc(r["gameplay_check"])+"</td><td>"+esc(where)+"</td></tr>")
 marker_rows=[]
 for r in report["markers"]:marker_rows.append("<tr><td>"+esc(f'{r["type"]:04X}')+"</td><td>"+esc(f'({r["x"]},{r["y"]})')+"</td><td>"+esc(r["connection"])+"</td><td>"+esc(r["gameplay_check"])+"</td></tr>")
 path.write_text("<!doctype html><meta charset=utf-8><title>Level 1 offline macro audit</title><style>body{background:#101820;color:#eef3f7;font:16px system-ui;margin:28px}table{border-collapse:collapse;width:100%;margin:20px 0}td,th{border:1px solid #51606c;padding:8px;text-align:left}td:last-child{max-width:500px}p{max-width:1000px}.warn{color:#ffd078}h1{color:#78dca0}</style><h1>Level 1 offline macro audit</h1><p>"+esc(report["summary"])+"</p><p class=warn>Data checks and source connection checks only. Gameplay collision, moving platforms, rider behaviour, visual accuracy and original timing remain NOT TESTED by this audit. No routine greens are changed.</p><h2>Native loading/render check</h2><p>"+esc(report.get("native_loading_render_check",{}).get("status","NOT RUN"))+" - "+esc(report.get("native_loading_render_check",{}).get("result",{}).get("viewports",0))+" viewports. This does not test original images or gameplay behaviour.</p><h2>Failures and work remaining</h2><ul>"+"".join("<li>"+esc(v)+"</li>" for v in report["worklist"])+"</ul><h2>All macros used by Level 1</h2><table><tr><th>Macro</th><th>Pixels</th><th>Data</th><th>Connection evidence</th><th>Gameplay</th><th>Occurrences</th></tr>"+"".join(rows)+"</table><h2>All foreground object / control markers</h2><table><tr><th>Type</th><th>Position</th><th>Connection evidence</th><th>Gameplay</th></tr>"+"".join(marker_rows)+"</table><p>See level1-macro-audit-latest.json for input hashes, individual records and precise scope.</p>",encoding="utf-8")

def audit(p,force=False,run_native=False):
 out=p/"docs/stage9";latest=out/"level1-macro-audit-latest.json";page=out/"level1-macro-audit.html"
 level=p/"assets/extracted/all-levels/selector-01"
 inputs=[Path(__file__).resolve(),p/"local/rolo.md",level/"manifest.json",level/"markers.json",p/"src/core/level1_terrain_data.hpp",p/"src/core/level1_enemy_slice.hpp",p/"src/core/level1_object_data.hpp",p/"src/core/level1_world_data.hpp",p/"src/core/terrain_descriptor.hpp",p/"src/core/level1_transport_world.hpp",p/"src/core/level1_startup.hpp"]
 manifest=json.loads((level/"manifest.json").read_text())
 for layer in manifest["layers"].values():inputs.extend(p/layer[k]["path"] for k in ("binary","image"))
 inputs.append(p/manifest["palette"]["path"])
 native=native_check(p,run_native)
 hashes={str(f.relative_to(p)) if f.is_relative_to(p) else str(f):digest(f) for f in inputs}
 if not force and latest.exists():
  old=json.loads(latest.read_text())
  if old.get("input_sha256")==hashes and old.get("native_loading_render_check")==native:
   if not page.exists():render(old,page)
   print("Unchanged Level 1 inputs: previous audit reused. No gameplay tests rerun.");print(old["summary"]);return old
 failures=[]
 if digest(p/"local/rolo.md")!=ROM_HASH:raise ValueError("Supplied ROM revision does not match pinned SHA256")
 if manifest["rom_sha256"]!=ROM_HASH:raise ValueError("Extracted manifest ROM revision differs")
 for entry in [*[v[k]for v in manifest["layers"].values()for k in ("binary","image")],manifest["palette"]]:
  f=p/entry["path"]
  if digest(f)!=entry["sha256"] or f.stat().st_size!=entry["size"]:failures.append("Extraction pin mismatch: "+entry["path"])
 data=(p/"src/core/level1_terrain_data.hpp").read_text();tiles=array(data,"macro_tiles");quads=array(data,"quad_words");bank=array(data,"bank_patterns");common=array(data,"common_patterns")
 macros=[tuple(map(int,m))for m in re.findall(r"\{(\d+),(\d+),std::span<const std::uint16_t>\(macro_tiles\).subspan\((\d+),(\d+)\)\}",data)]
 if not macros:raise ValueError("Native macro table format requires review")
 foreground=(p/"src/core/level1_enemy_slice.hpp").read_text();descriptor=(p/"src/core/terrain_descriptor.hpp").read_text()
 routing_ok="if(record.type>=0x400)" in descriptor and "copy_normal_terrain_descriptor" in descriptor and "level1_terrain_data::macros.at(i)" in foreground
 definitions=set()
 for name in ("level1_object_data.hpp","level1_world_data.hpp"):
  definitions.update(int(v,0) for v in re.findall(r"ActorDefinition\{(0x[0-9a-fA-F]+|\d+),",(p/"src/core"/name).read_text()))
 obj=(p/"src/core/level1_object_data.hpp").read_text()
 tables={name:array(obj,name)for name in ("enemy_spawn_table","generic_spawn_table","collectible_spawn_table","companion_spawn_table")}
 locations={};markers=[];native_maps={"foreground":"map_bytes","background":"background_map_bytes"}
 for layer,metadata in manifest["layers"].items():
  raw=(p/metadata["binary"]["path"]).read_bytes();rr=records(raw)
  if bytes(array(data,native_maps[layer]))!=raw:failures.append("Native "+layer+" MAP differs from pinned extraction")
  for r in rr:
   if r["type"]<0x400:
    index=r["type"]&127;locations.setdefault(index,[]).append(dict(layer=layer,**r))
   elif layer=="foreground":markers.append(r)
 # Independently cross-check the exported special-marker list against actual MAP bytes.
 exported=json.loads((level/"markers.json").read_text())
 if {(r["record_offset"],r["type"],r["x"],r["y"]) for r in exported}!={(r["offset"],r["type"],r["x"],r["y"])for r in markers}:failures.append("Exported marker list differs from foreground MAP")
 macro_rows=[]
 for index,occurrences in sorted(locations.items()):
  errors=check_macro(index,macros,tiles,quads,bank,common)
  failures.extend("Macro "+str(index)+": "+v for v in errors)
  w,h,*_=macros[index] if index<len(macros) else (0,0,0,0)
  macro_rows.append(dict(macro=index,dimensions_pixels=[w*16,h*16],occurrences=occurrences,data_check="FAIL" if errors else "PASS (structure and artwork references)",errors=errors,connection="Normal terrain source route present; execution not checked" if routing_ok else "NEEDS REVIEW: normal terrain route changed",gameplay_check="NOT TESTED"))
 for r in markers:
  category,parameter=r["type"]>>8,r["type"]&255;key=None;connection="NEEDS REVIEW: marker role/connection"
  if category in (4,5,6,18):
   name={4:"enemy_spawn_table",5:"generic_spawn_table",6:"collectible_spawn_table",18:"companion_spawn_table"}[category];index=parameter//2 if category in (4,5) else parameter
   if index<len(tables[name]):key=tables[name][index]
   if key in definitions:connection="Definition present; source routing needs review" if any(t not in foreground for t in ("world.spawn_marker(r)","enemy_spawn_table","generic_spawn_table","(r.type>>8)==6","(r.type>>8)==0x12")) else "Definition and marker source route present; execution not checked"
   else:connection="MISSING: native definition/table binding";failures.append(f'Marker {r["type"]:04X} at {r["x"]},{r["y"]}: missing definition binding')
  elif category==8:connection="Transport source route present; execution not checked" if "if((record.type>>8)!=8)return false;"in (p/"src/core/level1_transport_world.hpp").read_text() else "NEEDS REVIEW: transport route changed"
  elif category==10 and parameter==4:
   original=(p/"local/rolo.md").read_bytes()
   for at,encoded in ((0x4684,"600001b8"),(0x483e,"024000ffd040d0407800740060000238"),(0x9302,"60000182"),(0x9486,"4e75")):
    if original[at:at+len(bytes.fromhex(encoded))].hex()!=encoded:raise ValueError("Class10 no-op trace pin mismatch")
   connection="RESOLVED: original slot4 is no-op; native trigger-list bookkeeping remains unbound"
  elif category==17:connection="Startup scan control marker; not a visible macro"
  elif 32<=category<=47:
   index=parameter;locations.setdefault(index,[]);connection="MISSING: dynamic macro/mode connection";failures.append(f'Dynamic macro {index}, mode {category-32}, at {r["x"]},{r["y"]} requires runtime audit')
  r.update(category=category,parameter=parameter,definition=key,connection=connection,gameplay_check="NOT TESTED")
 if native.get("status")=="CURRENT":
  observed=set(native["result"]["spawned_marker_offsets"]);pending=set(native["result"]["pending_marker_offsets"])
  for r in markers:r["native_loading_observation"]="SPAWN OBSERVED" if r["offset"] in observed else "PENDING MARKER OBSERVED" if r["offset"]in pending else "NOT OBSERVED AS ACTOR (may be control/transport)"
 groups=Counter(r["connection"] for r in markers);review=sum("NEEDS REVIEW"in r["connection"]for r in markers)
 summary=f'{len(macro_rows)} used terrain macros, {sum(len(r["occurrences"]) for r in macro_rows)} placements, {len(markers)} foreground markers. {len(failures)} detected failures; {review} marker roles need review. Gameplay fidelity: not tested.'
 if native.get("status")=="CURRENT" and not native["result"]["passed"]:failures.append("Native loading/render stress reported failures; see native evidence")
 worklist=list(failures)
 for role,count in groups.items():
  if "NEEDS REVIEW"in role:worklist.append(str(count)+" marker(s): "+role)
 if any(r["category"]==10 for r in markers):worklist.append("Class10 parameter4 has no original contact action (literal RTS); native trigger-list bookkeeping remains unbound. See level1-marker-0a04-review.json.")
 worklist.extend(["Run reviewed native placement/render/collision checks for each used macro; none are certified by this static audit.","Exercise object activation, movement modes and original-reference comparisons; source presence alone does not prove connection."])
 result=dict(native_loading_render_check=native,schema=1,selector=1,rom_sha256=ROM_HASH,input_sha256=hashes,summary=summary,scope="Offline structure/artwork-reference and bounded source-presence audit only. No native game execution, original-reference comparison or routine-green promotion.",failures=failures,worklist=worklist,macros=macro_rows,markers=markers,unused_macro_ids=[n for n in range(len(macros))if n not in locations],gameplay_status="NOT TESTED")
 latest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");render(result,page);print(summary);print(page);return result

def self_test():
 assert records(b"MAP\x01\x00\x20\x00\x10\x00\x0c\x00\x10\x00\x00\x00\x08")==[dict(offset=12,x=8,y=0,type=0)]
 try:records(b"MAP\x01\x00\x20\x00\x10\x00\x0c\x00\x12")
 except ValueError:pass
 else:raise AssertionError("Truncated MAP not rejected")
 assert check_macro(0,[(1,1,0,1)],[0],[0]*4,bytes(32),bytes(32))==[]
 assert check_macro(0,[(2,1,0,1)],[0],[0]*4,bytes(32),bytes(32))
 assert check_macro(0,[(1,1,0,1)],[4],[0]*4,bytes(32),bytes(32))
 assert check_macro(0,[(1,1,0,1)],[0],[1]*4,bytes(32),bytes(32))
 print("Six audit fixtures passed (valid data, malformed MAP, bad macro extent, quad and pattern references).")

if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--project",type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument("--force",action="store_true");a.add_argument("--run-native",action="store_true");a.add_argument("--self-test",action="store_true");args=a.parse_args()
 try:
  if args.self_test:self_test()
  else:
   result=audit(args.project.resolve(),args.force,args.run_native)
   sys.exit(1 if result["failures"] else 2 if args.run_native and result["native_loading_render_check"]["status"]!="CURRENT" else 0)
 except (OSError,ValueError,KeyError) as error:print("Audit could not complete: "+str(error),file=sys.stderr);sys.exit(2)
