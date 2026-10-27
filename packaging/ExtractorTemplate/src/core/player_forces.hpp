#pragma once
#include "core/actor_state.hpp"
namespace rolo {
// $8100..$8116: exact zero leaves direction unchanged; only negative clears it.
inline void player_horizontal_drag(ActorState& actor,std::uint32_t drag) {
    const auto speed=actor.longword(58)-drag;
    if(signed_long(speed)<0){actor.longword(58,0);actor.byte(121,0);}
    else actor.longword(58,speed);
}
struct PlayerGravityGlobals {std::uint8_t c514{},c519{},c51a{},c481{};};
// $8116..$8202. Source sign tests and wrapped long arithmetic are preserved.
inline void player_gravity(ActorState& actor,const PlayerGravityGlobals& globals) {
    auto speed=actor.longword(62);const auto direction=actor.byte(122);
    const bool positive=direction!=0&&!(direction&128);
    const auto subtract=[&](std::uint32_t amount,std::uint8_t new_direction) {
        speed-=amount;
        if(signed_long(speed)<0){speed=0u-speed;actor.byte(122,new_direction);}
    };
    const auto accelerate=[&](std::uint32_t amount,std::uint32_t limit) {
        if(signed_long(speed)<signed_long(limit)) {
            speed+=amount;if(signed_long(speed)>signed_long(limit))speed=limit;
        }
    };
    const auto decelerate_to_one=[&] {
        speed-=0x6000u;if(signed_long(speed)<0x10000)speed=0x10000;
    };
    if(!globals.c514||globals.c519||globals.c51a) {
        if(!positive)subtract(0x6000,1);else accelerate(0x6000,0xf0000);
    } else if(!globals.c481) {
        if(!(direction&128))subtract(0x800,255);
        else if(signed_long(speed)>0x10000)decelerate_to_one();
        else accelerate(0x800,0x10000);
    } else {
        if(!positive) {
            if(signed_long(speed)>0x10000)decelerate_to_one();
            else subtract(0x800,1);
        } else accelerate(0x800,0x10000);
    }
    actor.longword(62,speed);
}
}
