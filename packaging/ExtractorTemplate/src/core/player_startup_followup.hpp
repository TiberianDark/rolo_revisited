#pragma once
#include "core/level_reset_state.hpp"
#include "core/actor_allocation.hpp"
namespace rolo {
struct PlayerStartupServices {virtual ~PlayerStartupServices()=default;virtual ActorAllocationResult startup_allocate(ActorAllocationRequest)=0;};
// $766A: failed allocation selects original boot continuation before any resets.
inline bool initialize_level_player(ActorPool&pool,LevelResetState&state,std::uint32_t context,PlayerStartupServices&services){
 const auto result=services.startup_allocate({0x13ecc,0x1a40000,0xc80000,0,context,0});if(!result.success)return false;
 const auto key=result.head;auto&actor=pool.resolve(key);
 auto store_long=[&](unsigned at,std::uint32_t value){state.word(at,std::uint16_t(value>>16));state.word(at+2,std::uint16_t(value));};
 store_long(0xc4e0,key);store_long(0xc4e4,key);actor.word(68,0);state.word(0xc4e8,4);state.word(0x6000,0);
 for(unsigned i=0;i<3;++i)store_long(0x6402+i*4,0);
 for(unsigned at:{0xc50eu,0xc520u,0xc51cu,0xc547u,0xc510u,0xc50fu,0xc545u,0xc515u,0xc513u})state.bytes[at]=0;
 for(unsigned at:{0xc53au,0xc53eu,0xc54cu,0xc548u,0xc4eau,0xc4eeu,0xc4f2u,0xc4f6u,0xc4fau})store_long(at,0);
 state.word(0xc526,0);state.word(0xc542,3);return true;
}
struct ScoreFollowupState {std::uint32_t base{},followup{},allocation_context{};std::uint8_t override_c512{};};
struct ScoreFollowupServices {virtual ~ScoreFollowupServices()=default;virtual ActorState& score_base(std::uint32_t)=0;virtual std::uint32_t allocate_score_followup(ActorAllocationRequest)=0;virtual void pickup_sound(std::uint16_t)=0;virtual void collect_score_actor(ActorState&)=0;};
inline void spawn_score_followup(ScoreFollowupState& state,ScoreFollowupServices&services){
 auto&base=services.score_base(state.base);const auto result=services.allocate_score_followup({0x14928,base.longword(12),base.longword(16),0,state.allocation_context,0});
 state.followup=result;if(result)state.override_c512=255;
}
inline void collect_score_with_followup(ActorState&actor,ScoreFollowupState&state,ScoreFollowupServices&services){
 services.pickup_sound(64);services.collect_score_actor(actor);spawn_score_followup(state,services);
}
}
