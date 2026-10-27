#pragma once
#include "core/direction_vector_data.hpp"
#include <stdexcept>
namespace rolo {
struct ActorDirectionVector {std::uint32_t x{},y{};};
// $CA48..$CAB8: eight original octant entries, including LONG negation.
inline ActorDirectionVector actor_direction_octant(unsigned bank,unsigned octant,unsigned step){
    if(bank>=8||octant>=8||step>=8)throw std::out_of_range("Direction-vector selector domain");
    const auto& table=direction_vector_data::tables[bank];
    const auto at=(octant&1?8-step:step)*2;
    const auto a=table[at],b=table[at+1];
    switch(octant){
    case 0:return {a,0u-b};
    case 1:return {b,0u-a};
    case 2:return {b,a};
    case 3:return {a,b};
    case 4:return {0u-a,b};
    case 5:return {0u-b,a};
    case 6:return {0u-b,0u-a};
    default:return {0u-a,0u-b};
    }
}
// $CA0A: D1 selects original magnitude table1..8; D0 admits angles0..63.
// Result is signed fixed-point bits, preserving exact original lookup values.
inline ActorDirectionVector actor_direction_vector(std::uint16_t angle,std::uint16_t magnitude){
    if(angle>=64||magnitude<1||magnitude>8)throw std::out_of_range("Direction-vector input domain");
    return actor_direction_octant(magnitude-1,angle>>3,angle&7);
}
}
