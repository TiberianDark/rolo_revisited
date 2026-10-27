#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <shellapi.h>
#undef near
#undef far
#include "core/level1_transport_world.hpp"
#include "core/actor_palette_raster.hpp"
#include "core/forest_log_raster.hpp"
#include "assignment_check_data.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <set>
#include <memory>
using namespace rolo;
namespace fs=std::filesystem;
std::string escape(std::string s){std::string out;for(char c:s){if(c=='&')out+="&amp;";else if(c=='<')out+="&lt;";else if(c=='>')out+="&gt;";else out+=c;}return out;}
std::string jq(std::string s){std::string o="\"";for(unsigned char c:s){if(c=='\\'||c=='\"'){o+='\\';o+=c;}else if(c=='\n')o+="\\n";else if(c>=32)o+=c;}return o+'"';}
std::string sha(const fs::path&p){std::ifstream in(p,std::ios::binary);if(!in)return "MISSING";std::vector<unsigned char>b{std::istreambuf_iterator<char>(in),{}};unsigned char hash[32];BCRYPT_ALG_HANDLE a{};if(BCryptOpenAlgorithmProvider(&a,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)throw std::runtime_error("SHA256 unavailable");auto status=BCryptHash(a,nullptr,0,b.data(),ULONG(b.size()),hash,32);BCryptCloseAlgorithmProvider(a,0);if(status<0)throw std::runtime_error("SHA256 failed");std::ostringstream out;for(auto c:hash)out<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(c);return out.str();}
struct Row{unsigned level,offset,x,y;std::string status,note;};
struct Count{unsigned assigned{},missing{},blocked{},metadata{};};
int main(int argc,char**argv)try{
 bool automatic=argc>1&&std::string(argv[1])=="--no-pause";wchar_t exe[MAX_PATH];GetModuleFileNameW(nullptr,exe,MAX_PATH);const fs::path root=fs::path(exe).parent_path();const auto out=root/"docs/assignment-check";fs::create_directories(out);
 std::vector<std::string> stale;for(auto&p:assignment_data::pins)if(sha(root/fs::path(p.path))!=p.sha)stale.push_back(p.path);
 std::vector<Row> rows;std::array<Count,80> counts{};unsigned last_level=0;
 if(stale.empty())for(const auto&r:assignment_data::cases){
  if(last_level!=r.level){last_level=r.level;std::cout<<"Checking Level "<<last_level<<"..."<<std::endl;}
  Row row{r.level,r.offset,r.x,r.y,"BLOCKED",""};
  try{
   for(unsigned n=0;n<r.count;++n)if(std::none_of(Level1EnemySlice::definitions.begin(),Level1EnemySlice::definitions.end(),[&](auto&d){return d.key==r.chain[n];})){std::ostringstream msg;msg<<"Definition or linked part not exported: "<<std::hex<<r.chain[n];throw std::runtime_error(msg.str());}
   PlayerCheckpoint cp{std::uint16_t(r.x>96?r.x-96:0),std::uint16_t(r.y>48?r.y-48:0)};auto ptr=std::make_unique<Level1EnemySlice>(nullptr,0,3,r.level,&cp);auto&w=*ptr;Level1TransportWorld transport(w);
   TerrainMapView original{w.level_assets.map};if(original.word(r.offset)!=r.type||original.word(r.offset+2)!=r.x)throw std::runtime_error("Expected ledger differs from compiled original MAP");
   auto find=[&](){for(auto i=w.spawn_events.rbegin();i!=w.spawn_events.rend();++i)if(i->marker==w.map_identity+r.offset){auto&a=w.pool.resolve(i->actor);if(signed_word(a.word(0))>=0&&a.longword(88)==i->marker)return i->actor;}return 0u;};
   auto key=find();if(!key){w.macros.terrain_special_descriptor(original.record(r.offset),0);key=find();}
   const auto category=r.type>>8;
   if(category==17){row.status="METADATA";row.note="Original startup-selector marker; no sprite expected";}
   else if(category>=7&&category<=10){bool found=false;for(auto&t:transport.triggers.records)if(t.word(12)==std::uint16_t(w.map_identity+r.offset)&&t.byte(14)==category)found=true;row.status=found?"METADATA":"MISSING";row.note=found?"Trigger registered; activation behaviour untested":"Trigger not registered";}
   else if(!key){row.status="MISSING";row.note="Original marker did not create an active native object";}
   else{
    auto&actor=w.pool.resolve(key);if(r.root&&actor.longword(4)!=r.root){std::ostringstream msg;msg<<"Root identity needs review: expected "<<std::hex<<r.root<<", observed "<<actor.longword(4);throw std::runtime_error(msg.str());}
    w.list();w.animate();std::set<unsigned> seen;unsigned visual=0;bool verified_emitter=false;
    if(actor.longword(4)==0x15808){
     // Reviewed 118EC: this root has no Frame command; it emits 157E6.
     const auto*node=actor_animation_node(level1_object_animation_data::data,0x118ec);
     if(!node||node->op!=AnimationOp::SpawnRandom||node->frame!=0x157e6)throw std::runtime_error("Emitter spawn command differs from reviewed data");
     (void)w.definition(0x157e6);std::set<unsigned> previous;
     for(unsigned i=0;i<w.pool.actors.size();++i)if(signed_word(w.pool.actors[i].word(0))>=0)previous.insert(ActorPool::key(i));
     actor.word(72,0xffff);actor.longword(106,0);w.animate();w.list();w.animate();
     for(unsigned i=0;i<w.pool.actors.size();++i){auto&child=w.pool.actors[i];if(previous.count(ActorPool::key(i))||signed_word(child.word(0))<0||child.longword(4)!=0x157e6)continue;
      if(!child.longword(28)||!child.word(36)||!child.word(38))throw std::runtime_error("Emitter child has no published frame");
      std::vector<unsigned char> pixels(std::size_t(child.word(36))*child.word(38)*4);
      raster_actor_frame(child.longword(28),child.word(36),child.word(38),(w.definition(0x157e6).word(6)>>13)&3,w.palette,pixels);++visual;verified_emitter=true;
     }
     if(!verified_emitter)throw std::runtime_error("Invisible emitter failed to create its original animated child");
    }
    for(auto k=key;k;k=w.pool.resolve(k).longword(84)){
     if(!seen.insert(k).second||seen.size()>48)throw std::runtime_error("Invalid linked actor chain");auto&a=w.pool.resolve(k);auto&d=w.definition(a.longword(4));
     if(verified_emitter&&a.longword(4)==0x15808)continue;
     if(d.longword(18)){if(!a.longword(28)||!a.word(36)||!a.word(38))throw std::runtime_error("Animation has no published frame");std::vector<unsigned char> pixels(std::size_t(a.word(36))*a.word(38)*4);
      if(dynamic_platform_data::is_definition(a.longword(4)))raster_dynamic_macro(w.level_assets.terrain_bank(),a.longword(46),(d.word(6)>>13)&3,w.palette,pixels);
      else raster_actor_frame(a.longword(28),a.word(36),a.word(38),(d.word(6)>>13)&3,w.palette,pixels);++visual;
     }
    }
    for(unsigned n=0;n<4;++n){auto&a=w.pool.resolve(key);if(signed_word(a.word(0))<0||a.byte(116))break;w.invoke_actor_callback(key,a.longword(42));w.list();w.animate();}
    row.status="ASSIGNED";row.note=verified_emitter?"Invisible effect spawner: original child157E6 spawned and its frame rasterized; root correctly has no picture":"Root/linked definitions, native spawn and "+std::to_string(visual)+" rasterized frames; bounded callback check passed";
   }
  }catch(const std::exception&e){row.note=e.what();if(row.note.find("not exported")!=std::string::npos)row.status="MISSING";}
  auto&c=counts[row.level];if(row.status=="ASSIGNED")++c.assigned;else if(row.status=="METADATA")++c.metadata;else if(row.status=="MISSING")++c.missing;else ++c.blocked;rows.push_back(row);
 }
 std::ofstream html(out/"report.html"),json(out/"report.json"),csv(out/"issues.csv");if(!html||!json||!csv)throw std::runtime_error("Cannot write reports");
 html<<"<!doctype html><meta charset=utf-8><title>Rolo offline level assignments</title><style>body{background:#151719;color:#eee;font:16px system-ui;margin:30px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #555;padding:8px}.MISSING,.BLOCKED{background:#633}.ASSIGNED{background:#254d35}.METADATA{background:#33465a}summary{padding:10px;cursor:pointer}</style><h1>Rolo offline assignment check</h1><p>Build "<<__DATE__<<" "<<__TIME__<<". All 74 connected selectors, including side areas such as Level35. No network, AI or ROM instruction execution.</p><p><b>Assignment is not full gameplay fidelity.</b> Fresh fixtures near markers; original definition chains, spawn, published frames and four direct updates. Normal terrain, full animation branches, natural route activation, physics/timing and complete generated-object closure remain untested. Blocking or missing items never count as assigned.</p>";
 json<<"{\"schema\":1,\"gameplay_fidelity\":\"NOT TESTED\",\"stale_inputs\":[";for(unsigned n=0;n<stale.size();++n){if(n)json<<',';json<<jq(stale[n]);}json<<"],\"levels\":[";
 unsigned missing=0,blocked=0,assigned=0;bool comma=false;
 if(!stale.empty()){html<<"<h2>STALE / NOT RUN</h2><p>The game or its sources changed after this checker was built. Rebuild the checker; no prior result is reused.</p><ul>";for(auto&s:stale)html<<"<li>"<<escape(s)<<"</li>";html<<"</ul>";}
 else{
  html<<"<table><tr><th>Level</th><th>Objects assigned</th><th>Metadata</th><th>Missing</th><th>Blocked</th><th>Assignment %</th></tr>";
  for(auto level:all_native_level_data::selectors){const auto&c=counts[level];auto total=c.assigned+c.missing+c.blocked;html<<"<tr><td><a href=#level"<<level<<">"<<level<<"</a></td><td>"<<c.assigned<<'/'<<total<<"</td><td>"<<c.metadata<<"</td><td>"<<c.missing<<"</td><td>"<<c.blocked<<"</td><td>"<<(total?std::to_string(c.assigned*100/total):"N/A")<<"</td></tr>";if(comma)json<<',';comma=true;json<<"{\"selector\":"<<level<<",\"assigned\":"<<c.assigned<<",\"missing\":"<<c.missing<<",\"blocked\":"<<c.blocked<<",\"metadata\":"<<c.metadata<<'}';assigned+=c.assigned;missing+=c.missing;blocked+=c.blocked;}
  html<<"</table>";csv<<"level,offset,x,y,status,note\n";
  for(auto level:all_native_level_data::selectors){html<<"<details id=level"<<level<<"><summary>Level "<<level<<" - placement details</summary><table><tr><th>Offset</th><th>Location</th><th>Result</th><th>Evidence / issue</th></tr>";for(auto&r:rows)if(r.level==level){html<<"<tr class="<<r.status<<"><td>"<<r.offset<<"</td><td>"<<r.x<<','<<r.y<<"</td><td>"<<r.status<<"</td><td>"<<escape(r.note)<<"</td></tr>";if(r.status=="MISSING"||r.status=="BLOCKED")csv<<r.level<<','<<r.offset<<','<<r.x<<','<<r.y<<','<<r.status<<','<<jq(r.note)<<'\n';}html<<"</table></details>";}
 }
 json<<"],\"placements\":[";comma=false;for(auto&r:rows){if(comma)json<<',';comma=true;json<<"{\"level\":"<<r.level<<",\"offset\":"<<r.offset<<",\"x\":"<<r.x<<",\"y\":"<<r.y<<",\"status\":"<<jq(r.status)<<",\"note\":"<<jq(r.note)<<'}';}json<<"]}\n";html.close();json.close();csv.close();
 std::cout<<"Rolo offline checker: "<<assigned<<" assigned, "<<missing<<" missing, "<<blocked<<" blocked. "<<stale.size()<<" stale inputs.\nReport: "<<(out/"report.html").string()<<"\n";
 if(!automatic){ShellExecuteW(nullptr,L"open",(out/L"report.html").c_str(),nullptr,nullptr,SW_SHOWNORMAL);std::cout<<"Press Enter to close.";std::cin.get();}
 return !stale.empty()?2:(missing||blocked)?1:0;
}catch(const std::exception&e){std::cerr<<"Audit could not complete: "<<e.what()<<'\n';return 2;}


