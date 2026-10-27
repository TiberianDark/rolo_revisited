#pragma once
#include "core/actor_state.hpp"
#include "core/suction_particle_data.hpp"
#include <vector>
#include <stdexcept>
namespace rolo {
struct SuctionParticleSprite {std::int16_t x,y;unsigned graphic,phase;bool flip;};
struct SuctionParticles {
    std::uint8_t countdown{},phase{};
    std::vector<SuctionParticleSprite> sprites;
    // $5348..$546E. Pause state while inactive/injured, then decrement a signed
    // BYTE timer. Each three active calls advances the four-frame graphics.
    void step(const ActorState& base,const ActorState& head,std::uint8_t strength,
            std::uint8_t c519,std::uint8_t c51a,std::uint8_t c51b,std::uint16_t camera_x,std::uint16_t camera_y){
        sprites.clear();
        if(static_cast<std::uint8_t>(c519+c51a+c51b)||!base.byte(52))return;
        if(strength<1||strength>3)throw std::out_of_range("Original suction sprite strength domain");
        countdown=static_cast<std::uint8_t>(countdown-1);
        if(countdown&128){countdown=2;phase=static_cast<std::uint8_t>(phase+1);if(phase>3)phase=0;}
        const bool left=head.byte(118)&8;
        auto x=static_cast<std::uint16_t>(base.word(12)-camera_x+(left?-47:15)+(left?-int(head.word(32)):int(head.word(32))));
        auto y=static_cast<std::uint16_t>(base.word(16)-camera_y-17+head.word(34));
        for(unsigned i=0;i<strength;++i){
            sprites.push_back({static_cast<std::int16_t>(x),static_cast<std::int16_t>(y),i,phase,left});
            x=static_cast<std::uint16_t>(x+(left?-32:32));y=static_cast<std::uint16_t>(y-4);
        }
    }
};
}
