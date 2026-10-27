#pragma once
#include "core/world_cursor_data.hpp"
#include "core/world_map.hpp"
#include "core/actor_animation.hpp"
#include "core/actor_sprite.hpp"
namespace rolo {
// $9F72 successful allocation branch, after the shared native allocator.
inline void initialize_world_map_cursor(ActorState& actor){
    actor.byte(126,static_cast<std::uint8_t>(actor.byte(126)|2));
    actor.word(70,0);actor.word(48,0);actor.word(46,2);
}
inline AnimationResult animate_world_map_cursor(ActorState& actor){
    return update_actor_animation_from_definition(actor,0x13eaa,world_cursor_data::data);
}
inline ActorSpriteView world_map_cursor_sprite(const ActorState& actor,std::uint16_t camera_x,std::uint16_t camera_y){
    return actor_sprite_view(actor,camera_x,camera_y);
}
inline constexpr unsigned world_map_cursor_palette=(world_cursor_data::definition.word(6)>>13)&3;
}
