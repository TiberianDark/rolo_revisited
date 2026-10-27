#pragma once
#include "core/actor_definition.hpp"
namespace rolo::dynamic_platform_data {
inline std::array<ActorDefinition,11> definitions{};
inline constexpr std::uint32_t definition_key(unsigned bank,unsigned macro){return bank==1&&macro==84?0xffff6000u:0xffff6100u+bank*256+macro;}
inline constexpr bool is_definition(std::uint32_t key){for(const auto&d:definitions)if(d.key==key)return true;return false;}
}
