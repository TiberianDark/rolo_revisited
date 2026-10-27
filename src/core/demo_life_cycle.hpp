#pragma once
#include "core/level1_enemy_slice.hpp"
#include <memory>
namespace rolo {
// Native host handoff for the existing $9534 -> $1D94 request. Movement has
// already decremented C51D; rebuilding must not spend another life. This binds
// persistent game state, not the still-pending original fade/device cadence.
inline std::unique_ptr<Level1EnemySlice> rebuild_after_player_death(const Level1EnemySlice& previous){
    if(!previous.death_requested||previous.game_over_requested)
        throw std::logic_error("Restart requires the original live-level death request");
    auto next=std::make_unique<Level1EnemySlice>(&previous.progress.flags,previous.score,
        previous.movement.c51d,previous.progress.selector,&previous.checkpoint);
    next->awards=previous.awards;
    next->completion.world_x=previous.completion.world_x;
    next->completion.world_y=previous.completion.world_y;
    next->completion.saved_x=previous.completion.saved_x;
    next->completion.saved_y=previous.completion.saved_y;
    return next;
}
}
