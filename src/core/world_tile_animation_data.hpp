#pragma once
#include <array>
#include <cstdint>
namespace rolo::world_tile_animation_data {
inline std::array<std::uint8_t,1024> patterns{};
inline std::array<std::uint8_t,10> sequences{};
struct Track {unsigned cache_byte_offset,delay,first,bytes,sequence_first,sequence_count;};
inline std::array<Track,2> tracks{};
}
