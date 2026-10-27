#pragma once
#include "core/actor_phase_emitters.hpp"
#include "core/actor_acceleration.hpp"
#include "core/level2_actor_updates.hpp"
namespace rolo {
struct RemainingActorGlobals{std::uint8_t visited=0;};
struct RemainingActorServices:PhaseEmitterServices{virtual void object(ActorState*&)=0;virtual bool contact(ActorState*&)=0;virtual void damage(ActorState*&)=0;virtual void hurt(ActorState*&)=0;virtual ActorState& controlled()=0;virtual ActorState& parent(std::uint32_t)=0;virtual void direction(ActorState*&,PhaseEmitterContext&)=0;virtual void land(ActorState*&)=0;virtual void horizontal(ActorState*&)=0;virtual void trunk(ActorState*&,PhaseEmitterContext&)=0;virtual void phase_target(ActorState*&,std::uint32_t)=0;};
inline void update_contact_phase_dispatch(ActorState*&a,PhaseEmitterContext&c,RemainingActorServices&s){
 if(a->byte(117))return;if(!(a->byte(125)&64)){s.trunk(a,c);actor_decelerate(*a);s.horizontal(a);if(!(a->byte(124)&6)){if(!s.contact(a)){if(a->word(70)==8)return;constexpr std::uint32_t targets[]{0xe3a0,0xe3d2,0xe41c,0xe43a};const auto index=a->byte(46);if(index>3)throw std::out_of_range("E342 phase");s.phase_target(a,targets[index]);return;}s.hurt(a);}}a->word(70,8);
}
inline void update_parent_linked_part(ActorState*&a,std::span<const std::uint8_t>rom,RemainingActorServices&s,std::uint32_t rom_base=0){
 if(s.contact(a))s.damage(a);auto&parent=s.parent(a->longword(46));if(signed_word(parent.word(46))<12){if(parent.word(46)==4&&signed_word(parent.word(50))>50)a->byte(125,a->byte(125)^2);else a->byte(125,a->byte(125)&~2u);const auto base=parent.word(70)?0xec94:0xecac;const auto index=static_cast<std::uint16_t>(a->word(50)*4);const auto at=std::int64_t(base)+signed_word(index)-rom_base;if(at<0||std::size_t(at)+4>rom.size())throw std::out_of_range("Part offsets");a->word(12,static_cast<std::uint16_t>(parent.word(12)+((rom[at]<<8)|rom[at+1])));a->word(16,static_cast<std::uint16_t>(parent.word(16)+((rom[at+2]<<8)|rom[at+3])));return;}
 if(a->byte(117)||signed_word(a->word(50))>3){a->byte(116,255);return;}actor_gravity(*a);actor_integrate(*a);const auto speed=a->longword(62);s.land(a);const auto old=a->byte(124);a->byte(124,old&~1u);if(old&1){a->longword(62,static_cast<std::uint32_t>(signed_long(speed)>>1));a->byte(122,255);}
}
inline void update_limited_child_emitter(ActorState*&a,PhaseEmitterContext&c,RemainingActorGlobals&g,RemainingActorServices&s){
 if(g.visited){a->byte(116,255);return;}a->byte(125,a->byte(125)|4);auto&controlled=s.controlled();c.resource=0x60000;auto distance=static_cast<std::uint16_t>(controlled.word(12)-a->word(12));if(signed_word(a->word(48))>=3){a->byte(118,a->byte(118)|8);accelerate_actor_magnitude(*a,0,false,0x4000,0x60000);}else if(distance){const bool positive=!(distance&32768);a->byte(118,positive?a->byte(118)&~8u:a->byte(118)|8);accelerate_actor_magnitude(*a,0,positive,0x4000,0x60000);if(!positive)distance=static_cast<std::uint16_t>(0-distance);}actor_integrate(*a);if(signed_word(a->word(48))>=3)return;if(a->word(46)){a->word(46,static_cast<std::uint16_t>(a->word(46)-1));return;}if(signed_word(distance)>32)return;a->word(46,100);a->word(48,static_cast<std::uint16_t>(a->word(48)+1));c.d2=a->longword(12);c.d3=a->longword(16);auto*saved=a;auto*child=s.allocate(a,c,{0x1443e,c.resource,c.d2,c.d3,0,0});a=saved;if(child){child->longword(42,0xb726);child->byte(46,255);child->byte(121,a->byte(121));child->longword(58,a->longword(58));}
}
inline void update_split_child_emitter(ActorState*&a,PhaseEmitterContext&c,RemainingActorServices&s){
 if(a->byte(117))return;s.object(a);if(a->word(70)==8)return;bool emit=s.contact(a);
 if(!emit){auto&controlled=s.controlled();auto dy=static_cast<std::uint16_t>(controlled.word(16)-a->word(16));if(dy&32768)dy=static_cast<std::uint16_t>(0-dy);
  if(signed_word(dy)>16){a->byte(115,6);actor_integer_x_step(*a,1);s.direction(a,c);a->word(70,0);}
  else{a->byte(115,3);a->byte(121,255);c.resource=(c.resource&0xffffff00)|8;auto dx=static_cast<std::uint16_t>(a->word(12)-controlled.word(12));if(dx&32768){dx=static_cast<std::uint16_t>(0-dx);a->byte(121,1);c.resource=0;}a->word(70,4);if(signed_word(dx)>=60){a->word(70,0);a->longword(58,0x30000);a->byte(118,static_cast<std::uint8_t>(c.resource));}const auto speed=a->longword(58)-0x1800;a->longword(58,speed);if(speed&0x80000000){a->longword(58,0);a->byte(121,0);emit=true;}}
 }
 if(emit){a->word(70,8);constexpr std::uint8_t data[]{255,3,0,0,1,3};unsigned at=0;for(unsigned counter=2;;--counter){c.resource=counter;c.d2=a->longword(12);c.d3=a->longword(16);auto*child=s.allocate(a,c,{0x14d8a,c.resource,c.d2,c.d3,0,0});c.resource=counter;if(!child)break;a->byte(122,255);a->longword(62,0x60000);a->byte(121,data[at++]);a->byte(59,data[at++]);c.resource=static_cast<std::uint16_t>(counter-1);if(!counter)break;}}
 actor_gravity(*a);actor_integrate(*a);s.land(a);s.horizontal(a);
}
}
