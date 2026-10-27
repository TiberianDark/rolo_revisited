#pragma once
#include "core/actor_state.hpp"
#include "core/actor_contact.hpp"
namespace rolo {
struct ActorSpriteView {
    std::uint32_t graphics{};std::int16_t x{},y{};std::uint16_t width{},height{};
    bool flip_x{},flip_y{};
};
// $330A..$3366: whole image origin before hardware32px chunk subdivision.
inline ActorSpriteView actor_sprite_view(const ActorState& actor,std::uint16_t camera_x,std::uint16_t camera_y) {
    auto ox=actor.word(32),oy=actor.word(34);
    if(actor.byte(118)&8)ox=static_cast<std::uint16_t>(0u-ox);
    if(actor.byte(119)&16)oy=static_cast<std::uint16_t>(0u-oy);
    auto x=static_cast<std::uint16_t>(ox+actor.word(12)-half_signed_word(actor.word(36)));
    auto y=static_cast<std::uint16_t>(oy+actor.word(16)-actor.word(38));
    if(!(actor.byte(126)&16)){x=static_cast<std::uint16_t>(x-camera_x);y=static_cast<std::uint16_t>(y-camera_y);}
    return {actor.longword(28),signed_word(x),signed_word(y),actor.word(36),actor.word(38),
        (actor.byte(119)&8)!=0,(actor.byte(119)&16)!=0};
}
}
