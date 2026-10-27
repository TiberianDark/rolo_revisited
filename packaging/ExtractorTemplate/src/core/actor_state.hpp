#pragma once
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>

namespace rolo {
// Original actor data layout, not CPU memory or an instruction interpreter.
// A fresh allocation's selective clearing is a separate lifecycle contract.
struct ActorState {
    std::array<std::uint8_t,130> fields{};
    std::uint8_t byte(std::size_t offset) const {return fields.at(offset);}
    std::uint16_t word(std::size_t offset) const {
        return static_cast<std::uint16_t>((byte(offset)<<8)|byte(offset+1));
    }
    std::uint32_t longword(std::size_t offset) const {
        return (static_cast<std::uint32_t>(word(offset))<<16)|word(offset+2);
    }
    void byte(std::size_t offset,std::uint8_t value) {fields.at(offset)=value;}
    void word(std::size_t offset,std::uint16_t value) {
        byte(offset,static_cast<std::uint8_t>(value>>8));byte(offset+1,static_cast<std::uint8_t>(value));
    }
    void longword(std::size_t offset,std::uint32_t value) {
        word(offset,static_cast<std::uint16_t>(value>>16));word(offset+2,static_cast<std::uint16_t>(value));
    }
};
inline constexpr std::int16_t signed_word(std::uint16_t value) {return std::bit_cast<std::int16_t>(value);}
inline constexpr std::int32_t signed_long(std::uint32_t value) {return std::bit_cast<std::int32_t>(value);}
}
