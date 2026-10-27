#pragma once
#include "core/player_movement_phase.hpp"
#include "core/player_input_phase.hpp"
#include "core/player_slope_impact.hpp"
#include "core/held_object_release.hpp"
#include "core/rolo_slope_motion.hpp"
namespace rolo {
struct PlayerLifecycleServices {
    virtual ~PlayerLifecycleServices()=default;
    virtual void player_death_transition()=0;
    virtual void player_companion_action(std::uint16_t,ActorPool&,std::uint32_t&)=0;
};
// All routines resolve the same actor pool. Movement.contact owns contact gates;
// action globals receive a read context at the input call, not a second world state.
struct PlayerActorWorld final:PlayerMovementServices,PlayerInputPhaseServices,PlayerImpactServices,HeldObjectServices {
    ActorPool& pool;ActorReservationPool& reservations;
    PlayerMovementState& movement;PlayerInputPhaseState& input;HeldObjectState& held;
    std::span<const ActorDefinition> definitions;ActorAllocationServices& allocation;
    std::uint16_t& sound_command;PlayerLifecycleServices& lifecycle;
    RoloSlopeMotionServices slopes;
    // Requested demo correction: Level18's shallow ripple tiles use the standard
    // flat-ground horizontal response. This is not a ROM-fidelity certificate.
    bool standard_shallow_ground{};
    PlayerActorWorld(ActorPool& p,ActorReservationPool& r,PlayerMovementState& m,
            PlayerInputPhaseState& i,HeldObjectState& h,std::span<const ActorDefinition> d,
            ActorAllocationServices& a,std::uint16_t& s,PlayerLifecycleServices& l)
        :pool(p),reservations(r),movement(m),input(i),held(h),definitions(d),allocation(a),sound_command(s),lifecycle(l),slopes(i.direction.tables){}
    PlayerSlopeMotion slope_motion(std::uint8_t slot,bool reverse) override{
        if(standard_shallow_ground&&movement.controlled_type==4&&slot==3)return slopes.slope_motion(1,false);
        return slopes.slope_motion(slot,reverse);
    }
    void held_object_release() override{held.base=input.base_key;release_held_object(pool,reservations,held,*this);}
    void player_interactions(std::uint32_t& key) override{player_slope_impact(pool.resolve(key),*this);}
    void player_input_actions(std::uint32_t& key) override {
        input.controlled_key=movement.controlled;input.controlled_type=movement.controlled_type;input.c514=movement.c514;
        input.action.c513=movement.c513;
        input.action.c547=held.stored_count; // Original C547: snapshot after release, before action input.
        input.action.c519=movement.contact.hit_gate_c519;input.action.c51a=movement.contact.hit_gate_c51a;
        input.action.c51b=movement.contact.hit_gate_c51b;
        player_input_phase(pool,key,input,*this);
    }
    void begin_death_transition() override{lifecycle.player_death_transition();}
    void companion_action(std::uint16_t type,ActorPool& p,std::uint32_t& key) override{lifecycle.player_companion_action(type,p,key);}
    void jump_sound(std::uint16_t effect) override{sound_command=effect;}
    void action_sound(std::uint16_t effect) override{sound_command=effect;}
    void impact_sound(std::uint16_t effect) override{sound_command=effect;}
    const ActorDefinition& held_definition(const ActorState& actor) override {
        for(const auto& d:definitions)if(d.key==actor.longword(4))return d;
        throw std::logic_error("Shared player held definition unbound");
    }
    std::uint32_t spawn_released_object(std::uint32_t definition,std::uint32_t x,std::uint32_t y,std::uint8_t facing) override {
        return allocate_actor_chain(pool,{definition,x,y,0,0,facing},allocation).returned_key;
    }
};
}
