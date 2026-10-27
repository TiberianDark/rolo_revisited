#pragma once
#include "core/actor_state.hpp"
namespace rolo {
// $D05A..$D06C: write vertical speed highword and step actual Y highword.
inline void actor_integer_y_step(ActorState& a,std::uint16_t step){
 a.word(62,step);if(a.byte(122)&128)step=static_cast<std::uint16_t>(0u-step);
 a.word(16,static_cast<std::uint16_t>(a.word(16)+step));
}
// $D108..$D11A: same contract, applied to alternate/presentation Y at24.
inline void actor_integer_alternate_y_step(ActorState& a,std::uint16_t step){
 a.word(62,step);if(a.byte(122)&128)step=static_cast<std::uint16_t>(0u-step);
 a.word(24,static_cast<std::uint16_t>(a.word(24)+step));
}
}
