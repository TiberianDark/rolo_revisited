#pragma once
#include "core/actor_definition.hpp"
namespace rolo::level1_object_data {
inline std::array<ActorDefinition,177> definitions{};
inline std::array<std::uint32_t,24> collectible_spawn_table{};
inline std::array<std::uint32_t,37> enemy_spawn_table{};
inline std::array<std::uint32_t,2> special_spawn_table{};
inline std::array<std::uint32_t,13> generic_spawn_table{};
inline std::array<std::uint32_t,4> companion_spawn_table{};
inline std::array<std::uint32_t,128> ride_slope_forward{};
inline std::array<std::uint32_t,128> ride_slope_reverse{};
inline std::array<std::uint32_t,8> phase_boss_offsets{};
inline std::array<std::uint32_t,9> choreography_spawn{};
inline std::array<std::uint32_t,18> choreography_permutations{};
inline std::array<std::uint8_t,9> choreography_groups{};
inline std::array<std::uint16_t,8> choreography_tiles{};
inline std::array<std::uint32_t,17> spawner_rewards{};
inline std::array<std::uint8_t,6> spawner_directions{};
inline std::array<std::uint8_t,48> boss29_part_offsets{};
inline std::array<std::uint16_t,15> common_flash_palette{};
inline std::array<std::uint8_t,24> companion_menu_navigation{};
}
