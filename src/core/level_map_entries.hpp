#pragma once
#include "core/backward_asset_codec.hpp"
#include <algorithm>
#include "core/actor_state.hpp"
#include "core/terrain_display.hpp"
namespace rolo {
struct LevelMapEntryState{std::uint16_t selector=0;std::uint8_t foreground_bank=0,bank_override=0,background_bank=0,reward=0;std::uint32_t cache=0;std::uint16_t checkpoint_x=0,checkpoint_y=0;ActorState*controlled=nullptr;};
struct LevelMapEntryServices{virtual ~LevelMapEntryServices()=default;virtual void special_background(std::uint32_t,std::span<std::uint8_t>)=0;virtual void prepare_planes(ActorState&,ActorState&)=0;virtual void camera(LevelMapEntryState&)=0;virtual void startup_allocate(std::uint32_t,std::uint32_t)=0;};
inline std::uint16_t map_entry_word(std::span<const std::uint8_t>b,std::size_t at){if(at+1>=b.size())throw std::out_of_range("MAP read");return std::uint16_t((b[at]<<8)|b[at+1]);}
inline std::uint32_t map_entry_long(std::span<const std::uint8_t>b,std::size_t at){return(std::uint32_t(map_entry_word(b,at))<<16)|map_entry_word(b,at+2);}
inline void load_level_plane_maps(ActorState&fg,ActorState&bg,std::span<std::uint8_t>front,std::span<std::uint8_t>back,std::span<const std::uint8_t>rom,LevelMapEntryState&g,LevelMapEntryServices&s){
 if(g.selector&32768)return;const auto offset=static_cast<std::uint16_t>(g.selector<<3);const auto table=std::int64_t(0x4ab1a)+signed_word(offset);const auto first=map_entry_long(rom,std::size_t(table));if(!g.bank_override)g.foreground_bank=static_cast<std::uint8_t>(first>>24);
 auto copy=[&](std::uint32_t source,std::span<std::uint8_t>out,std::size_t raw){if((map_entry_long(rom,source)&0xffffff00)==0x4d415000){if(source+raw>rom.size()||raw>out.size())throw std::out_of_range("Raw MAP extent");std::copy_n(rom.begin()+source,raw,out.begin());}else{auto decoded=decode_backward_asset(rom,source,out.size());std::copy(decoded.bytes.begin(),decoded.bytes.end(),out.begin());}};
 fg.longword(34,0xffffcc44);copy(first&0xffffff,front,4096);const auto second=map_entry_long(rom,std::size_t(table)+4);g.background_bank=static_cast<std::uint8_t>(second>>24);bg.longword(34,0xffffdc44);if(!offset)s.special_background(second&0xffffff,back);else copy(second&0xffffff,back,2048);
}
inline void initialize_level_plane_entries(ActorState&fg,ActorState&bg,std::span<std::uint8_t>front,std::span<std::uint8_t>back,std::span<const std::uint8_t>rom,LevelMapEntryState&g,LevelMapEntryServices&s){
 fg.word(16,0xc000);bg.word(16,0xe000);fg.longword(0,0xffff0000);bg.longword(0,0xffff4000);fg.longword(30,0x40000003);bg.longword(30,0x60000003);fg.longword(26,0);bg.longword(26,0);fg.word(22,65535);bg.word(22,65535);
 constexpr std::uint16_t front_values[]{64,6,0x1f80,0x3f0,0x1f80,0x2000},back_values[]{32,2,0xf80,0x1f0,0xf80,0x1000};for(unsigned i=0;i<6;++i){fg.word(4+i*2,front_values[i]);bg.word(4+i*2,back_values[i]);}
 load_level_plane_maps(fg,bg,front,back,rom,g,s);g.reward=front[3];fg.word(38,map_entry_word(front,4));fg.word(40,map_entry_word(front,6));bg.word(38,map_entry_word(back,4));bg.word(40,map_entry_word(back,6));g.cache=0;s.prepare_planes(fg,bg);
}
inline void scan_startup_map_entries(std::span<std::uint8_t>map,std::span<const std::uint32_t>definitions,LevelMapEntryState&g,LevelMapEntryServices&s){
 const auto rows=map_entry_word(map,6)>>4;unsigned row=0;do{const auto start=map_entry_word(map,8+row*2),end=map_entry_word(map,10+row*2);if(start>=32768||end>=32768||end<start||(end-start)%4||end>map.size())throw std::out_of_range("Startup MAP row");for(unsigned cursor=start;cursor<end;cursor+=4){const auto record=map_entry_long(map,cursor);const auto type=std::uint16_t(record>>16);if(type<0x400)continue;const auto parameter=type&255,kind=type&0xff00;
  if(kind==0x1100&&parameter==g.foreground_bank){auto&actor=*g.controlled;actor.longword(12,std::uint32_t(std::uint16_t(record+8))<<16);actor.longword(16,std::uint32_t(std::uint16_t(row<<4))<<16);g.checkpoint_x=actor.word(12);g.checkpoint_y=actor.word(16);s.camera(g);}
  else if(kind==0x500){const auto index=(parameter&254)/2;if(index>=definitions.size())throw std::out_of_range("Startup definition table");const auto def=definitions[index];if(def==0x14906||def==0x148c2||def==0x148e4){map[cursor]=0x17;s.startup_allocate(def,record);}}
 }++row;}while(row<rows);
}
struct LevelStartupMapStorage{std::span<std::uint8_t>foreground,background;};
inline void scan_foreground_startup_map(LevelStartupMapStorage storage,std::span<const std::uint32_t>definitions,LevelMapEntryState&g,LevelMapEntryServices&s){scan_startup_map_entries(storage.foreground,definitions,g,s);}
struct TerrainBottomRowEntryServices:TerrainDisplayServices{virtual void refill_bottom(ActorState&,TerrainCameraGlobals&)=0;};
inline void update_bottom_terrain_row_entry(ActorState&plane,TerrainCameraGlobals&g,std::span<const std::uint8_t>backing,TerrainBottomRowEntryServices&s){s.refill_bottom(plane,g);display_terrain_row(plane,g,backing,true,s);}
}
