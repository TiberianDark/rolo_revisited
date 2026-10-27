#pragma once
#include "core/actor_allocation.hpp"
#include "core/animation.hpp"
namespace rolo {
struct RandomAnimationSpawnPosition {
    std::uint32_t x{},y{};std::uint16_t target_x_c494{},target_y_c498{};
};
// $100A2 before allocation. The two incoming upper WORDs become fractional
// position after MOVE.W/add/SWAP. They are explicit evidence inputs, not zero
// defaults. The signed RNG displacement also updates shared C494/C498.
inline RandomAnimationSpawnPosition random_animation_spawn_position(const ActorState& parent,
        std::uint16_t range,AnimationRandom& random,std::uint16_t incoming_d2_high,std::uint16_t incoming_d3_high){
    const auto upper=static_cast<std::uint16_t>(range+range);
    const auto dx=static_cast<std::uint16_t>(random.between(0,upper)-range);
    const auto dy=static_cast<std::uint16_t>(random.between(0,upper)-range);
    const auto x=static_cast<std::uint16_t>(parent.word(12)+parent.word(32)+dx);
    const auto y=static_cast<std::uint16_t>(parent.word(16)+parent.word(34)+dy);
    return {(std::uint32_t(x)<<16)|incoming_d2_high,(std::uint32_t(y)<<16)|incoming_d3_high,dx,dy};
}
// $10102 copies these fields only on successful allocation; a failed chain
// keeps the allocator's original partial-failure semantics.
inline ActorAllocationResult spawn_random_animation_actor(ActorState& parent,std::uint32_t definition,
        const RandomAnimationSpawnPosition& position,ActorPool& pool,ActorAllocationServices& services){
    const auto result=allocate_actor_chain(pool,{definition,position.x,position.y,0,0,parent.byte(118)},services);
    if(result.success){auto& actor=pool.resolve(result.head);actor.byte(121,parent.byte(121));actor.longword(58,parent.longword(58));actor.byte(122,parent.byte(122));actor.longword(62,parent.longword(62));}
    return result;
}
}
