#pragma once
#include "core/actor_contact_family.hpp"
#include "core/actor_acceleration.hpp"
#include "core/actor_direction_vector.hpp"
#include "core/actor_wave_motion.hpp"
#include "core/actor_integer_y_step.hpp"
namespace rolo {
struct ActorPursuitServices:ActorDirectContactServices {virtual bool select_vertical_direction(ActorState&)=0;};
inline void update_actor_flying_pursuit(ActorState&a,FirstEnemyServices&s){
 if(a.byte(117))return;update_actor_contact_only(a,s);const auto&c=s.controlled_actor();
 auto dx=std::uint16_t(c.word(12)-a.word(12));if(dx){const bool positive=!(dx&0x8000);a.byte(118,positive?a.byte(118)&~8u:a.byte(118)|8);accelerate_actor_magnitude(a,0,positive,0x4000,0x60000);if(!positive)dx=std::uint16_t(0-dx);}
 const auto dy=std::uint16_t(a.word(16)-c.word(16)+80);if(dy)accelerate_actor_magnitude(a,1,bool(dy&0x8000),0x2000,0x20000);
 if(signed_word(dx)<=50)a.byte(46,255);s.integrate(a);
}
inline void update_actor_rotating_pursuit(ActorState&a,ActorDirectContactServices&s){
 if(s.player_contact(a))s.hurt_controlled_actor(a);const auto phase=std::uint16_t((a.word(50)+a.word(52))&63);a.word(50,phase);auto v=actor_direction_vector(phase,1);a.longword(12,a.longword(12)+v.x);a.longword(16,a.longword(16)+v.y);
 if(!a.word(48))s.gravity(a);else{a.word(48,std::uint16_t(a.word(48)-1));const auto&c=s.controlled_actor();const auto dx=std::uint16_t(c.word(12)-a.word(12));if(dx)accelerate_actor_magnitude(a,0,!(dx&0x8000),0x4000,0x40000);const auto dy=std::uint16_t(a.word(16)-c.word(16)+16);if(dy)accelerate_actor_magnitude(a,1,bool(dy&0x8000),0x4000,0x40000);}
 s.integrate(a);
}
inline void update_actor_parent_jump(ActorPool&pool,std::uint32_t key,ActorDirectContactServices&s){
 auto&a=pool.resolve(key);if(a.byte(117))return;if(s.player_contact(a))s.hurt_controlled_actor(a);auto&parent=pool.resolve(a.longword(76));
 if(!a.word(46)){a.word(34,std::uint16_t(std::int16_t(std::int8_t(parent.byte(47)))));if(parent.byte(46)){a.byte(122,255);a.longword(62,0x80000);a.word(46,a.word(16));}return;}
 s.gravity(a);s.integrate(a);const auto anchor=a.word(46);if(signed_word(anchor)>signed_word(a.word(16)))return;a.word(16,anchor);parent.byte(46,0);a.word(46,0);
}
inline void update_actor_ground_hopper(ActorState&a,FirstEnemyServices&s){
 if(a.byte(117))return;update_actor_contact_only(a,s);if(a.byte(46)){a.byte(46,0);a.byte(122,255);const auto&c=s.controlled_actor();auto dx=std::uint16_t(c.word(12)-a.word(12));if(dx&0x8000)dx=std::uint16_t(0-dx);a.longword(62,signed_word(dx)<=128?0x80000:0x40000);}
 const bool grounded=a.byte(124)&1;a.byte(47,grounded?255:0);if(!grounded)actor_integer_x_step(a,1);s.gravity(a);s.integrate(a);s.land(a);s.choose_direction(a);
}
inline void update_actor_orbit_patrol(ActorState&a,ActorPursuitServices&s){
 if(a.byte(117))return;if(!a.byte(47)){a.byte(47,255);a.word(20,a.word(12));a.word(24,a.word(16));}
 update_actor_contact_only(a,s);actor_face_from_controlled(a,s.controlled_actor());update_actor_small_orbit(a);
 if(std::int8_t(a.byte(46))>10){a.byte(46,std::uint8_t(a.byte(46)-1));return;}
 actor_integer_alternate_y_step(a,3);if(a.byte(46)){a.byte(46,std::uint8_t(a.byte(46)-1));return;}
 if(s.select_vertical_direction(a))a.byte(46,50);
}
}
