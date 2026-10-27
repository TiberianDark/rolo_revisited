#pragma once
#include "core/level1_companion_selection.hpp"
#include "core/level1_object_data.hpp"
namespace rolo {
struct CompanionMenuState {std::uint16_t selector=3;std::uint8_t ready{},closing{},slide{},previous_complement{},exit_wait{};};
struct CompanionMenuServices {
    virtual ~CompanionMenuServices()=default;
    virtual void companion_menu_begin()=0; //687A,3900,9514,260A,25A8 publication.
    virtual void companion_menu_slide(std::uint16_t vdp_register)=0; //9200|slide
    virtual void companion_menu_palette_in()=0; //2158 including3934.
    virtual void companion_menu_highlight()=0; //3934 after navigation.
    virtual bool companion_menu_select(std::uint16_t)=0; // Original choice subroutine.
    virtual void companion_menu_accept()=0; //684E,6864,4CB8,7292,72A2,6960,6AA6,21C6.
    virtual void companion_menu_resume()=0; //C444=1C6C.
    virtual void companion_menu_sound(std::uint16_t)=0;
    virtual void companion_menu_exit()=0; //1F84 waits all input release then C444=1A6E.
};
inline void begin_level1_companion_menu(CompanionMenuState& state,CompanionMenuServices& services){
    state.ready=0;state.closing=0;state.slide=0;state.previous_complement=0;state.exit_wait=0;services.companion_menu_begin();
}
// $1E44/$2130. Physical bits follow the original C488 order, edge mask C544.
inline void update_level1_companion_menu(CompanionMenuState& state,std::uint8_t physical_pressed,CompanionMenuServices& services){
    if(state.exit_wait){if(!physical_pressed){state.exit_wait=0;services.companion_menu_exit();}return;}
    if(state.closing){if(state.slide){--state.slide;services.companion_menu_slide(static_cast<std::uint16_t>(0x9200|state.slide));}else services.companion_menu_resume();return;}
    if(state.slide!=28){++state.slide;services.companion_menu_slide(static_cast<std::uint16_t>(0x9200|state.slide));}
    else if(!state.ready){state.ready=255;services.companion_menu_palette_in();}
    auto fresh=static_cast<std::uint8_t>(physical_pressed&state.previous_complement);state.previous_complement=static_cast<std::uint8_t>(~physical_pressed);
    if(fresh&128){services.companion_menu_sound(15);if(state.selector==5)state.exit_wait=255;return;}
    if(fresh&112){
        services.companion_menu_sound(15);if(state.selector==5)return;
        if(!services.companion_menu_select(state.selector))return;
        state.closing=255;if(state.slide==28)services.companion_menu_accept();return;
    }
    unsigned direction;
    if(fresh&8)direction=3;else if(fresh&4)direction=2;else if(fresh&2)direction=1;else if(fresh&1)direction=0;else return;
    if(!state.ready)return;if(state.selector>=6)throw std::out_of_range("Unbound companion menu selector");
    const auto next=level1_object_data::companion_menu_navigation[state.selector*4+direction];if(next&128)return;
    state.selector=next;services.companion_menu_sound(15);services.companion_menu_highlight();
}
}
