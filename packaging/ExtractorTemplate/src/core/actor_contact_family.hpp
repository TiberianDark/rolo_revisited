#pragma once
#include "core/actor_common_callbacks.hpp"
namespace rolo {
inline std::array<std::uint16_t,8> actor_contact_thresholds{};
inline std::array<std::uint8_t,6> actor_contact_speeds{};
inline std::array<std::int16_t,4> actor_contact_y_offsets{};
// $E5A4: directional walk before gravity, integration and floor service.
inline void update_actor_contact_ground_walk(ActorState& a,FirstEnemyServices& s){
 if(a.byte(117))return;update_actor_contact_only(a,s);actor_integer_x_step(a,1);s.choose_direction(a);s.gravity(a);s.integrate(a);s.land(a);
}
// $E6D8: contact directly hurts controlled actor; floor contact also stops callback.
inline void update_actor_contact_settle(ActorState& a,ActorDirectContactServices& s){
 if(a.byte(117))return;s.object_contact(a);const bool hit=s.player_contact(a);
 if(hit)s.hurt_controlled_actor(a);else{s.gravity(a);s.integrate(a);s.land(a);if(!(a.byte(124)&1))return;}
 a.word(70,4);a.longword(42,0xa84c);
}
// $F856: signed phase threshold chooses axis;122sets optional halfpixel direction.
inline void update_actor_contact_corner(ActorState& a,ActorDirectContactServices& s){
 if(s.player_contact(a))s.hurt_controlled_actor(a);
 const bool horizontal=signed_word(a.word(46))>112;
 if(horizontal)actor_integer_x_step(a,6);else a.word(16,static_cast<std::uint16_t>(a.word(16)+6));
 const auto direction=a.byte(122);if(!direction)return;const unsigned axis=horizontal?16:12;
 a.longword(axis,a.longword(axis)+((direction&128)?0xffff8000u:0x8000u));
}
// $E0C2: proximity arms falling motion, beginning on the next callback.
inline void update_actor_proximity_fall(ActorState& a,ActorDirectContactServices& s){
 a.byte(118,a.byte(118)&~8u);if(s.player_contact(a))s.hurt_controlled_actor(a);
 if(a.byte(46)){s.gravity(a);s.integrate(a);return;}
 const auto& controlled=s.controlled_actor();auto delta=static_cast<std::uint16_t>(controlled.word(12)-a.word(12));
 if(delta&0x8000)delta=static_cast<std::uint16_t>(0-delta);
 if(signed_word(delta)<=signed_word(actor_contact_thresholds[controlled.word(58)&7]))a.byte(46,255);
}
// $DBBE: live contact services may change phase before testing the jump state.
inline void update_actor_contact_return_jump(ActorState& a,ActorDirectContactServices& s){
 if(a.byte(117))return;s.object_contact(a);if(s.player_contact(a))s.hurt_controlled_actor(a);
 if(a.word(46)){s.gravity(a);s.integrate(a);const auto anchor=a.word(46);if(signed_word(anchor)>signed_word(a.word(16)))return;
  a.word(16,anchor);a.byte(124,a.byte(124)|1);a.word(46,0);return;}
 // The original absolute WORD distance is always signed<=7FFF, including8000.
 a.word(46,a.word(16));a.byte(124,a.byte(124)&~1u);a.byte(122,255);a.longword(62,0x68000);
}
// $DA22: admitted six-step phase cycle; bytecounter occupies the highBYTE of46.
inline void update_actor_contact_six_step(ActorState& a,FirstEnemyServices& s){
 if(a.byte(117))return;update_actor_contact_only(a,s);if(a.byte(114))return;
 if(a.byte(46)>5)throw std::out_of_range("Six-step actor phase");
 auto phase=static_cast<std::uint8_t>(a.byte(46)+1);if(phase>=6)phase=0;a.byte(46,phase);
 const auto speed=actor_contact_speeds[phase];a.word(58,speed);
 a.word(12,static_cast<std::uint16_t>(a.word(12)+((a.byte(118)&8)?-int(speed):int(speed))));s.choose_direction(a);
}
// $D7E6: four admitted BYTE48 entries, retained fractions on coordinate writes.
inline void update_actor_contact_diagonal(ActorState& a,FirstEnemyServices& s){
 if(a.word(70)==4)return;s.object_contact(a);if(s.player_contact(a)){s.player_damage(a);a.word(70,4);}
 const auto phase=a.byte(48);if(phase<1||phase>4)throw std::out_of_range("Diagonal actor phase");
 a.word(12,static_cast<std::uint16_t>(a.word(12)-4));a.word(16,static_cast<std::uint16_t>(a.word(16)+actor_contact_y_offsets[phase-1]));
}
}
