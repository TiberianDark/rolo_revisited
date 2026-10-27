#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct ActorRescueServices{
 virtual ~ActorRescueServices()=default;
 virtual bool object_contact(ActorState*&)=0;
 virtual bool player_contact(ActorState*&)=0;
 virtual void damage(ActorState*&)=0;
 virtual ActorState& linked_word(std::uint16_t)=0;
 virtual bool type_is_56(ActorState&)=0;
 virtual void replace_type_56(ActorState*&,std::uint32_t)=0;
};
inline void update_actor_linked_rescue(ActorState*&a,std::uint8_t& latch,ActorRescueServices&s){
 if(!latch){
  if(!s.object_contact(a)&&a->word(70)!=8){if(s.player_contact(a))s.damage(a);return;}
  auto&linked=s.linked_word(a->word(74));if(!s.type_is_56(linked))return;
  latch=255;linked.longword(58,0);linked.byte(119,linked.byte(119)&~16u);s.replace_type_56(a,0xa8bc);linked.longword(42,0xe776);
 }a->word(70,4);
}
struct ActorHeldPublication{std::uint16_t actor=0,sentinel=0;};
inline void update_actor_held_presentation(ActorState&a,ActorState&head,ActorState&body,std::uint16_t identity,std::uint8_t enabled,std::uint8_t gate,ActorHeldPublication&publication){
 if(!enabled||gate)return;publication={identity,0};a.byte(118,head.byte(118));a.byte(125,(a.byte(125)&253)|(head.byte(125)&2));
 auto y=(head.byte(124)&32)?head.word(16):a.word(24);const auto limit=static_cast<std::uint16_t>(head.word(16)+body.word(34)-body.word(38)+8);if(signed_word(y)>signed_word(limit))y=limit;a.word(16,y);
 constexpr std::int16_t offsets[]{0,0,-2,0,0,-3,-3,0,0,-2,-2,0,0,0,0,0,0,0,0,0,0,0,0};const auto selector=head.word(70);if(selector%4||selector>88)throw std::out_of_range("Held head frame");auto x=body.word(32);auto offset=static_cast<std::uint16_t>(offsets[selector/4]);if(head.byte(118)&8){x=static_cast<std::uint16_t>(0-x);offset=static_cast<std::uint16_t>(0-offset);}a.word(12,static_cast<std::uint16_t>(head.word(12)+x+offset));a.word(24,static_cast<std::uint16_t>(body.word(16)+body.word(34)-body.word(38)+7));
}
struct ActorRightProbeServices{virtual ~ActorRightProbeServices()=default;virtual std::uint16_t tile(std::uint16_t,std::uint16_t)=0;virtual std::uint8_t geometry(std::uint16_t)=0;};
inline bool actor_right_half_condition(const ActorState&a,ActorRightProbeServices&s){
 const auto x=static_cast<std::uint16_t>((signed_word(a.word(36))>>1)+8+a.word(12)),y=static_cast<std::uint16_t>(a.word(16)+a.word(34)-(signed_word(a.word(38))>>1));const auto tile=s.tile(x,y);
 if(!(tile&0x2000)&&(tile&0xe00)==0xe00)return true;
 return (tile&0x4000)&&(s.geometry(tile)&63);
}
}
