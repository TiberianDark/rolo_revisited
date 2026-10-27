#pragma once
#include "core/actor_state.hpp"
namespace rolo {
// $DFE6..$DFFE: signed WORD height gate, then copy other actor vertical motion.
inline void actor_copy_vertical_at_height(ActorState& actor,const ActorState& source,std::uint16_t height){
 if(signed_word(height)>signed_word(actor.word(16)))return;
 actor.word(16,height);actor.byte(122,source.byte(122));actor.longword(62,source.longword(62));
}
// $E0B4..$E0C2: copy coordinate WORDs, subtract22 fromY, retain fractions.
inline void actor_place_from_anchor(ActorState& actor,std::uint16_t x,std::uint16_t y){
 actor.word(12,x);actor.word(16,static_cast<std::uint16_t>(y-22u));
}
}
