#pragma once
#include "core/actor_common_state.hpp"
namespace rolo {
// $DD36: position relative to the live scroll WORD; no fractional writes.
inline void actor_scroll_relative_motion(ActorState& a,std::uint16_t scroll){
 if(!a.word(46)){a.word(46,a.word(12));return;}
 const auto x=static_cast<std::uint16_t>(a.word(46)-scroll);
 auto delta=static_cast<std::uint16_t>(a.word(12)-x);a.word(12,x);
 if(!delta){a.word(70,0);a.word(58,0);return;}
 if(delta&0x8000){a.word(70,8);delta=static_cast<std::uint16_t>(0-delta);}else a.word(70,4);
 a.word(58,delta);
}
// $C95A: velocity high WORDs report integer displacement including fraction carry.
inline void actor_displace_and_measure(ActorState& a,std::uint32_t dx,std::uint32_t dy){
 const auto x=a.longword(12),y=a.longword(16);
 a.longword(12,x+dx);a.word(58,static_cast<std::uint16_t>((a.longword(12)>>16)-(x>>16)));
 a.longword(16,y+dy);a.word(62,static_cast<std::uint16_t>((a.longword(16)>>16)-(y>>16)));
}
// $BFE4: negate only input D3 low WORD before SWAP; retain high WORD.
inline void actor_carry_negated_word(ActorState& a,ActorState& controlled,std::uint32_t dx,std::uint32_t d3){
 const auto neg=static_cast<std::uint16_t>(0-static_cast<std::uint16_t>(d3));
 actor_carry_controlled(a,controlled,dx,(std::uint32_t(neg)<<16)|(d3>>16));
 a.byte(52,static_cast<std::uint8_t>(static_cast<std::uint16_t>(d3)*2));
}
}
