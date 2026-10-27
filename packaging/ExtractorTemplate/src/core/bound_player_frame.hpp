#pragma once
#include "core/shared_player_frame.hpp"
#include "core/player_frame_history.hpp"
#include "core/player_terrain_response.hpp"
namespace rolo {
// Remaining post-motion, active scan, actor update and spawning phases are pure
// required services. These three bindings call original translated routines.
struct BoundPlayerFrameServices:SharedPlayerFrameServices {
    ActorPool& pool;PlayerMovementState& movement;PlayerInputPhaseState& input;
    PlayerFrameHistory& history;PlayerHistorySelectorServices& history_selectors;
    const ActorTerrain& terrain;PlayerTerrainResponseServices& surfaces;std::uint16_t& previous_x_shift;
    BoundPlayerFrameServices(ActorPool& p,PlayerMovementState& m,PlayerInputPhaseState& i,
            PlayerFrameHistory& h,PlayerHistorySelectorServices& selectors,const ActorTerrain& t,
            PlayerTerrainResponseServices& s,std::uint16_t& previous)
        :pool(p),movement(m),input(i),history(h),history_selectors(selectors),terrain(t),surfaces(s),previous_x_shift(previous){}
    void post_collision() override{record_player_frame_history(history,input.main_state,pool.resolve(input.base_key),history_selectors);}
    void player_link_phase() override{player_airborne_count(pool.resolve(movement.controlled),movement.c524);}
    void contact_phase() override {
        update_player_terrain_response(pool.resolve(movement.controlled),terrain,
            {movement.drag,input.direction.override_acceleration,previous_x_shift},surfaces);
    }
};
}
