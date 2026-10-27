#pragma once
#include "core/player_jump.hpp"
#include "core/player_direction_input.hpp"
#include "core/rolo_action.hpp"
namespace rolo {
struct PlayerInputPhaseState {
    PlayerDirectionState direction;
    RoloActionGlobals action;
    std::uint32_t main_state{},controlled_key{},base_key{};
    std::uint16_t controlled_type{};
    std::uint8_t c514{};
};
struct PlayerInputPhaseServices:PlayerJumpServices,RoloActionServices {
    virtual void companion_action(std::uint16_t type,ActorPool&,std::uint32_t& live_key)=0;
};
// $7A66..$7AD8. The release tail changes A0 to the base actor.
inline void player_action_dispatch(ActorPool& pool,std::uint32_t& live_key,
        PlayerInputPhaseState& state,PlayerInputPhaseServices& services) {
    auto& actor=pool.resolve(live_key);
    actor.byte(125,static_cast<std::uint8_t>(actor.byte(125)&~8u));
    if(state.direction.mapped[7]) {
        if(state.controlled_type==4) {
            if(!state.action.c520&&state.action.c487==255)live_key=state.base_key;
            rolo_action_press(pool,state.base_key,state.action,services);
        } else if(state.controlled_type==8||state.controlled_type==16)
            services.companion_action(state.controlled_type,pool,live_key);
        return;
    }
    if(state.controlled_type==8&&pool.resolve(state.controlled_key).byte(53)) {
        const auto flags=actor.byte(126);
        actor.byte(126,static_cast<std::uint8_t>(flags&~2u));
        if(flags&2)actor.word(70,0);
    }
    live_key=state.base_key;
    rolo_action_release(pool.resolve(live_key));
}
// $78B8..$79BE: switch request, jump, saved-pointer action, direction.
// C480 is the mapped input array here, so its byte6 is also C486.
inline void player_input_phase(ActorPool& pool,std::uint32_t& live_key,
        PlayerInputPhaseState& state,PlayerInputPhaseServices& services) {
    if(state.direction.mapped[4]&&state.main_state==0x1c6c)state.main_state=0x1e20;
    const auto jump=state.direction.mapped[6];
    update_player_jump(pool.resolve(live_key),{jump,jump,state.c514,state.controlled_type},services);
    const auto saved_key=live_key;
    state.action.c487=state.direction.mapped[7];
    player_action_dispatch(pool,live_key,state,services);
    live_key=saved_key; // MOVEM restores A0/A1 even when action selected the base.
    player_direction_input(pool.resolve(live_key),state.direction);
}
}
