#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct PlayerImpactServices {
    virtual ~PlayerImpactServices()=default;
    virtual void impact_sound(std::uint16_t)=0;
};
// $8C24..$8C88, controlled actor at entry. A5 changes; A0 is preserved locally.
inline void player_slope_impact(ActorState& actor,PlayerImpactServices& services) {
    if(!(actor.byte(124)&64))return;
    if(signed_word(actor.word(66))>=2)services.impact_sound(32);
    const auto slope=actor.byte(120);const auto shape=static_cast<int>(slope&63)-1;
    if(shape<=0)return;
    auto acceleration=static_cast<std::uint32_t>(shape)*actor.word(66);
    acceleration=(acceleration<<16)|(acceleration>>16);
    acceleration=(acceleration>>4)|((acceleration&0x80000000u)?0xf0000000u:0);
    const auto direction=actor.byte(121);
    if(slope&64) {
        if(direction&&!(direction&128))acceleration=0u-acceleration;
        else actor.byte(121,255);
    } else {
        if(direction&128)acceleration=0u-acceleration;
        else actor.byte(121,1);
    }
    actor.longword(46,acceleration);
}
}
