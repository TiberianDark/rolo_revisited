#pragma once
#include "core/terrain_descriptor.hpp"
#include <array>
namespace rolo::level4_terrain_data {
inline constexpr std::uint8_t reward_selector=8; // $37EA background pointer high byte, F26F.
inline std::array<std::uint8_t,1138> map_bytes{};
inline std::array<std::uint16_t,1322> macro_tiles{};
inline std::array<std::uint16_t,1440> quad_words{};
inline std::array<std::uint8_t,28320> bank_patterns{};
inline std::array<std::uint8_t,3424> common_patterns{};
inline std::array<std::uint8_t,192> background_map_bytes{};
inline std::array<std::uint16_t,64> palette_words{};
inline std::array<std::uint8_t,58> history_selector_bytes{};
inline std::array<std::uint8_t,172> post_motion_table_bytes{};
inline std::array<std::uint32_t,128> rolo_slope_forward{};
inline std::array<std::uint32_t,128> rolo_slope_reverse{};
inline std::array<std::uint32_t,128> rolo_slope_run_forward{};
inline std::array<std::uint32_t,128> rolo_slope_run_reverse{};
inline std::array<TerrainMacroDefinition,85> macros{};
inline constexpr std::uint16_t width=2592,height=1472;
}
