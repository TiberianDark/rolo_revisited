#pragma once
#include "core/actor_state.hpp"
#include <span>
namespace rolo {
struct ScoreEffectServices {
    virtual ~ScoreEffectServices()=default;
    virtual std::uint32_t score_effect_value(const ActorState&)=0; // Definition long28, a score here, not a pointer.
    virtual void add_score(std::uint32_t)=0; // $997E, threshold/life/HUD work remains required.
};
// $EF68..$EFA8; original16-byte wave at$E468 is typed immutable data.
inline void update_score_effect(ActorState& actor,std::span<const std::int8_t,16> wave,
                                ScoreEffectServices& services) {
    if(!actor.byte(46)) {
        actor.byte(46,255);actor.byte(50,0x32);
        services.add_score(services.score_effect_value(actor));
    }
    const auto dx=wave[actor.byte(50)&15];
    actor.word(12,static_cast<std::uint16_t>(actor.word(12)+dx));
    actor.word(16,static_cast<std::uint16_t>(actor.word(16)-1));
    actor.byte(50,static_cast<std::uint8_t>(actor.byte(50)-1));
    if(actor.byte(50)&128)actor.byte(116,255);
}
}
