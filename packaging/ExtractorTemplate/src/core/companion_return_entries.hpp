#pragma once
#include "core/level1_companion_selection.hpp"
namespace rolo {
inline void return_companion_control_to_base(ActorPool&pool,Level1ProgressState&progress,CompanionControlState&control,CompanionControlServices&s){progress.action_c510=0;select_level1_controlled_actor(control.base,pool,control,s);}
inline void choose_companion_follow_mode(ActorPool&pool,Level1CompanionState&companions,Level1ProgressState&progress,CompanionControlState&control,CompanionControlServices&s,bool free){return_companion_control_to_base(pool,progress,control,s);companions.c50f=std::uint8_t(free);set_level1_companion_callbacks(companions,pool,free?0xaa4a:0xab28);}
inline void return_companion_menu_noop(){}
inline void return_actor_dispatch_noop(){}
}
