#pragma once
#include "core/actor_wave_motion.hpp"
namespace rolo {
struct PlatformDirectionService {virtual ~PlatformDirectionService()=default;virtual void choose_direction(ActorState&)=0;};
inline bool actor_supported_by(const ActorState& controlled,std::uint32_t actor_key){return controlled.longword(98)==actor_key&&(controlled.byte(124)&32);}
// $C244/$C2B4: first update advances even before a rider sets latch56.
inline void update_actor_ellipse_platform(ActorState& a,const ActorState& controlled,std::uint32_t key,bool vertical){
 if(!a.byte(56)){
  if(!a.word(20)){
   a.word(50,vertical?0:128);a.longword(20,a.longword(12)+(vertical?0:0x00c80000u));
   a.longword(24,a.longword(16)-(vertical?0x00c80000u:0));
  }else {if(!actor_supported_by(controlled,key))return;a.byte(56,255);}
 }
 const auto phase=a.word(50);a.word(50,static_cast<std::uint16_t>(phase+1));auto v=actor_wave_vector(phase,200,1);
 if(vertical)v.x=static_cast<std::uint32_t>(signed_long(v.x)>>2);else v.y=static_cast<std::uint32_t>(signed_long(v.y)>>2);
 actor_displace_and_measure(a,v.x+a.longword(20)-a.longword(12),v.y+a.longword(24)-a.longword(16));
}
// $C4BA/$C51E: cooldown stops movement and clears velocity highWORDs only.
inline void update_actor_rider_reversing_platform(ActorState& a,const ActorState& controlled,std::uint32_t key,bool horizontal,PlatformDirectionService& service){
 if(a.word(52)){a.word(52,static_cast<std::uint16_t>(a.word(52)-1));actor_displace_and_measure(a,0,0);return;}
 if(!actor_supported_by(controlled,key))return;
 if(!a.word(50)){a.word(50,horizontal?2:static_cast<std::uint16_t>(-2));a.word(52,50);return;}
 const auto delta=std::uint32_t(a.word(50))<<16;actor_displace_and_measure(a,horizontal?delta:0,horizontal?0:delta);
 a.byte(121,0);service.choose_direction(a);
 if(a.byte(121)){a.word(50,static_cast<std::uint16_t>(0-a.word(50)));a.word(52,50);}
}
// $C7B8/$C7FC/$C844/$C850: unsigned cached-limit test then signed origin test.
inline void update_actor_retracting_platform(ActorState& a,std::uint8_t gate,std::uint16_t origin,bool vertical){
 if(!gate)return;const unsigned position=vertical?16:12,dimension=vertical?38:36;
 if(!a.word(50))a.word(50,static_cast<std::uint16_t>(a.word(position)-a.word(dimension)*(vertical?2:1)));
 std::uint32_t delta=0;
 if(a.word(50)<a.word(position)&&signed_word(static_cast<std::uint16_t>(origin-100))<=signed_word(a.word(position)))delta=0xffff0000u;
 actor_displace_and_measure(a,vertical?0:delta,vertical?delta:0);
}
}
