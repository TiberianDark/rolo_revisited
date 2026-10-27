#pragma once
#include "core/actor_anchor_steps.hpp"
#include "core/actor_motion.hpp"
namespace rolo {
struct ActorAnchorPair {std::uint16_t first_x=0,first_y=0,second_x=0,second_y=0;};
struct ActorAnchorFloor {std::uint16_t status,height;};
struct ActorAnchorServices {
 virtual ~ActorAnchorServices()=default;
 virtual void gravity(ActorState& a){actor_gravity(a);}
 virtual void integrate(ActorState& a){actor_integrate(a);}
 virtual void land(ActorState&)=0;
 virtual ActorAnchorFloor floor(std::uint16_t,std::uint16_t)=0;
};
// $E02C: controlled source remains live, including when source and actor alias.
inline void update_actor_anchor_follow(ActorState& a,ActorState& controlled,std::uint16_t offset,ActorAnchorServices& s){
 a.word(12,static_cast<std::uint16_t>(controlled.word(12)+offset));a.byte(121,0);
 a.longword(58,controlled.longword(58));
 const auto direction=controlled.byte(122);
 if(!(direction&128)){a.byte(122,direction);a.longword(62,controlled.longword(62));}
 s.gravity(a);s.integrate(a);s.land(a);
 const auto floor=s.floor(a.word(12),static_cast<std::uint16_t>(a.word(16)-16));
 if(!(floor.status&0x8000))a.word(16,floor.height);
 const auto x=a.word(12);a.word(70,x==a.word(20)?0:4);a.word(20,x);
 controlled.byte(124,controlled.byte(124)|(a.byte(124)&1));
}
inline void update_actor_first_anchor(ActorState& a,ActorState& c,ActorAnchorPair& anchors,ActorAnchorServices& s){
 update_actor_anchor_follow(a,c,static_cast<std::uint16_t>(-10),s);anchors.first_x=a.word(12);anchors.first_y=a.word(16);
}
inline void update_actor_second_anchor(ActorState& a,ActorState& c,ActorAnchorPair& anchors,ActorAnchorServices& s){
 update_actor_anchor_follow(a,c,10,s);anchors.second_x=a.word(12);anchors.second_y=a.word(16);
}
inline void place_actor_first_anchor(ActorState& a,const ActorAnchorPair& anchors){actor_place_from_anchor(a,anchors.first_x,anchors.first_y);}
inline void place_actor_second_anchor(ActorState& a,const ActorAnchorPair& anchors){actor_place_from_anchor(a,anchors.second_x,anchors.second_y);}
}
