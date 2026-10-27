#pragma once
#include <array>
#include <cstdint>
namespace rolo::actor_pattern_data {
inline std::array<std::uint8_t,158048> bytes{};
struct Frame {std::uint32_t source,width,height,offset,size;};
inline std::array<Frame,406> frames{};
}
