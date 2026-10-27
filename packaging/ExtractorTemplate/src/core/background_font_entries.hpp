#pragma once
#include "core/backward_asset_codec.hpp"
#include "core/world_map.hpp"
#include "core/actor_state.hpp"
namespace rolo {
struct BackgroundEntryResult{std::vector<std::uint8_t>bytes;std::uint32_t restored_source{},restored_destination{};};
inline BackgroundEntryResult load_background_entry(std::span<const std::uint8_t>rom,std::uint32_t entry,std::uint16_t offset,ActorState&plane,std::uint8_t&reward,std::uint32_t saved_source,std::uint32_t saved_destination,std::span<const std::uint8_t>flags){
 reward=std::uint8_t(entry>>24);const auto source=entry&0xffffff;plane.longword(34,0xffffdc44);BackgroundEntryResult result;result.restored_source=saved_source;result.restored_destination=saved_destination;
 if(!offset){result.bytes=generate_world_map_background(flags);return result;}
 if(source+4>rom.size())throw std::out_of_range("Background source header");if(rom[source]=='M'&&rom[source+1]=='A'&&rom[source+2]=='P'){if(source+2048>rom.size())throw std::out_of_range("Raw background copy extent");result.bytes.assign(rom.begin()+source,rom.begin()+source+2048);}else result.bytes=decode_backward_asset(rom,source).bytes;return result;
}
struct FontPlaneUpload{std::vector<std::uint8_t>bytes;std::uint32_t source{},destination{},count{},command{};};
inline FontPlaneUpload prepare_text_font_upload(std::span<const std::uint8_t>rom,std::uint32_t incoming_count){FontPlaneUpload r;r.bytes=decode_backward_asset(rom,0x46d4c).bytes;const auto word=std::uint16_t(r.bytes.size());const int signed_size=word<32768?int(word):int(word)-65536;const auto half=signed_size>=0?signed_size/2:-((1-signed_size)/2);r.source=0xffff0000;r.destination=64;r.count=(incoming_count&0xffff0000u)|std::uint16_t(half);r.command=0x40000000;return r;}
}
