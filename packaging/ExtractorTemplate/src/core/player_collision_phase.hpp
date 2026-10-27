#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct PlayerCollisionPhaseState {std::uint8_t c524{},f2bc{};std::uint32_t controlled{};};
struct PlayerCollisionPhaseView {const std::uint8_t& c524;const std::uint8_t& f2bc;const std::uint32_t& controlled;};
struct PlayerCollisionPhaseServices {
    virtual ~PlayerCollisionPhaseServices()=default;
    virtual std::uint16_t collision_definition_type(const ActorState&)=0;
    // Native bindings must preserve each helper's live actor convention.
    virtual void ceiling_collision(std::uint32_t& live_actor)=0;
    virtual void floor_collision(std::uint32_t& live_actor)=0;
    virtual void side_collision(std::uint32_t& live_actor)=0;
    virtual void collision_followup_a(std::uint32_t& live_actor)=0;
    virtual void collision_followup_b(std::uint32_t& live_actor)=0;
};
// $785C..$78B8: local phase orchestration, helper implementations are required.
inline void player_collision_phase(ActorPool& pool,PlayerCollisionPhaseView state,
        PlayerCollisionPhaseServices& services) {
    if(state.c524||state.f2bc)return;
    auto live_actor=state.controlled;auto& actor=pool.resolve(live_actor);
    if((actor.byte(124)&32)||(actor.byte(125)&8))return;
    const auto saved_height=actor.word(38);
    if(services.collision_definition_type(actor)==20)actor.word(38,32);
    services.ceiling_collision(live_actor); //8376
    services.floor_collision(live_actor); //84F4
    services.side_collision(live_actor); //827A
    services.collision_followup_a(live_actor); //842E
    services.collision_followup_b(live_actor); //8482
    // Reload controlled pointer after helpers, exactly as78AC does.
    pool.resolve(state.controlled).word(38,saved_height);
}
inline void player_collision_phase(ActorPool& pool,PlayerCollisionPhaseState& state,PlayerCollisionPhaseServices& services) {
    player_collision_phase(pool,PlayerCollisionPhaseView{state.c524,state.f2bc,state.controlled},services);
}
}
