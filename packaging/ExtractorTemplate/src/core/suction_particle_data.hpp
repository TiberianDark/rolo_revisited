#pragma once
#include <array>
#include <cstdint>
namespace rolo::suction_particle_data {
inline std::array<std::uint8_t,4608> patterns{};
struct Graphic {unsigned width,height,frame_size,first,palette;};
inline std::array<Graphic,3> graphics{};
}
