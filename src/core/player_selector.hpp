#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct PlayerSelectorGlobals {
    std::uint8_t c510{},c513{},c520{},c519{},c51b{},c481{},c485{};
};
// $8934..$8A0C, caller $8838 supplies latched flag bytes D0/D1.
// Returns D2; caller writes actor70. Side effects occur only on reached paths.
inline std::uint16_t player_animation_selector(ActorState& actor,PlayerSelectorGlobals& globals,
        std::uint8_t flags124,std::uint8_t flags125) {
    if(!globals.c510) {
        if(globals.c513)return 88;
        if(globals.c520&128) {
            globals.c51b=0;
            if(flags124&16)return 72;
            return actor.longword(46)?68:64;
        }
        if(globals.c520)return 0;
    }
    if(globals.c519)return (flags124&1)?36:32;
    if(globals.c51b) {
        if(!(flags124&1))return 32;
        globals.c51b=0;
    }
    if(flags125&8)return 52;
    if(flags124&16)return 8;
    if(!(flags124&1)&&actor.word(68)>=8)return 12;
    const auto flags=actor.byte(126);
    actor.byte(126,static_cast<std::uint8_t>(flags&~32u));
    if(!(flags&32)&&globals.c481)return 24;
    if(actor.longword(46))return globals.c485?16:4;
    return actor.byte(121)?20:0;
}
}
