#pragma once
#include "core/actor_state.hpp"
namespace rolo {
// $B1C6..$B1D6: C4E4 base identity supplied by the native world.
inline void set_base_actor_waiting(ActorState& base){base.longword(42,0xa84e);}
}
