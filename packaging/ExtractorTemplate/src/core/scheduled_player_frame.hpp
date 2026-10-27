#pragma once
#include "core/bound_player_frame.hpp"
#include "core/actor_scheduler.hpp"
#include "core/first_enemy.hpp"
#include "core/player_trigger_scan.hpp"
#include "core/player_post_motion.hpp"
namespace rolo {
struct NativeFirstEnemyCallbacks final:ActorCallbackServices {
    ActorPool& pool;FirstEnemyServices& enemy;ActorCallbackServices& other;
    NativeFirstEnemyCallbacks(ActorPool& p,FirstEnemyServices& e,ActorCallbackServices& fallback):pool(p),enemy(e),other(fallback){}
    void invoke_actor_callback(std::uint32_t identity,std::uint32_t callback) override {
        if(callback==0xb566){update_first_enemy(pool.resolve(identity),enemy);return;}
        if(callback==0xa84c)return; // Proven literal RTS, not an unresolved stub.
        other.invoke_actor_callback(identity,callback);
    }
};
struct ScheduledPlayerFrameServices:BoundPlayerFrameServices {
    DeferredMarkerPool& markers;ActiveActorList& active;ActorScheduleState& schedule;
    ActiveActorServices& lifetimes;ActorCallbackServices& callbacks;
    const std::uint16_t& reference_x;const std::uint16_t& reference_y;
    PlayerTriggerServices& triggers;
    const std::uint8_t& terrain_bank;PlayerPostMotionServices& post_motion;
    ScheduledPlayerFrameServices(ActorPool& p,PlayerMovementState& m,PlayerInputPhaseState& i,
        PlayerFrameHistory& h,PlayerHistorySelectorServices& selectors,const ActorTerrain& t,
        PlayerTerrainResponseServices& surfaces,std::uint16_t& previous,DeferredMarkerPool& marker_pool,
        ActiveActorList& list,ActorScheduleState& scheduling,ActiveActorServices& lifetime,
        ActorCallbackServices& functions,const std::uint16_t& x,const std::uint16_t& y,PlayerTriggerServices& trigger_services,
        const std::uint8_t& bank,PlayerPostMotionServices& mutation)
        :BoundPlayerFrameServices(p,m,i,h,selectors,t,surfaces,previous),markers(marker_pool),active(list),schedule(scheduling),
        lifetimes(lifetime),callbacks(functions),reference_x(x),reference_y(y),triggers(trigger_services),terrain_bank(bank),post_motion(mutation){}
    void player_post_motion() override{player_post_motion_terrain(pool.resolve(movement.controlled),movement.controlled_type,terrain_bank,post_motion);}
    void scan_active_actors() override{rebuild_active_actor_list(pool,markers,active,reference_x,reference_y,lifetimes);}
    void update_actors() override {
        schedule.controlled=movement.controlled;schedule.base=input.base_key;
        update_actor_callbacks(pool,schedule,active,callbacks);
    }
    void post_presentation() override {
        const auto& actor=pool.resolve(movement.controlled);
        const auto x=actor.word(12),y=actor.word(16);
        scan_player_triggers(x,y,reference_x,reference_y,16,triggers);
    }
};
}
