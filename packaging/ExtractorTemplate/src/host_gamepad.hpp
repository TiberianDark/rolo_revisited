#pragma once
#include <SDL3/SDL.h>
#include <array>
#include <algorithm>
#include <cstdint>

namespace rolo {
// One active SDL-mapped gamepad, with startup discovery and hot-plug fallback.
class HostGamepad {
    SDL_Gamepad* pad_{};
    SDL_JoystickID selected_{};
    bool focused_=true;
    void discover(){
        if(pad_)return;
        int count=0;auto* ids=SDL_GetGamepads(&count);
        for(int i=0;i<count&&!pad_;++i)if(!selected_||selected_==ids[i])pad_=SDL_OpenGamepad(ids[i]);
        SDL_free(ids);
    }
public:
    explicit HostGamepad(SDL_JoystickID selected=0):selected_(selected){discover();}
    ~HostGamepad(){if(pad_)SDL_CloseGamepad(pad_);}
    HostGamepad(const HostGamepad&)=delete;
    HostGamepad& operator=(const HostGamepad&)=delete;
    void event(SDL_Event& event){
        if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST)focused_=false;
        if(event.type==SDL_EVENT_WINDOW_FOCUS_GAINED)focused_=true;
        if(event.type==SDL_EVENT_GAMEPAD_REMOVED){
            if(pad_&&SDL_GetGamepadID(pad_)==event.gdevice.which){SDL_CloseGamepad(pad_);pad_=nullptr;}
            discover();
        }
        if(event.type==SDL_EVENT_GAMEPAD_ADDED)discover();
        if(event.type!=SDL_EVENT_GAMEPAD_BUTTON_DOWN || !focused_ || !pad_ ||
           event.gbutton.which!=SDL_GetGamepadID(pad_))return;
        SDL_Keycode key=0;
        switch(event.gbutton.button){
        case SDL_GAMEPAD_BUTTON_START:key=SDLK_RETURN;break;
        case SDL_GAMEPAD_BUTTON_BACK:key=SDLK_P;break;
        case SDL_GAMEPAD_BUTTON_NORTH:key=SDLK_F6;break;
        case SDL_GAMEPAD_BUTTON_LEFT_SHOULDER:key=SDLK_PAGEUP;break;
        case SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER:key=SDLK_PAGEDOWN;break;
        default:break;
        }
        if(key){event={};event.type=SDL_EVENT_KEY_DOWN;event.key.key=key;event.key.down=true;event.key.repeat=false;}
    }
    std::uint8_t buttons()const{
        if(!focused_||!pad_||!SDL_GamepadConnected(pad_))return 0;
        auto b=[&](SDL_GamepadButton button){return SDL_GetGamepadButton(pad_,button);};
        const auto x=SDL_GetGamepadAxis(pad_,SDL_GAMEPAD_AXIS_LEFTX);
        const auto y=SDL_GetGamepadAxis(pad_,SDL_GAMEPAD_AXIS_LEFTY);
        constexpr int deadzone=10000;
        return std::uint8_t(((b(SDL_GAMEPAD_BUTTON_DPAD_UP)||y < -deadzone)?1:0)|
          ((b(SDL_GAMEPAD_BUTTON_DPAD_DOWN)||y > deadzone)?2:0)|
          ((b(SDL_GAMEPAD_BUTTON_DPAD_LEFT)||x < -deadzone)?4:0)|
          ((b(SDL_GAMEPAD_BUTTON_DPAD_RIGHT)||x > deadzone)?8:0)|
          (b(SDL_GAMEPAD_BUTTON_SOUTH)?16:0)|(b(SDL_GAMEPAD_BUTTON_WEST)?32:0)|
          (b(SDL_GAMEPAD_BUTTON_EAST)?64:0)|(b(SDL_GAMEPAD_BUTTON_START)?128:0));
    }
    auto keys()const{
        std::array<bool,SDL_SCANCODE_COUNT> result{};
        const bool* keyboard=SDL_GetKeyboardState(nullptr);
        std::copy_n(keyboard,result.size(),result.begin());
        const auto held=buttons();
        constexpr std::array<SDL_Scancode,8> codes{SDL_SCANCODE_UP,SDL_SCANCODE_DOWN,SDL_SCANCODE_LEFT,SDL_SCANCODE_RIGHT,SDL_SCANCODE_SPACE,SDL_SCANCODE_Z,SDL_SCANCODE_X,SDL_SCANCODE_RETURN};
        for(unsigned i=0;i<codes.size();++i)result[codes[i]]=result[codes[i]]||bool(held&(1<<i));
        return result;
    }
};
}
