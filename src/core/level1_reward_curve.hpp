#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct RewardCurveServices {
    virtual ~RewardCurveServices()=default;
    virtual void increment_reward_byte(std::uint32_t address)=0; // ADDQ.B1, not Boolean set.
    virtual std::uint16_t reward_camera_x()=0; // F362
    virtual std::uint16_t reward_camera_y()=0; // F366
};
// $B386. MULU and DIVU are unsigned, including wrapped relative distances.
inline void update_reward_curve(ActorState& actor,RewardCurveServices& services) {
    actor.byte(118,actor.byte(118)&~8u);
    auto remaining=static_cast<std::uint16_t>(actor.byte(56)-3);
    if(remaining&0x8000){remaining=0;services.increment_reward_byte(actor.longword(50));actor.byte(116,255);}
    actor.byte(56,static_cast<std::uint8_t>(remaining));
    actor.word(16,static_cast<std::uint16_t>(actor.word(18)+remaining));
    const auto product=std::uint32_t(remaining)*actor.word(46);const auto divisor=actor.word(48);
    if(!divisor)throw std::domain_error("Original reward curve DIVU zero divisor");
    const auto quotient=product/divisor;
    if(quotient>65535)throw std::domain_error("Original reward curve DIVU overflow domain");
    actor.word(12,static_cast<std::uint16_t>(actor.word(14)-quotient));
}
// $D2E2. Fraction words14/18 intentionally become target integer coordinates.
inline void start_reward_curve(ActorState& actor,std::uint16_t x,std::uint16_t y,
        std::uint32_t completion_byte,RewardCurveServices& services) {
    actor.byte(125,actor.byte(125)|4);actor.byte(126,actor.byte(126)|16);
    actor.longword(42,0xb386);actor.longword(50,completion_byte);
    actor.word(14,x);actor.word(46,static_cast<std::uint16_t>(x-actor.word(12)+services.reward_camera_x()));
    actor.word(18,y);const auto distance=static_cast<std::uint16_t>(0u-static_cast<std::uint16_t>(y-actor.word(16)+services.reward_camera_y()));
    actor.word(48,distance);actor.byte(56,static_cast<std::uint8_t>(distance));
    update_reward_curve(actor,services); // Immediate first step is part of the original call.
}
}
