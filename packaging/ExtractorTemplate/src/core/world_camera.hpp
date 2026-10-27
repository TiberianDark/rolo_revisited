#pragma once
#include "core/world_map.hpp"
#include <bit>
namespace rolo {
struct WorldCameraState {std::uint32_t x{},y{};};
// 63A6 valid world-coordinate domain: WORD deltas below signed magnitude8000.
// Normalize the major axis to10000; minor division truncates. Equality would
// overflow DIVU's16-bit quotient, selecting the original10000 fallback.
struct WorldCameraVector {std::uint32_t x{},y{};std::uint16_t distance{};};
inline WorldCameraVector world_camera_vector(std::uint16_t from_x,std::uint16_t from_y,
        std::uint16_t target_x,std::uint16_t target_y){
    const auto dx=static_cast<std::int16_t>(static_cast<std::uint16_t>(target_x-from_x));
    const auto dy=static_cast<std::int16_t>(static_cast<std::uint16_t>(target_y-from_y));
    if(dx==-32768||dy==-32768)throw std::out_of_range("Unproved world camera signed magnitude");
    const auto ax=static_cast<unsigned>(dx<0?-int(dx):dx),ay=static_cast<unsigned>(dy<0?-int(dy):dy);
    const auto major=std::max(ax,ay),minor=std::min(ax,ay);if(!major)return {};
    const auto quotient=(minor<<16)/major;
    auto x=ax>=ay?65536u:quotient,y=ay>ax?65536u:quotient;
    if(dx<0)x=0u-x;if(dy<0)y=0u-y;
    return {x,y,static_cast<std::uint16_t>(major)};
}
inline WorldCameraState initialize_world_camera(const WorldMapCursor& cursor,std::uint16_t width,std::uint16_t height){
    const auto initial=initialize_world_map_camera(cursor,width,height);return {std::uint32_t(initial.x)<<16,std::uint32_t(initial.y)<<16};
}
// 9E98: paused camera follows C5BA instead of C4E0. Caller supplies that chosen
// actor's coordinates. C494/C498 are scratch targets, not persistent state.
inline void update_world_camera(WorldCameraState& state,const WorldMapCursor& selected,
        std::uint16_t width,std::uint16_t height){
    const auto target=initialize_world_map_camera(selected,width,height);
    const auto vector=world_camera_vector(static_cast<std::uint16_t>(state.x>>16),static_cast<std::uint16_t>(state.y>>16),target.x,target.y);
    const unsigned exponent=vector.distance<=10?0:vector.distance<=20?1:vector.distance<=40?2:3;
    state.x+=vector.x<<exponent;state.y+=vector.y<<exponent;
}
inline WorldMapCamera world_camera_integer(const WorldCameraState& state){return {static_cast<std::uint16_t>(state.x>>16),static_cast<std::uint16_t>(state.y>>16)};}
}
