#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
struct TileMetadataPair {std::uint8_t first{},second{};std::uint16_t after_pair{};};
inline TileMetadataPair read_tile_metadata_pair(std::span<const std::uint8_t> data,std::uint16_t at){
 if(static_cast<unsigned>(at)+2>data.size())throw std::out_of_range("Unproved metadata table extent");
 return {data[at],data[at+1],static_cast<std::uint16_t>(at+2)};
}
// Original879A,87DC,87F6: data lookup APIs, no CPU/ROM instruction execution.
inline TileMetadataPair vertical_tile_metadata(std::span<const std::uint8_t> data,std::uint16_t tile){return read_tile_metadata_pair(data,(tile&511)*8+((tile&0x1000)?2:0));}
inline TileMetadataPair first_lateral_tile_metadata(std::span<const std::uint8_t> data,std::uint16_t tile){return read_tile_metadata_pair(data,(tile&511)*8+4);}
inline TileMetadataPair second_lateral_tile_metadata(std::span<const std::uint8_t> data,std::uint16_t tile){return read_tile_metadata_pair(data,(tile&511)*8+6);}
}
