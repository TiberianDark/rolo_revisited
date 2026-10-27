#pragma once
#include "core/player_actor_world.hpp"
#include "core/player_terrain_collision.hpp"
#include "core/player_presentation.hpp"
namespace rolo {
struct SharedPlayerFrameServices {
    virtual ~SharedPlayerFrameServices()=default;
    virtual void player_post_motion()=0; //8C88
    virtual void scan_active_actors()=0; //29EE
    virtual void update_actors()=0; //A808
    virtual void post_collision()=0; //6796
    virtual void player_link_phase()=0; //881C
    virtual void contact_phase()=0; //9196
    virtual void post_presentation()=0; //925C
};
// $1C8E..$1CB8, bounded middle of the normal frame, not the complete frame.
// Explicit intervening services preserve actor updates BEFORE player collision.
inline void shared_player_frame_after_movement(ActorPool& pool,PlayerMovementState& movement,
        PlayerActorWorld& player,const std::uint8_t& f2bc,PlayerDefinedTerrainCollisionServices& collision,
        PlayerPresentationState& presentation,PlayerPresentationServices& graphics,SharedPlayerFrameServices& phases) {
    phases.player_post_motion();phases.scan_active_actors();phases.update_actors();
    player_collision_phase(pool,PlayerCollisionPhaseView{movement.c524,f2bc,movement.controlled},collision);
    phases.post_collision();phases.player_link_phase();phases.contact_phase();
    auto& selector=presentation.selector;
    selector.c510=movement.c510;selector.c513=movement.c513;selector.c520=player.input.action.c520;
    selector.c519=movement.contact.hit_gate_c519;selector.c51b=movement.contact.hit_gate_c51b;
    selector.c481=movement.c481;selector.c485=player.input.direction.mapped[5];
    presentation.c51a=movement.contact.hit_gate_c51a;presentation.c512=movement.contact.override_c512;
    update_player_presentation(pool,movement.controlled,player.input.base_key,presentation,graphics);
    //8934 can clear C51B: publish that mutation to the one contact state.
    movement.contact.hit_gate_c51b=selector.c51b;
    phases.post_presentation();
}
// Full middle retains the original movement-first entry. The live host can
// enter the tail after handling a movement-requested dispatcher transition.
inline void shared_player_frame_middle(ActorPool& pool,PlayerMovementState& movement,
        PlayerActorWorld& player,const std::uint8_t& f2bc,PlayerDefinedTerrainCollisionServices& collision,
        PlayerPresentationState& presentation,PlayerPresentationServices& graphics,SharedPlayerFrameServices& phases) {
    player_movement_phase(pool,movement,player);
    shared_player_frame_after_movement(pool,movement,player,f2bc,collision,presentation,graphics,phases);
}
}
