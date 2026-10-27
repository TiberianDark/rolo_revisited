#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
// D06C/D094/D0BA/D0E2: explicit original D0 increment / D1 signed cap.
inline void accelerate_actor_magnitude(ActorState& actor,unsigned axis,bool positive,
        std::uint32_t increment,std::uint32_t limit){
    if(axis>1)throw std::out_of_range("Native acceleration axis");
    const unsigned speed_offset=axis?62:58,direction_offset=axis?122:121;
    const auto direction=actor.byte(direction_offset);
    auto speed=actor.longword(speed_offset);
    const bool opposing=positive?(direction&128)!=0:direction!=0&&!(direction&128);
    if(opposing){
        speed-=increment;actor.longword(speed_offset,speed);
        if(!(speed&0x80000000u))return;
        actor.longword(speed_offset,0u-speed);
    }else{
        speed+=increment;
        if(signed_long(speed)>signed_long(limit))speed=limit;
        actor.longword(speed_offset,speed);
    }
    actor.byte(direction_offset,positive?1:255);
}
}
