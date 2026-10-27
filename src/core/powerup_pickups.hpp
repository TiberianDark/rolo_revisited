#pragma once
#include "core/actor_defeat.hpp"
namespace rolo {
struct PowerupPickupServices:DefeatServices {virtual void powerup_sound(std::uint16_t)=0;};
inline void collect_trunk_strength(ActorState& a,std::uint8_t& v,PowerupPickupServices& s){s.powerup_sound(64);if(v!=3)v=static_cast<std::uint8_t>(v+1);a.byte(125,a.byte(125)|4);(void)actor_hit_counter_zero(a,s);}
inline void collect_float_power(ActorState& a,std::uint8_t& c513,std::uint8_t& c520,PowerupPickupServices& s){s.powerup_sound(64);c513=255;c520=0;a.byte(125,a.byte(125)|4);(void)actor_hit_counter_zero(a,s);}
inline void collect_stored_projectiles(ActorState& a,std::uint32_t& d,std::uint8_t& v,ActorState& head,PowerupPickupServices& s){s.powerup_sound(64);if(d!=0x140ca){v=0;d=0x140ca;}unsigned sum=unsigned(v)+3;v=static_cast<std::uint8_t>(sum>255?1:sum);head.byte(46,255);a.byte(125,a.byte(125)|4);(void)actor_hit_counter_zero(a,s);}
}
