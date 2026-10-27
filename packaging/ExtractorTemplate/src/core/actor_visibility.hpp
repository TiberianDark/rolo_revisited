#pragma once
#include "core/actor_state.hpp"
namespace rolo {
// $2A18..$2AB4: comparisons use signed, wrapped word bounds.
inline std::uint8_t actor_visibility_flags(const ActorState& actor,
        std::uint16_t reference_x,std::uint16_t reference_y) {
    if(actor.byte(126)&16)return 0;
    std::uint8_t flags=0;
    const auto x=actor.word(12),y=actor.word(16);
    auto lower=static_cast<std::uint16_t>(reference_x-80);
    auto upper=static_cast<std::uint16_t>(lower+480);
    if(signed_word(lower)>signed_word(x))flags|=4;
    if(signed_word(upper)<signed_word(x))flags|=8;
    lower=static_cast<std::uint16_t>(reference_y-32);
    upper=static_cast<std::uint16_t>(lower+336);
    if(signed_word(lower)>signed_word(y))flags|=1;
    if(signed_word(upper)<signed_word(y))flags|=2;
    // The original branch to $2A6C still checks far bounds when near flags are zero.
    lower=static_cast<std::uint16_t>(reference_x-368);
    upper=static_cast<std::uint16_t>(lower+1056);
    if(signed_word(lower)>signed_word(x))flags|=0x40;
    if(signed_word(upper)<signed_word(x))flags|=0x80;
    lower=static_cast<std::uint16_t>(reference_y-240);
    upper=static_cast<std::uint16_t>(lower+704);
    if(signed_word(lower)>signed_word(y))flags|=0x10;
    if(signed_word(upper)<signed_word(y))flags|=0x20;
    return flags;
}
}
