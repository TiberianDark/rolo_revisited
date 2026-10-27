#pragma once
#include "core/animation.hpp"
#include "core/entrance_data.hpp"
#include "core/actor_state.hpp"
#include <algorithm>

namespace rolo {
constexpr std::uint32_t replace_integer(std::uint32_t value, std::uint16_t integer) {
    return (static_cast<std::uint32_t>(integer)<<16)|(value&0xffffu);
}
struct EntranceObject {
    std::uint32_t definition{}, x{}, y{}, velocity_x{}, velocity_y{};
    std::uint16_t delay{}, selector{};
    std::uint8_t facing{}, direction_x{}, direction_y{}, clip{};
    AnimationState animation;
};
struct EntranceState {
    // Original allocation order, excluding four cages marked inactive at setup.
    std::array<EntranceObject,6> objects{{
        {0x13ecc,0x01de0000,0x00f10000,0,0,0,0,0xff},
        {0x13eee,0x01de0000,0x00f10000,0,0,0,0,0xff},
        {0x13f76,0x00ef0000,0x00a20000,0,0,250},
        {0x13f54,0x02100000,0x00ef0000,0,0,200,0,0xff},
        {0x13f32,0x01690000,0x00ed0000,0,0,0,56},
        {0x13f10,0x004e0000,0x00f90000,0x2000,0x400,1,52}
    }};
    std::uint16_t camera_x{100}, camera_y{100};
    std::uint32_t tick{};
    AnimationRandom random;
};
// $17BC/$17EA/$1822: word decrement, signed test, undo negative decrement.
inline bool entrance_delay_ready(std::uint16_t& delay) {
    delay=static_cast<std::uint16_t>(delay-1);
    if (signed_word(delay)>=0) return false;
    delay=static_cast<std::uint16_t>(delay+1); return true;
}
inline void clip_entrance_object(EntranceObject& object, const EntranceState& state) {
    const int x=signed_word(static_cast<std::uint16_t>(object.x>>16));
    const int y=signed_word(static_cast<std::uint16_t>(object.y>>16));
    const int cx=signed_word(state.camera_x),cy=signed_word(state.camera_y);
    object.clip=static_cast<std::uint8_t>((x<cx-80?4:0)|(x>cx+400?8:0)|
        (y<cy-32?1:0)|(y>cy+304?2:0));
    // $2A6C adds the wider exclusion rectangle when outside the near rectangle.
    if (object.clip) object.clip=static_cast<std::uint8_t>(object.clip|
        (x<cx-368?64:0)|(x>cx+688?128:0)|(y<cy-240?16:0)|(y>cy+464?32:0));
}
inline void walk_entrance(EntranceObject& object, std::uint16_t stop, std::uint16_t idle) {
    const auto decremented=static_cast<std::uint16_t>((object.x>>16)-1);
    const bool arrived=signed_word(decremented)<=signed_word(stop);
    object.x=replace_integer(object.x,arrived?stop:decremented);
    object.selector=arrived?idle:4;
}
// $CD8E and $CFCE, including the signed upward/descending velocity state.
inline void entrance_gravity(EntranceObject& object) {
    if (!(object.clip&14)) {
        if (object.direction_y>=0x80) {
            object.velocity_y-=0x6000;
            if (signed_long(object.velocity_y)<0) {
                object.velocity_y=0u-object.velocity_y;object.direction_y=1;
            }
        } else {
            object.direction_y=1;
            if (signed_long(object.velocity_y)<0xf0000)
                object.velocity_y=static_cast<std::uint32_t>(std::min<std::int64_t>(signed_long(object.velocity_y+0x6000),0xf0000));
        }
    }
    if (object.direction_x) object.x+=object.direction_x>=0x80 ? 0u-object.velocity_x : object.velocity_x;
    if (object.direction_y) object.y+=object.direction_y>=0x80 ? 0u-object.velocity_y : object.velocity_y;
}
// One original initial-state dispatcher call, in $169A..$16B2 order.
// A call corresponds to one VBlank-driven update; no invented real-time delta.
inline AnimationResult update_entrance(EntranceState& state) {
    if (state.tick>=850) return AnimationResult::ScopeComplete;
    // $2A12 scans positions BEFORE the movement routines.
    for (auto& object:state.objects) clip_entrance_object(object,state);
    auto& elephant=state.objects[0]; auto& head=state.objects[1];
    auto& squirrel=state.objects[2]; auto& rabbit=state.objects[3]; auto& beaver=state.objects[5];
    walk_entrance(elephant,278,60);
    if (entrance_delay_ready(rabbit.delay)) walk_entrance(rabbit,320,0);
    if (entrance_delay_ready(squirrel.delay)) {
        entrance_gravity(squirrel); squirrel.selector=12;
        if (signed_word(static_cast<std::uint16_t>(squirrel.y>>16))>=241) {
            squirrel.y=replace_integer(squirrel.y,241);squirrel.selector=0;
        }
    }
    if (entrance_delay_ready(beaver.delay)) {
        beaver.x=std::min(beaver.x+beaver.velocity_x,0x00ae0000u);
        beaver.y=std::max(beaver.y-beaver.velocity_y,0x00ed0000u);
    }
    // $885A..$88C8 no-input entrance attachment path. Global interactions are later scope.
    head.x=replace_integer(head.x,static_cast<std::uint16_t>(elephant.x>>16));
    head.y=replace_integer(head.y,static_cast<std::uint16_t>(elephant.y>>16));
    head.selector=elephant.selector;head.facing=elephant.facing;
    head.direction_x=elephant.direction_x;head.direction_y=elephant.direction_y;
    for (auto& object:state.objects) {
        const auto status=update_animation(object.animation,entrance_data::data,
            object.definition,object.selector,object.velocity_x,state.random);
        if (status!=AnimationResult::Ok) return status;
    }
    ++state.tick; return AnimationResult::Ok;
}
struct EntranceDraw {
    std::uint32_t graphics{};
    int x{},y{};
    std::uint16_t width{},height{};
    bool flip_x{};
};
inline std::optional<EntranceDraw> entrance_draw(const EntranceObject& object, const EntranceState& state) {
    if (object.animation.current<0) return std::nullopt;
    const auto& frame=entrance_data::frames[object.animation.current];
    const bool facing=(object.facing&8)!=0;
    const auto selected=facing?frame.right_graphics:frame.left_graphics;
    const auto graphics=selected?selected:(facing?frame.left_graphics:frame.right_graphics);
    const int offset_x=facing?-frame.offset_x:frame.offset_x;
    return EntranceDraw{graphics,signed_word(static_cast<std::uint16_t>(object.x>>16))+offset_x-frame.width/2-signed_word(state.camera_x),
        signed_word(static_cast<std::uint16_t>(object.y>>16))+frame.offset_y-frame.height-signed_word(state.camera_y),
        frame.width,frame.height,selected==0};
}
} // namespace rolo

