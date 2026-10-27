#pragma once
#include <array>
#include <algorithm>
#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
namespace rolo {
// Host diagnostics only: never used as a gameplay clock or to discard updates.
class FrameTimingLog {
public:
 enum Phase{Events,Simulation,Draw,Present,Wait,Count};
 struct Context{unsigned level{},actors{},textures{},alloc_failures{};int x{},y{};bool map{},paused{},menu{};};
private:
 std::ofstream out;std::uint64_t start{},last_end{},phase_start{},last_summary{},frame{},steps{},window_frames{},stalls{};
 std::array<double,Count> times{};Phase phase=Events;double maximum{};Context context{};
 static std::string stamp(){const auto now=std::chrono::system_clock::now();const auto t=std::chrono::system_clock::to_time_t(now);std::tm utc{};gmtime_s(&utc,&t);std::ostringstream s;s<<std::put_time(&utc,"%Y-%m-%dT%H:%M:%S")<<'.'<<std::setw(3)<<std::setfill('0')<<(std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count()%1000)<<'Z';return s.str();}
 void prefix(const char*kind){out<<stamp()<<'\t'<<kind<<"\tframe="<<frame;}
 void fields(){out<<"\tlevel="<<context.level<<"\tx="<<context.x<<"\ty="<<context.y<<"\tactors="<<context.actors<<"\ttextures="<<context.textures<<"\tallocation_failures="<<context.alloc_failures<<"\tmap="<<context.map<<"\tpaused="<<context.paused<<"\tmenu="<<context.menu;}
public:
 explicit FrameTimingLog(const std::filesystem::path&folder){try{std::filesystem::create_directories(folder);auto name=stamp();for(auto&c:name)if(c==':')c='-';static unsigned session=0;out.open(folder/("rolo-timing-"+name+"-"+std::to_string(++session)+".log"));if(out){out<<std::fixed<<std::setprecision(3);prefix("SESSION_START");out<<"\tstall_threshold_ms=50\theartbeat_seconds=5\tUTC_timestamps\n";out.flush();}}catch(...){/* Diagnostics must never prevent playing. */}}
 ~FrameTimingLog(){if(out){prefix("SESSION_END");out<<"\tstalls="<<stalls<<'\n';out.flush();}}
 void set_context(Context value){context=value;}
 void event(const char*name){if(out){prefix(name);fields();out<<'\n';}}
 void begin(std::uint64_t now){start=phase_start=now;phase=Events;times.fill(0);steps=0;++frame;++window_frames;if(!last_summary)last_summary=now;}
 void mark(Phase next,std::uint64_t now){times[phase]+=double(now-phase_start)/1e6;phase=next;phase_start=now;}
 void step(){++steps;}
 void end(std::uint64_t now){
  mark(Wait,now);const auto duration=double(now-start)/1e6;const auto gap=last_end&&start>=last_end?double(start-last_end)/1e6:0;last_end=now;maximum=std::max(maximum,duration+gap);
  if(!out)return;
  if(duration+gap>=50){++stalls;prefix("STALL");out<<"\tmonotonic_ms="<<double(now)/1e6<<"\ttotal_ms="<<duration<<"\toutside_frame_ms="<<gap<<"\tevents_ms="<<times[Events]<<"\tsimulation_ms="<<times[Simulation]<<"\tdraw_ms="<<times[Draw]<<"\tpresent_ms="<<times[Present]<<"\twait_ms="<<times[Wait]<<"\tupdates="<<steps;fields();out<<'\n';}
  if(now-last_summary>=5000000000ull){prefix("HEARTBEAT");out<<"\tmonotonic_ms="<<double(now)/1e6<<"\tframes_in_window="<<window_frames<<"\tmax_frame_ms="<<maximum<<"\tstalls="<<stalls;fields();out<<'\n';const auto before=std::chrono::steady_clock::now();out.flush();const auto flush_ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-before).count();if(flush_ms>=5){prefix("LOG_FLUSH_SLOW");out<<"\tms="<<flush_ms<<'\n';}last_summary=now;window_frames=0;maximum=0;}
 }
 class EventScope{
  FrameTimingLog&log;const char*name;std::chrono::steady_clock::time_point begun=std::chrono::steady_clock::now();
 public:EventScope(FrameTimingLog&l,const char*n):log(l),name(n){log.event(name);}~EventScope(){if(log.out){log.prefix("EVENT_END");log.out<<"\tevent="<<name<<"\tms="<<std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-begun).count()<<'\n';}}
 };
};
}
