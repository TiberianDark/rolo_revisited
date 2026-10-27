#pragma once
#include "core/actor_state.hpp"
namespace rolo {
enum class ActorChainFlag {set,clear,toggle};
// $9504/$9514/$9524. Caller supplies a nonzero valid finite linked chain.
// A malformed cycle has no original terminating contract and is not certified.
template<ActorChainFlag operation,class Pool>
void actor_chain_flag(Pool& pool,std::uint32_t key){
 do{auto& actor=pool.resolve(key);const auto flag=actor.byte(125);
 if constexpr(operation==ActorChainFlag::set)actor.byte(125,flag|2u);
 else if constexpr(operation==ActorChainFlag::clear)actor.byte(125,flag&~2u);
 else actor.byte(125,flag^2u);
 key=actor.longword(84);
 }while(key);
}
}
