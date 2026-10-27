#pragma once
#include <array>
#include <cstdint>
namespace rolo::cavern_tile_animation_data {
inline std::array<std::uint8_t,2304> patterns{};
inline std::array<std::uint8_t,18> sequences{};
struct Track {unsigned cache_byte_offset,delay,first,bytes,sequence_first,sequence_count;};
inline std::array<Track,4> tracks{};
}
