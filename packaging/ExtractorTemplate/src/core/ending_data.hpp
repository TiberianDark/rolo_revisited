#pragma once
#include <array>
#include <cstdint>
namespace rolo::ending_data {
struct Sprite{unsigned source,width,height,offset;};
inline std::array<Sprite,15> sprites{};
inline std::array<std::uint8_t,18048> pixels{};
inline std::array<std::uint8_t,214> good_text{};
inline std::array<std::uint8_t,261> bad_text{};
inline std::array<std::uint16_t,16> white{};
inline std::array<std::uint16_t,16> black{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
inline std::array<std::uint16_t,16> bad_palette{};
}

