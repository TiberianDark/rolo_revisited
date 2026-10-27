#pragma once
#include "core/actor_scene_rewards.hpp"
#include "core/graphic_actor_shared_entries.hpp"
namespace rolo {
// Original E3A0..E478. Four native bodies reached by E342's BYTE46 table.
// The final sixteen signed bytes are data, not instructions.
inline std::array<std::int8_t,16> timed_projectile_wave{};
template<class World>void update_timed_projectile_phase(ActorState& a,std::uint32_t entry,World& w){
 switch(entry){
 case 0xe3a0:
  if(actor_floor_probe(w.terrain,a.word(12),static_cast<std::uint16_t>(a.word(16)+59)).found)a.byte(46,static_cast<std::uint8_t>(a.byte(46)+1));
  actor_gravity(a);if(signed_long(a.longword(62))>0x50000)a.longword(62,0x50000);actor_integrate(a);return;
 case 0xe3d2:
  w.reservations.reserve(w.pool,ActorPool::key(&a-w.pool.actors.data()));a.word(70,4);adjust_actor_vertical_force(a,0x4000);actor_integrate(a);
  if(!a.byte(47)){if(a.byte(122)&128){const auto delay=static_cast<std::uint8_t>(w.random.between(3,9));a.byte(47,delay);a.byte(48,delay);}return;}
  a.byte(47,static_cast<std::uint8_t>(a.byte(47)-1));if(!a.byte(47)){a.byte(46,static_cast<std::uint8_t>(a.byte(46)+1));a.word(50,250);}return;
 case 0xe41c:
  actor_gravity(a);if(a.byte(122)&128){actor_integrate(a);return;}
  a.byte(122,0);a.longword(62,0);a.byte(46,static_cast<std::uint8_t>(a.byte(46)+1));return;
 case 0xe43a:{
  actor_integrate(a);a.longword(62,0);const auto index=(static_cast<std::uint8_t>(w.frame)+a.byte(48))&15;
  a.word(16,static_cast<std::uint16_t>(a.word(16)+timed_projectile_wave[index]));a.word(50,static_cast<std::uint16_t>(a.word(50)-1));if(!a.word(50))a.word(70,8);return;
 }
 default:throw std::out_of_range("Timed projectile phase entry");
 }
}
}

