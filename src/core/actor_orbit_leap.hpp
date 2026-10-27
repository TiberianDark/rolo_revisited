#pragma once
#include "core/actor_probe_patrol.hpp"
#include "core/actor_wave_motion.hpp"
#include <algorithm>
namespace rolo {
inline void update_actor_pause_orbit(ActorState*&a,ActorProbeServices&s){
 actor_probe_contacts(a,s);const auto state=a->byte(46);
 if(!state){a->byte(46,255);a->word(50,0);a->longword(20,a->longword(12));a->longword(24,a->longword(16));return;}
 if(state<128){auto lo=a->word(12),hi=lo;const auto x=s.controlled().word(12);if(a->byte(118)&8)lo=static_cast<std::uint16_t>(lo-200);else hi=static_cast<std::uint16_t>(hi+200);if(signed_word(x)>=signed_word(lo)&&signed_word(x)<=signed_word(hi))a->byte(46,255);return;}
 const auto phase=a->word(50);if(!phase){a->word(48,0x580);a->byte(121,a->byte(121)^1);}
 const auto speed=a->word(48);const auto delta=static_cast<std::uint32_t>(static_cast<std::int32_t>(signed_word(speed)))*256u;
 a->longword(50,a->byte(121)?a->longword(50)-delta:a->longword(50)+delta);a->word(48,static_cast<std::uint16_t>(speed-32));
 if(speed<32){a->byte(46,1);a->byte(118,(a->byte(118)&~8u)|(a->byte(121)?8u:0));}
 const auto v=actor_wave_vector(phase,100,1);a->longword(12,v.x+a->longword(20));a->longword(16,v.y+a->longword(24));
}
inline void update_actor_range_leap(ActorState*&a,ActorProbeServices&s){
 if(a->byte(117))return;s.object_contact(a);if(s.player_contact(a))s.hurt(a);
 if(!(a->byte(124)&16)){
  a->longword(58,0);a->word(70,0);auto&c=s.controlled();auto dx=static_cast<std::uint16_t>(c.word(12)-a->word(12));
  if(dx&32768){a->byte(121,255);a->byte(118,a->byte(118)|8);dx=static_cast<std::uint16_t>(0-dx);}else{a->byte(121,1);a->byte(118,a->byte(118)&~8u);}
  const auto dy=static_cast<std::uint16_t>(a->word(16)-c.word(16));
  if(signed_word(dy)>=-16&&signed_word(dy)<=150&&signed_word(dx)<=100){
   a->byte(124,a->byte(124)|16);a->byte(122,255);const auto quarter=signed_word(dy)>>2;
   a->word(62,static_cast<std::uint16_t>(std::clamp<int>(quarter,4,10)));a->longword(58,0x60000);a->word(70,4);
  }
 }s.gravity(a);s.integrate(a);s.land(a);
}
}
