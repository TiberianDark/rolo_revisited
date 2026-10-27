#pragma once
#include "core/animation.hpp"
#include "core/actor_state.hpp"
namespace rolo {
struct ActorAnimationEffects:AnimationEffects {
    ActorState& actor;
    explicit ActorAnimationEffects(ActorState& value):actor(value){}
    void animation_retire() override {
        actor.byte(116,255);
        actor.byte(125,static_cast<std::uint8_t>(actor.byte(125)|4));
    }
    // The sound pipeline supplies animation_sound; no silent default.
};
}
