#pragma once
#include "core/actor_common_callbacks.hpp"
#include <array>
namespace rolo {
inline std::array<std::uint8_t,4> actor_phase_cycle_delays{};
// $E120. Contact's direct-hit callback precedes all live timer/phase reads.
inline void update_actor_phase_cycle(ActorState& actor,ActorDirectContactServices& services){
    if(services.player_contact(actor))services.hurt_controlled_actor(actor);
    const auto timer=static_cast<std::uint8_t>(actor.byte(47)-1);actor.byte(47,timer);
    if(!(timer&128))return;
    const auto phase=static_cast<std::uint8_t>((actor.byte(48)+1)&3);
    actor.byte(48,phase);actor.byte(47,actor_phase_cycle_delays[phase]);actor.byte(46,255);
}
// $E11A falls into the same cycle after setting orientation bit4.
inline void update_actor_flipped_phase_cycle(ActorState& actor,ActorDirectContactServices& services){
    actor.byte(119,actor.byte(119)|16);update_actor_phase_cycle(actor,services);
}
}
