#pragma once
#include "core/actor_probe_patrol.hpp"
namespace rolo {
struct ActorEmitterContext{std::uint32_t resource;std::uint16_t x_fraction,y_fraction;};
struct ActorFacingEmitterServices:ActorProbeServices{
 virtual ActorState* allocate(ActorState*&,std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t,std::uint8_t,std::uint8_t)=0;
};
inline void update_actor_facing_emitter(ActorState*&a,ActorEmitterContext& context,ActorFacingEmitterServices&s){
 if(a->byte(117))return;actor_probe_contacts(a,s);
 if(a->byte(48)){a->byte(48,0);const auto x=(std::uint32_t(a->word(12))<<16)|context.x_fraction,y=(std::uint32_t(static_cast<std::uint16_t>(a->word(16)-16))<<16)|context.y_fraction;const auto facing=a->byte(118);s.allocate(a,0x149b0,context.resource,x,y,facing,0);return;}
 if(a->word(70))return;a->byte(121,0);a->word(58,1);a->word(12,static_cast<std::uint16_t>(a->word(12)+((a->byte(118)&8)?-1:1)));s.gravity(a);s.integrate(a);s.land(a);s.horizontal_direction(a);
 if(a->word(46)){a->word(46,static_cast<std::uint16_t>(a->word(46)-1));return;}
 auto&c=s.controlled();auto delta=static_cast<std::uint16_t>((a->byte(118)&8)?a->word(12)-c.word(12):c.word(12)-a->word(12));if(signed_word(delta)<0||signed_word(delta)>160)return;
 delta=static_cast<std::uint16_t>(a->word(16)-c.word(16));if(delta&32768)delta=static_cast<std::uint16_t>(0-delta);if(signed_word(delta)>16)return;a->word(70,4);a->word(46,100);
}
}
