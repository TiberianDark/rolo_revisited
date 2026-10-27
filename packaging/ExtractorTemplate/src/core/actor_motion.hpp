#pragma once
#include "core/actor_state.hpp"

namespace rolo {
// $CD8E..$CDE4: magnitude and signed byte direction, preserving modular data.
inline void actor_gravity(ActorState& actor) {
    if(actor.byte(117)&0x0e) return;
    auto speed=actor.longword(62);
    if(actor.byte(122)&0x80) {
        speed-=0x6000u;
        if(speed&0x80000000u) {speed=0u-speed;actor.byte(122,1);}
        actor.longword(62,speed);return;
    }
    actor.byte(122,1);
    if(signed_long(speed)>=0xf0000) return;
    speed+=0x6000u;
    if(signed_long(speed)>0xf0000) speed=0xf0000;
    actor.longword(62,speed);
}

// $CFCE..$CFFC. Never replace sign/magnitude fields with signed floating speed.
inline void actor_integrate(ActorState& actor) {
    for(const auto axis:{0,1}) {
        const auto direction=actor.byte(121+axis);
        if(direction==0) continue;
        const auto speed=actor.longword(axis?62:58);
        const auto position=actor.longword(axis?16:12);
        actor.longword(axis?16:12,(direction&0x80)?position-speed:position+speed);
    }
}

// $D042..$D05A changes integer X/velocity highwords, retaining fractions.
inline void actor_integer_x_step(ActorState& actor,std::uint16_t step) {
    actor.byte(121,0);actor.word(58,step);
    if(actor.byte(118)&8) step=static_cast<std::uint16_t>(0u-step);
    actor.word(12,static_cast<std::uint16_t>(actor.word(12)+step));
}
}
