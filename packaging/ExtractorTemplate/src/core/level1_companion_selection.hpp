#pragma once
#include "core/level1_companions.hpp"
#include "core/actor_contact.hpp"
#include "core/actor_chain_flag.hpp"
#include "core/base_actor_waiting.hpp"
namespace rolo {
struct CompanionControlState {std::uint32_t controlled{},base{},saved46{},saved50{};std::uint16_t type=4;};
struct CompanionControlServices {
    virtual ~CompanionControlServices()=default;
    virtual const ActorDefinition& companion_control_definition(const ActorState&)=0;
};
// $20A2: restore old actor work fields, save new actor work fields, then publish
// controlled/type and clear blink through the entire base actor linked chain.
inline void select_level1_controlled_actor(std::uint32_t key,ActorPool& pool,
        CompanionControlState& control,CompanionControlServices& services){
    auto& old=pool.resolve(control.controlled);old.longword(46,control.saved46);old.longword(50,control.saved50);
    auto& next=pool.resolve(key);control.saved46=next.longword(46);control.saved50=next.longword(50);
    control.type=services.companion_control_definition(next).word(10);control.controlled=key;next.longword(42,0xa84c);
    if(control.base)actor_chain_flag<ActorChainFlag::clear>(pool,control.base);
}
// Menu choices0/1/2 dispatch1FCE/200E/204E to slots3/2/1; choices3/4 return
// control to Rolo and select grounded/free follow modes1F98/1FB2. Failed
// selection returns false as the original MOVEQ-1/N result, without mutation.
inline bool select_level1_companion_menu_choice(std::uint16_t choice,ActorPool& pool,
        Level1CompanionState& companions,Level1ProgressState& progress,CompanionControlState& control,
        CompanionControlServices& services){
    if(choice<=2){
        const auto slot=static_cast<std::uint8_t>(3-choice);
        if(progress.action_c510==slot)return true;
        if(progress.action_c510)return false;
        const auto key=companions.slots[slot-1];if(!key)return false;
        progress.action_c510=slot;set_level1_companion_callbacks(companions,pool,0xa8bc);
        set_base_actor_waiting(pool.resolve(control.base));select_level1_controlled_actor(key,pool,control,services);return true;
    }
    if(choice==3||choice==4){
        progress.action_c510=0;select_level1_controlled_actor(control.base,pool,control,services);
        companions.c50f=static_cast<std::uint8_t>(choice==4);set_level1_companion_callbacks(companions,pool,choice==4?0xaa4a:0xab28);return true;
    }
    if(choice==5)return true; // Caller supplies resume/menu close, no actor mutation.
    throw std::out_of_range("Unbound companion menu choice");
}
}
