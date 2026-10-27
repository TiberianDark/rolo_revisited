#pragma once
#include <array>
#include <cstdint>
namespace rolo::world_route_data {
struct Descriptor {std::uint32_t pointer;std::uint8_t negate_x,negate_y;};
inline constexpr std::uint32_t pool_start=0xa2ec,pool_end=0xa368;
inline std::array<Descriptor,32> descriptors{};
inline std::array<std::uint8_t,124> route_bytes{};
struct Stream {std::uint32_t pointer,terminator;std::uint16_t pairs;};
inline std::array<Stream,6> streams{};
}
