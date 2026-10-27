#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_contact.hpp"
#include "core/player_acceleration.hpp"
#include "core/player_forces.hpp"
#include "core/player_position.hpp"
namespace rolo {
struct PlayerMovementState {
    std::uint32_t controlled{},drag{};
    std::uint8_t c513{},c510{},c514{},c524{},c481{},c5cb{},c51d{},c50f{};
    std::uint16_t controlled_type{},camera_y{},c542{};
    ContactGlobals contact;PlayerPositionGlobals bounds;
};
struct PlayerMovementServices:PlayerAccelerationServices {
    virtual void held_object_release()=0; //7B74
    virtual void player_interactions(std::uint32_t& live_actor)=0; //8C24
    virtual void player_input_actions(std::uint32_t& live_actor)=0; //78B8
    virtual void begin_death_transition()=0; //63FA followed by C444=15AA
};
// $7748..$785C. Full local normal/damage phase; required helpers are explicit.
inline void player_movement_phase(ActorPool& pool,PlayerMovementState& state,PlayerMovementServices& services) {
    auto live=state.controlled;auto& initial=pool.resolve(live);
    initial.longword(46,0);initial.longword(20,initial.longword(12));initial.longword(24,initial.longword(16));
    state.c514=(state.c513&&!state.c510)?255:0;
    if(state.c524)return;
    const auto forces=[&] {
        auto& actor=pool.resolve(live);
        player_acceleration(actor,services);player_slope_vertical_motion(actor,state.c514);
        player_gravity(actor,{state.c514,state.contact.hit_gate_c519,state.contact.hit_gate_c51a,state.c481});
        integrate_player_position(actor,state.bounds);
    };
    if(!state.contact.hit_gate_c519) {
        services.held_object_release();live=state.controlled;
        player_horizontal_drag(pool.resolve(live),state.drag);
        services.player_interactions(live);services.player_input_actions(live);
        if(pool.resolve(live).byte(125)&8)return;
        forces();state.contact.vertical_gate_c515=pool.resolve(live).byte(122);return;
    }
    if(state.contact.hit_gate_c519&128) {
        auto& actor=pool.resolve(live);actor.byte(122,255);actor.longword(62,0x65e00);
        state.contact.hit_gate_c519=10;
    }
    player_horizontal_drag(pool.resolve(live),state.drag);forces();
    auto& actor=pool.resolve(live);
    if(actor.longword(20)==actor.longword(12)){actor.byte(121,0);actor.longword(58,0);}
    if(!(actor.byte(124)&1)) {
        const auto limit=static_cast<std::uint16_t>(state.camera_y+224);
        if(limit>actor.word(16))return;
    }
    state.contact.hit_gate_c519=static_cast<std::uint8_t>(state.contact.hit_gate_c519-1);
    if(state.contact.hit_gate_c519&&!(state.contact.hit_gate_c519&128))return;
    state.contact.hit_gate_c51a=255;
    if(state.controlled_type==4) {
        if(state.c5cb)return;
        state.c51d=static_cast<std::uint8_t>(state.c51d-1);
        if(!(state.c51d&128))return;
        services.begin_death_transition();return;
    }
    state.c542=static_cast<std::uint8_t>(3+state.c50f);
}
}
