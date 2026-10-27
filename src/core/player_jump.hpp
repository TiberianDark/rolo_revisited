#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct PlayerJumpInput {
    std::uint8_t mapped_jump{},held_jump{},c514{};
    std::uint16_t controlled_type{};
};
struct PlayerJumpServices {
    virtual ~PlayerJumpServices()=default;
    virtual void jump_sound(std::uint16_t)=0;
};
// $79BE..$7A66. A1 byte6 is mapped_jump; held input comes from C486.
inline void update_player_jump(ActorState& actor,const PlayerJumpInput& input,PlayerJumpServices& services) {
    auto flags=actor.byte(124);
    const auto sustain=[&] {
        if(input.held_jump&&(actor.byte(122)&128)&&!input.c514)
            actor.longword(62,actor.longword(62)+0x2ee0u);
    };
    if(!input.mapped_jump) {
        flags=static_cast<std::uint8_t>(flags&~8u);actor.byte(124,flags);
        sustain();return;
    }
    if(flags&16){sustain();return;}
    if((flags&8)||!(flags&1)||input.c514)return;
    if(actor.word(70)==24) {actor.byte(126,static_cast<std::uint8_t>(actor.byte(126)|32));return;}
    actor.byte(124,static_cast<std::uint8_t>((flags|24u)&~1u));actor.byte(122,255);
    if(input.controlled_type==20) {actor.longword(62,0xc0000);services.jump_sound(84);}
    else {actor.longword(62,0x65e00);services.jump_sound(13);}
}
}
