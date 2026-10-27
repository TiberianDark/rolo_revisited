#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct RoloActionGlobals {std::uint8_t c520{},c487{},c547{},c51c{},c513{},c519{},c51a{},c51b{};};
struct RoloActionServices {
    virtual ~RoloActionServices()=default;
    virtual void action_sound(std::uint16_t)=0;
};
// $7AD8..$7B74: type4 action path. No invented head attack timer.
inline void rolo_action_press(ActorPool& pool,std::uint32_t base_key,
        const RoloActionGlobals& globals,RoloActionServices& services) {
    if(globals.c520||globals.c487!=255)return;
    auto& base=pool.resolve(base_key);
    if(!base.word(70)){base.word(72,65535);base.longword(106,0);}
    auto& head=pool.resolve(base.longword(84));const auto mode=head.byte(46);
    if(!globals.c547&&!(mode&128)) {
        if(mode||!globals.c51c||globals.c513)return;
        base.byte(52,255);services.action_sound(23);return;
    }
    if(static_cast<std::uint8_t>(globals.c519+globals.c51a+globals.c51b)||head.word(70)==44)return;
    head.byte(126,static_cast<std::uint8_t>(head.byte(126)|2));head.word(70,44);
    services.action_sound(56);
}
// $7AB4..$7AD8: reached base-actor release tail, after the type8 branch.
inline void rolo_action_release(ActorState& base) {
    if(!base.byte(52))return;
    base.byte(52,0);
    if(!base.word(70)){base.word(72,65535);base.longword(106,0);}
}
}
