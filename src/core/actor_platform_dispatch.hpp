#pragma once
#include "core/actor_platform_contact.hpp"
#include "core/actor_rider_platforms.hpp"
#include "core/actor_triggered_platforms.hpp"
#include "core/actor_bounce_chain_platforms.hpp"
namespace rolo {
struct PlatformDispatchState {
 ActorPlatformRoster roster;
 std::uint16_t origin_x{},origin_y{},incoming_d3_high{};
 std::uint32_t allocation_context{};
 std::uint8_t f281{},f282{};
};
struct PlatformDispatchServices:ActorPlatformContactServices,PlatformDirectionService,PlatformDirectionFlagsService,
 PlatformObjectContactService,ChainPlatformServices {};
// $8A0C: delta snapshots precede fraction stores and every live rider visit.
inline void transfer_platform_displacement(ActorPool& pool,std::uint32_t key,const ActorPlatformRoster& roster){
 auto& platform=pool.resolve(key);const auto dx=platform.word(58),dy=platform.word(62);platform.word(60,dx);platform.word(64,dy);
 auto visit=[&](std::uint32_t rider){auto& a=pool.resolve(rider);if(a.longword(98)==key&&(a.byte(124)&32)){
  a.word(12,static_cast<std::uint16_t>(a.word(12)+dx));a.word(16,static_cast<std::uint16_t>(a.word(16)+dy));}};
 visit(roster.base);for(unsigned i=0;i<3;++i){const auto rider=roster.companions[i];if(rider)visit(rider);}
 platform.word(58,0);platform.word(62,0);
}
// $BE60..$BEDC: dispatch translated functions only, with explicit caller inputs.
inline void dispatch_actor_platform(ActorPool& pool,std::uint32_t key,std::uint16_t selector,PlatformDispatchState& state,PlatformDispatchServices& s){
 auto&a=pool.resolve(key);auto&c=pool.resolve(state.roster.controlled);
 switch(selector){
 case 0:update_actor_rider_sinking_platform(a,c,key,s);break;
 case 4:update_actor_bounce_platform(a,c,key,state.incoming_d3_high);break;
 case 8:update_actor_rider_accelerating_platform(a,c,key,false,s);break;
 case 12:update_actor_rider_accelerating_platform(a,c,key,true,s);break;
 case 16:update_actor_rider_spring_platform(a,c,key);break;
 case 20:case 24:case 28:case 32:update_actor_wave_platform(a,(selector-20)/4);break;
 case 36:case 40:update_actor_ellipse_platform(a,c,key,selector==40);break;
 case 44:case 48:update_actor_chain_platform(pool,key,selector==48,state.allocation_context,s);break;
 case 52:case 56:update_actor_rider_reversing_platform(a,c,key,selector==56,s);break;
 case 60:update_actor_grid_platform(a,c,key,s);break;
 case 64:update_actor_triggered_platform(a,c,key,state.f281,state.origin_y,0,s);break;
 case 68:case 72:update_actor_triggered_platform(a,c,key,state.f282,state.origin_x,selector==68?1:2,s);break;
 case 76:case 80:update_actor_retracting_platform(a,state.f281,selector==76?state.origin_x:state.origin_y,selector==80);break;
 case 84:case 88:update_actor_retracting_platform(a,state.f282,selector==84?state.origin_x:state.origin_y,selector==88);break;
 case 92:case 96:case 100:case 104:case 108:case 112:case 116:case 120:case 124:break;
 default:throw std::out_of_range("Platform selector54 admission");
 }
}
// $BE4E: contacts can mutate selector, roster and retained context before dispatch.
inline void update_actor_platform_motion(ActorPool& pool,std::uint32_t key,PlatformDispatchState& state,PlatformDispatchServices& services){
 update_platform_roster_contact(pool,key,state.roster,services);
 dispatch_actor_platform(pool,key,pool.resolve(key).word(54),state,services);
 transfer_platform_displacement(pool,key,state.roster);
}
}
