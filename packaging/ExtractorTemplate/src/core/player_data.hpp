#pragma once
#include <array>
#include <cstdint>
namespace rolo::player_data {
inline constexpr int width=124,height=90;
inline std::array<std::uint16_t,11160> grid{};
inline std::array<std::uint8_t,4096> collision{};
inline std::array<std::uint8_t,1024> shapes{};
inline std::array<std::int32_t,34> walk_forward{};
inline std::array<std::int32_t,34> walk_reverse{};
inline std::array<std::int32_t,34> run_forward{};
inline std::array<std::int32_t,34> run_reverse{};
}
