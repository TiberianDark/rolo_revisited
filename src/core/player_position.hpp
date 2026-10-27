#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct PlayerPositionGlobals {std::uint16_t width{},height{};std::uint8_t c516{};};
// $8202..$827A. Mixed signed/unsigned limits and word-only X clamps.
inline void integrate_player_position(ActorState& actor,PlayerPositionGlobals& globals) {
    const auto direction_x=actor.byte(121);
    if(direction_x) {
        const auto speed=actor.longword(58);
        if(direction_x&128) {
            actor.longword(12,actor.longword(12)-speed);
            if(signed_word(actor.word(12))<16) {
                actor.word(12,16);actor.byte(121,0);actor.longword(58,0);
            }
        } else {
            actor.longword(12,actor.longword(12)+speed);
            const auto width=actor.word(36);
            const auto half=static_cast<std::uint16_t>((width>>1)|(width&0x8000));
            const auto limit=static_cast<std::uint16_t>(globals.width-half);
            if(limit<=actor.word(12)) {
                actor.word(12,limit);actor.byte(121,0);actor.longword(58,0);
            }
        }
    }
    const auto speed_y=actor.longword(62);
    if(actor.byte(122)&128) {
        const auto position=actor.longword(16)-speed_y;
        actor.longword(16,signed_long(position)<0?0:position);
    } else {
        actor.longword(16,actor.longword(16)+speed_y);
        if(signed_word(globals.height)<signed_word(actor.word(16)))globals.c516=255;
    }
}
}
