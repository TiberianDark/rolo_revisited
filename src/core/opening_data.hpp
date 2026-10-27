#pragma once
#include <array>
#include <cstdint>
namespace rolo::opening_data {
inline std::array<std::uint8_t,4178> startup{};
inline std::array<std::uint8_t,3072> font{};
inline std::array<std::uint16_t,64> colour{};
inline std::array<std::uint16_t,64> photo{};
inline std::array<std::uint8_t,35840> back{};
inline std::array<std::uint8_t,35840> front{};
inline std::array<std::uint8_t,15360> logo{};
inline std::array<std::uint8_t,35840> photo_back{};
inline std::array<std::uint8_t,35840> photo_front{};
inline std::array<std::uint8_t,30464> sprite_pixels{};
struct Sprite{unsigned source,width,height,offset;};
inline std::array<Sprite,34> sprites{};
}
