#pragma once
#include <span>
#include <cstdint>
#include <stdexcept>
namespace rolo {
struct TerrainDescriptorPair {std::uint8_t bias{},shape{};};
// $87BC: no solidity gate; caller supplies raw tile WORD. Bit12 selects
// the opposite vertical descriptor from the floor reader.
inline TerrainDescriptorPair terrain_ceiling_descriptor(std::span<const std::uint8_t> collision,std::uint16_t tile){
    const auto at=(tile&511u)*8+((tile&4096)?0:2);
    if(at+2>collision.size())throw std::out_of_range("Ceiling descriptor extent");
    return {collision[at],collision[at+1]};
}
}
