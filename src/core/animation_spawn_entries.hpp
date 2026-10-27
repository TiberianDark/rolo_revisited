#pragma once
#include "core/animation_object_spawning.hpp"
namespace rolo {
struct AnimationSpawnCursor{std::uint32_t cursor{};std::uint16_t target_x{},target_y{};};
inline ActorAllocationResult animation_inherited_spawn(ActorState&parent,std::uint32_t definition,AnimationSpawnCursor&state,ActorPool&pool,ActorAllocationServices&services){
 const auto result=allocate_actor_chain(pool,{definition,parent.longword(12),parent.longword(16),0,0,parent.byte(118)},services);state.cursor+=8;
 if(result.success){auto&child=pool.resolve(result.head);child.byte(121,parent.byte(121));child.longword(58,parent.longword(58));child.byte(122,parent.byte(122));child.longword(62,parent.longword(62));}return result;
}
inline ActorAllocationResult animation_scattered_spawn(ActorState&parent,std::uint32_t definition,std::uint16_t range,AnimationRandom&random,std::uint16_t x_fraction,std::uint16_t y_fraction,AnimationSpawnCursor&state,ActorPool&pool,ActorAllocationServices&services){
 const auto position=random_animation_spawn_position(parent,range,random,x_fraction,y_fraction);state.target_x=position.target_x_c494;state.target_y=position.target_y_c498;const auto result=spawn_random_animation_actor(parent,definition,position,pool,services);state.cursor+=8;return result;
}
}
