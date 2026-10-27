#pragma once
#include "core/actor_state.hpp"

namespace rolo {
struct DefeatDefinition {
    std::uint16_t animation_selector{}; // Definition word32.
    std::uint32_t secondary_definition{}; // Definition long28, immutable asset key.
};
struct DefeatServices {
    virtual ~DefeatServices()=default;
    virtual DefeatDefinition defeat_definition(const ActorState&)=0;
    virtual void spawn_secondary(std::uint32_t definition,std::uint32_t x,std::uint32_t y)=0;
    virtual ActorState* next_linked_actor(const ActorState&)=0;
};
// $A84C is a single RTS: no actor update. Animation remains a separate phase.
// This is a native callback identifier, never executable ROM code.
constexpr std::uint32_t inactive_actor_callback=0xa84c;
inline void inactive_actor_update(ActorState&) {} // Exactly the documented RTS.

// $97AC..$97FE: callback/animation change and optional definition allocation.
inline ActorState* actor_hit_counter_zero(ActorState& actor,DefeatServices& services) {
    const auto definition=services.defeat_definition(actor);
    // Original A0 still points to definition data in this early-return case.
    if(definition.animation_selector==0) return nullptr;
    actor.word(70,definition.animation_selector);
    actor.longword(42,inactive_actor_callback);
    if(definition.secondary_definition)
        services.spawn_secondary(definition.secondary_definition,actor.longword(12),actor.longword(16));
    if(actor.longword(76)) return &actor;
    auto* current=&actor;
    while(auto* next=services.next_linked_actor(*current)) {
        current=next;
        current->word(70,definition.animation_selector);current->longword(42,inactive_actor_callback);
    }
    return current;
}
}
