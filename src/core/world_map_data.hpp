#pragma once
#include <array>
#include <cstdint>
namespace rolo::world_map_data {
inline std::array<std::uint8_t,650> foreground{};
inline std::array<std::uint8_t,20096> graphics{};
inline std::array<std::uint8_t,128> palette{};
inline std::array<std::uint8_t,2080> quads{};
inline std::array<std::uint8_t,2662> macros{};
inline std::array<std::uint8_t,224> common_quads{};
inline std::array<std::uint8_t,3424> common_patterns{};
inline std::array<std::uint8_t,160> return_coordinates{};
inline std::array<std::uint8_t,80> completion_selectors{};
inline std::array<std::uint8_t,128> completed_marker{};
inline std::array<std::uint8_t,14> palette_cycle{};
struct Piece {std::uint8_t selector,group,row,column,stride,xbase,edges;std::array<std::uint8_t,4> neighbors;};
inline std::array<Piece,80> pieces{};
}
