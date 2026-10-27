#pragma once
#include <array>
#include <cstdint>
namespace rolo::forest_tile_animation_data {
inline std::array<std::uint8_t,4096> patterns{};
inline std::array<std::uint8_t,32> sequences{};
struct Track {unsigned cache_byte_offset,delay,first,bytes,sequence_first,sequence_count;};
inline std::array<Track,6> tracks{};
}
