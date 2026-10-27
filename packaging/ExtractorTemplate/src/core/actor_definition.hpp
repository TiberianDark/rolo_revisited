#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
// Immutable definition bytes; callback values are identifiers for native binding.
struct ActorDefinition {
    std::uint32_t key{};
    std::array<std::uint8_t,34> data{};
    constexpr std::uint8_t byte(std::size_t i) const {return data.at(i);}
    constexpr std::uint16_t word(std::size_t i) const {return static_cast<std::uint16_t>((byte(i)<<8)|byte(i+1));}
    constexpr std::uint32_t longword(std::size_t i) const {return (static_cast<std::uint32_t>(word(i))<<16)|word(i+2);}
    constexpr ActorChainDefinition allocation() const {
        return {{key,longword(12),word(8),word(10),word(16),byte(27)},longword(0),word(4)};
    }
};
}
