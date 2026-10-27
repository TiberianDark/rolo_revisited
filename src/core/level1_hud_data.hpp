#pragma once
#include "core/actor_definition.hpp"
namespace rolo::level1_hud_data {
inline constexpr ActorDefinition definition{0x1476e,{0,0,0,0,1,192,64,0,52,200,0,0,0,0,212,82,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}};
inline std::array<std::int16_t,23> wave{};
inline std::array<std::uint8_t,128> label{};
inline std::array<std::uint8_t,64> blank{};
inline std::array<std::uint8_t,64> icon{};
inline std::array<std::uint8_t,640> digits{};
}
