#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_contact.hpp"
#include "core/actor_chain_flag.hpp"
namespace rolo {
struct PlayerContactResolutionState {
    ContactGlobals& contact;std::uint8_t& effect_c516;
    std::uint8_t& exit_c518;std::uint8_t& protection_c5cd;std::uint8_t& transition_c522;
    std::uint8_t& frozen_c524;
    std::array<std::uint32_t,3>& companions;const std::uint16_t& controlled_type;
    const std::uint32_t& controlled;
};
struct PlayerContactResolutionServices {
    virtual ~PlayerContactResolutionServices()=default;
    virtual void contact_resolution_sound(std::uint16_t)=0;
    virtual void contact_exit_transition()=0; //953C63FA thenstate165E/C461clear
    virtual void contact_rolo_death_transition()=0; //9560 tail1D94
    virtual void contact_companion_death_transition()=0; //9564 native9642
};
// $95DE..$9642. Reverse three companion slots; DBNE stops at first nonzero.
inline void apply_player_contact_injury(ActorPool& pool,PlayerContactResolutionState state){
    if(state.controlled_type==4){
        for(int i=2;i>=0;--i){
            auto& key=state.companions[static_cast<std::size_t>(i)];if(!key)continue;
            auto& companion=pool.resolve(key);key=0;
            companion.longword(42,0xadd0);companion.byte(125,static_cast<std::uint8_t>(companion.byte(125)|4));
            companion.byte(47,0);companion.byte(46,0);
            auto& controlled=pool.resolve(state.controlled);controlled.byte(122,255);controlled.longword(62,0x65e00);
            state.contact.action_gate_c511=255;state.contact.hit_gate_c51b=255;return;
        }
    }
    state.contact.hit_gate_c519=255;state.contact.action_gate_c511=255;
}
// $9534..$95DE. Returns true for the original tail1CEE transition, retaining516/517.
inline bool resolve_player_contact(ActorPool& pool,PlayerContactResolutionState state,PlayerContactResolutionServices& services){
    if(state.exit_c518)services.contact_exit_transition();
    if(state.contact.hit_gate_c51a){
        if(state.controlled_type==4){services.contact_rolo_death_transition();return false;}
        services.contact_companion_death_transition();
    }
    if(!state.contact.hit_gate_c519&&state.effect_c516){
        services.contact_resolution_sound(0x16);state.contact.hit_gate_c519=255;
        state.frozen_c524=0;
        state.contact.action_gate_c511=255;
    }
    if(!state.protection_c5cd&&!state.contact.action_gate_c511&&state.contact.action_latch_c517){
        services.contact_resolution_sound(0x16);apply_player_contact_injury(pool,state);
    }
    if(state.transition_c522)return true;
    state.effect_c516=0;state.contact.action_latch_c517=0;return false;
}
struct PlayerBlinkState {std::uint16_t delay_c50a{},counter_c50c{};};
// $948A..$9534. Bit1 at actor125 is presentation blink; chain read stays live.
inline void update_player_contact_blink(ActorPool& pool,std::uint32_t controlled,
        std::uint8_t f2bc,ContactGlobals& contact,PlayerBlinkState& state){
    if(f2bc)return;
    enum class Operation{Clear,Toggle};Operation operation=Operation::Clear;
    if(!contact.hit_gate_c519&&contact.action_gate_c511){
        if(contact.action_gate_c511&128){contact.action_gate_c511=1;state.delay_c50a=0x600;state.counter_c50c=state.delay_c50a;return;}
        state.counter_c50c=static_cast<std::uint16_t>(state.counter_c50c-0x100);
        if(signed_word(state.counter_c50c)>=0)return;
        state.counter_c50c=state.delay_c50a;operation=Operation::Toggle;
        state.delay_c50a=static_cast<std::uint16_t>(state.delay_c50a-0x40);
        if(signed_word(state.delay_c50a)<0){contact.action_gate_c511=0;operation=Operation::Clear;}
    }
    if(operation==Operation::Toggle)actor_chain_flag<ActorChainFlag::toggle>(pool,controlled);
    else actor_chain_flag<ActorChainFlag::clear>(pool,controlled);
}
}
