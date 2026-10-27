#pragma once
#include "core/player_acceleration.hpp"
#include "core/player_direction_input.hpp"
#include "core/level1_terrain_data.hpp"
namespace rolo {
// Initial Rolo C502=7E58/C506=7EE0. Other identities/pointer mutations need other bindings.
struct RoloSlopeMotionServices:PlayerAccelerationServices {
    const PlayerMotionTables* live_tables{};
    RoloSlopeMotionServices()=default;
    explicit RoloSlopeMotionServices(const PlayerMotionTables& tables):live_tables(&tables){}
    PlayerSlopeMotion slope_motion(std::uint8_t slot,bool reverse) override {
        if(slot>=64)throw std::out_of_range("Native six-bit slope read domain");
        const bool run=live_tables&&*live_tables==PlayerMotionTables::Run;
        const auto& words=run?(reverse?level1_terrain_data::rolo_slope_run_reverse:level1_terrain_data::rolo_slope_run_forward)
                            :(reverse?level1_terrain_data::rolo_slope_reverse:level1_terrain_data::rolo_slope_forward);
        return {words[slot*2],words[slot*2+1]};
    }
};
}
