#pragma once
#include "core/actor_allocation.hpp"
#include "core/player_trigger_pool.hpp"
#include "core/actor_markers.hpp"
#include "core/actor_reservations.hpp"
namespace rolo {
struct SmallRecordPool {
    std::array<std::array<std::uint8_t,34>,32> records{};
    std::array<std::uint32_t,33> free_keys{};std::size_t cursor{};
    // $2816: only pointer stack/cursor reset; payload records remain stale.
    void initialize(){cursor=0;for(unsigned i=0;i<32;++i)free_keys[i]=0xffff64aeu+34*i;free_keys[32]=0;}
};
// $27DA: original five reset calls in order, with distinct native pools.
inline void reset_world_actor_resources(ActorPool& actors,SmallRecordPool& small,
        PlayerTriggerPool& triggers,DeferredMarkerPool& deferred,ActorReservationPool& reservations){
    actors.initialize_free_stack();small.initialize();triggers.initialize();deferred.initialize();reservations.initialize();
}
}
