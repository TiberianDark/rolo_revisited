#pragma once
#include "core/actor_contact_family.hpp"
#include "core/actor_allocation.hpp"
#include "core/level_reset_state.hpp"
#include "core/level1_reward_curve.hpp"
namespace rolo {
struct ActorSceneServices:ActorDirectContactServices,RewardCurveServices {
 virtual ActorAllocationResult scene_allocate(ActorAllocationRequest)=0;
 virtual bool contact_probe_nonnegative(ActorState&)=0;
 virtual bool shrunken_contact(ActorState&,std::uint16_t,std::uint16_t)=0;
 virtual void collect_default(ActorState&)=0;
};
// $E300: allocation changes original A5 to returned tail, even on partial failure.
inline void update_actor_timed_projectile(ActorPool&pool,std::uint32_t&live,std::uint32_t&context,ActorSceneServices&s){
 auto&a=pool.resolve(live);if(a.byte(117))return;update_actor_contact_only(a,s);actor_integer_x_step(a,1);s.choose_direction(a);
 const auto timer=std::uint16_t(a.word(46)-1);a.word(46,timer);if(!(timer&0x8000))return;a.word(46,100);
 const auto result=s.scene_allocate({0x14d46,a.longword(12),a.longword(16),0,context,0});live=result.tail;
}
inline void update_actor_gated_collectible(ActorState&a,std::uint8_t timer,ActorSceneServices&s){if(!timer)s.collect_default(a);}
// $DD74: query/gates precede the shrunken-contact service and shared latch writes.
inline void update_actor_contact_latch(ActorState&a,std::uint8_t&f2bc,std::uint8_t&c511,ActorSceneServices&s){
 if(!s.contact_probe_nonnegative(a))return;const auto&c=s.controlled_actor();if(c.byte(122)&128||!(c.byte(124)&16))return;
 if(!s.shrunken_contact(a,32,16))return;f2bc=255;a.byte(50,255);c511=0;
}
// $D3FE: signedBYTE absolute index spans0..128 in the original shared state page.
inline void reveal_scene_piece(ActorPool&pool,LevelResetState&state,std::uint32_t&live,std::uint32_t context,ActorSceneServices&s){
 const auto signed_index=std::int8_t(state.bytes[0xf26f]);const unsigned index=signed_index<0?unsigned(-int(signed_index)):unsigned(signed_index);
 auto&flag=state.bytes[0xc558+index];const bool already=flag&1;flag|=1;if(already)return;
 const auto controlled=(std::uint32_t(state.word(0xc4e0))<<16)|state.word(0xc4e2);const auto&a=pool.resolve(controlled);
 const auto result=s.scene_allocate({0x14482,a.longword(12),a.longword(16),0,context,0});live=result.tail;if(!result.success)return;
 live=result.head;auto&piece=pool.resolve(live);piece.word(70,4);start_reward_curve(piece,296,41,0xffffc551,s);
}
}
