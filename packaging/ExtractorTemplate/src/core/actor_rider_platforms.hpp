#pragma once
#include "core/actor_platform_family.hpp"
#include "core/actor_common_state.hpp"
namespace rolo {
struct PlatformDirectionFlagsService {virtual ~PlatformDirectionFlagsService()=default;virtual bool choose_direction_nonzero(ActorState&)=0;};
// $BEE0: rider lowers platform eight integer pixels, then it rises when released.
inline void update_actor_rider_sinking_platform(ActorState& a,const ActorState& controlled,std::uint32_t key,PlatformDirectionService& s){
 if(actor_supported_by(controlled,key)){
  if(!a.word(50)){a.word(50,a.word(16));a.word(52,1);}
  const auto limit=static_cast<std::uint16_t>(a.word(50)+8);
  const auto dy=signed_word(limit)>signed_word(a.word(16))?0x10000u:0u;
  auto dx=a.word(52);if(a.byte(121)&128)dx=static_cast<std::uint16_t>(0-dx);
  actor_displace_and_measure(a,std::uint32_t(dx)<<16,dy);s.choose_direction(a);return;
 }
 const auto anchor=a.word(50);if(!anchor)return;
 if(signed_word(anchor)<signed_word(a.word(16)))actor_displace_and_measure(a,0,0xffff0000u);else a.word(50,0);
}
// $C022 uses returned actor121; $C08A uses original returned Z instead.
inline void update_actor_rider_accelerating_platform(ActorState& a,const ActorState& controlled,std::uint32_t key,bool down,PlatformDirectionFlagsService& s){
 if(!a.byte(50)){if(!actor_supported_by(controlled,key))return;a.byte(50,255);a.word(52,0);}
 a.byte(121,0);const bool nonzero=s.choose_direction_nonzero(a);
 if(down?nonzero:bool(a.byte(121))){a.byte(50,0);actor_displace_and_measure(a,0,0);return;}
 auto rate=static_cast<std::uint16_t>(a.word(52)+64);if(signed_word(rate)>1024)rate=1024;a.word(52,rate);
 auto velocity=a.byte(52);if(!down)velocity=static_cast<std::uint8_t>(0-velocity);
 const auto step=static_cast<std::uint16_t>(static_cast<std::int16_t>(static_cast<std::int8_t>(velocity)));
 actor_displace_and_measure(a,0,std::uint32_t(step)<<16);
}
// $C0EC: original return clamp uses unsigned BLS and clears position fraction.
inline void update_actor_rider_spring_platform(ActorState& a,const ActorState& controlled,std::uint32_t key){
 if(actor_supported_by(controlled,key)){
  if(!a.word(50)){a.word(50,a.word(16));a.word(52,0);}
  actor_displace_and_measure(a,0,actor_increment_vertical_drive(a));return;
 }
 if(!a.word(50))return;
 const auto drive=actor_increment_vertical_drive(a);actor_displace_and_measure(a,0,0u-drive);
 if(a.word(50)>a.word(16)){a.word(16,a.word(50));a.word(18,0);a.longword(50,0);}
}
}
