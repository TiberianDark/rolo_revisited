#pragma once
#include "core/world_route.hpp"
#include "core/player_input.hpp"
namespace rolo {
struct WorldLevelAdmission {
    std::uint16_t current_f2f6{},saved_f2f0{};
    std::uint8_t entry_f26d{};
};
// 1ACA..1AFC and1C46: fresh A/B/C tails to admission before Start handling.
// Even a moving-route admission attempt skips the Start toggle that update.
// Selector resolution is supplied only after the original pointer-zero gate.
template<class Selector>
inline bool finish_world_input(WorldRouteState& route,WorldLevelAdmission& admission,
        const PlayerInputMapping& buttons,Selector&& selector){
    if(!route.pause&&((buttons.physical[5]|buttons.physical[6]|buttons.physical[7])&1)){
        if(route.pointer)return false;
        const auto selected=selector();admission.current_f2f6=selected;admission.saved_f2f0=selected;
        admission.entry_f26d=0;return true; // Caller invokes the1CEE rebuild contract.
    }
    if(buttons.physical[4]&1)route.pause=static_cast<std::uint8_t>(~route.pause);
    return false;
}
}
