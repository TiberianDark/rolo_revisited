#pragma once
#include <array>
#include <cstdint>
namespace rolo {
inline std::array<std::uint32_t,8> score_decimal_divisors{};
// $719A uses eight divisors at $71FA. The first digit is a BYTE even when
// the full unsigned input exceeds eight decimal digits; preserve that wrap.
inline std::array<std::uint8_t,8> score_decimal_bytes(std::uint32_t value){
    std::array<std::uint8_t,8> out{};
    for(unsigned i=0;i<8;++i){out[i]=static_cast<std::uint8_t>(value/score_decimal_divisors[i]);value%=score_decimal_divisors[i];}
    return out;
}
}
