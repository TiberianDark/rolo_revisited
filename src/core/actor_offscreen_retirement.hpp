#pragma once
#include "core/actor_motion.hpp"
namespace rolo {
// $B47C..$B498: integrate even when offscreen; retire from bit3 only when117!=0.
inline void update_offscreen_retirement(ActorState& actor){
    actor_integrate(actor);
    if(!actor.byte(117))return;
    actor.byte(116,(actor.byte(126)&8)?0:255);
    actor.byte(126,actor.byte(126)|4);
}
}
