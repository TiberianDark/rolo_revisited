#pragma once
#include "core/actor_state.hpp"
#include <array>
#include <stdexcept>
namespace rolo {
inline std::array<std::uint8_t,22> actor_probe_patrol_steps{};
struct ActorProbeServices {
 virtual ~ActorProbeServices()=default;
 virtual void object_contact(ActorState*&)=0;
 virtual bool player_contact(ActorState*&)=0;
 virtual void damage(ActorState*&)=0;
 virtual void hurt(ActorState*&)=0;
 virtual bool terrain(std::uint16_t,std::uint16_t)=0;
 virtual void vertical_direction(ActorState*&)=0;
 virtual void horizontal_direction(ActorState*&)=0;
 virtual ActorState& controlled()=0;
 virtual ActorState& linked(std::uint32_t)=0;
 virtual void gravity(ActorState*&)=0;
 virtual void integrate(ActorState*&)=0;
 virtual void land(ActorState*&)=0;
};
inline void actor_probe_contacts(ActorState*&a,ActorProbeServices&s){s.object_contact(a);if(s.player_contact(a))s.damage(a);}
// $E5D0, query result is the original nonzero/Z-clear predicate.
inline void update_actor_vertical_probe(ActorState*&a,ActorProbeServices&s){
 if(a->byte(117))return;actor_probe_contacts(a,s);a->byte(118,a->byte(118)|8);
 if(s.terrain(static_cast<std::uint16_t>(a->word(12)-16),a->word(16)))a->byte(118,a->byte(118)&~8u);
 a->word(62,1);a->word(16,static_cast<std::uint16_t>(a->word(16)+((a->byte(122)&128)?-1:1)));s.vertical_direction(a);
 a->byte(119,(a->byte(122)&128)?a->byte(119)&~16u:a->byte(119)|16u);
}
inline void update_actor_table_patrol(ActorState*&a,ActorProbeServices&s){
 actor_probe_contacts(a,s);if(a->word(70)==8)return;
 a->byte(121,0);a->word(58,2);a->word(12,static_cast<std::uint16_t>(a->word(12)+((a->byte(118)&8)?-2:2)));s.horizontal_direction(a);
 const auto phase=a->byte(46);
 if(phase){
  const auto index=phase/2;if(index>=actor_probe_patrol_steps.size())throw std::out_of_range("DB44 vertical table");const auto step=actor_probe_patrol_steps[index];
  if(!(step&128)){a->word(16,static_cast<std::uint16_t>(a->word(16)+step));a->byte(46,static_cast<std::uint8_t>(phase+1));a->word(70,4);return;}
 }else{
  auto delta=static_cast<std::uint16_t>(a->word(12)-s.controlled().word(12));if(delta&32768)delta=static_cast<std::uint16_t>(0-delta);
  if(signed_word(delta)<=200)a->byte(46,static_cast<std::uint8_t>(a->byte(46)+1));
 }a->word(70,0);
}
// $DCDA: admitted finite acyclic link chain, copies integer coordinates only.
inline void update_actor_chain_throw(ActorState*&a,ActorProbeServices&s){
 while(const auto link=a->longword(84)){auto&next=s.linked(link);a->word(12,next.word(12));a->word(16,next.word(16));a=&next;}
 if(s.player_contact(a))s.hurt(a);a->byte(116,a->byte(117)?255:0);
 if(a->byte(46)){s.gravity(a);s.integrate(a);s.land(a);return;}
 a->byte(46,255);a->byte(121,(a->byte(118)&8)?255:1);a->longword(58,0x60000);
}
}

