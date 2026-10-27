#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
// 8FA4: unsigned containment of the controlled actor's prior vertical interval.
inline bool prior_player_contained(const ActorState& controlled,const ActorState& trigger){
 const auto prior=controlled.word(24),bottom=trigger.word(16);
 if(prior>bottom)return false;
 if(static_cast<std::uint16_t>(prior-controlled.word(38))<static_cast<std::uint16_t>(bottom-trigger.word(38)))return false;
 const auto half=static_cast<std::uint16_t>(signed_word(controlled.word(36))>>1);
 const auto outer_half=static_cast<std::uint16_t>(signed_word(trigger.word(36))>>1);
 const auto left=static_cast<std::uint16_t>(controlled.word(12)-half),outer_left=static_cast<std::uint16_t>(trigger.word(12)-outer_half);
 if(left<outer_left)return false;
 return static_cast<std::uint16_t>(left+half*2)<=static_cast<std::uint16_t>(outer_left+outer_half*2);
}
struct TriggerCaptureState {
 std::uint8_t c520{},c521{},c513{},c524{};std::uint16_t c526{},controlled_type{4};
 bool operator==(const TriggerCaptureState&)const=default;
};
// 989C: declared live actor identities; linked pointer corresponds to trigger84.
inline void capture_controlled_player(ActorState& trigger,ActorState& controlled,ActorState* linked,TriggerCaptureState& state){
 if(state.c520||state.controlled_type!=4||!prior_player_contained(controlled,trigger))return;
 if(trigger.longword(84)){if(!linked)throw std::logic_error("Unbound capture child identity");linked->byte(46,255);}
 state.c520=255;state.c521=0;state.c513=0;state.c526=6000;state.c524=255;
 controlled.byte(121,(controlled.byte(118)&8)?255:1);controlled.longword(58,0x40000);controlled.byte(122,255);controlled.longword(62,0x65e00);
 controlled.word(16,static_cast<std::uint16_t>(controlled.word(16)-4));controlled.word(70,0);
}
}
