#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
inline void disable_display_cache(std::uint16_t&cache){cache=0x8104;}
struct VideoSetupPorts{virtual ~VideoSetupPorts()=default;virtual void control(std::uint16_t)=0;};
inline void configure_original_video(VideoSetupPorts&p){for(auto word:{0x8230,0x8407,0x8334,0x857a,0x8d3c,0x8b00,0x8c81,0x9001})p.control(std::uint16_t(word));}
inline std::uint32_t clear_startup_work_ram(std::span<std::uint8_t>memory,std::uint32_t continuation){if(memory.size()<65536)throw std::out_of_range("Startup RAM extent");for(unsigned i=0;i<65536;++i)memory[i]=0;return continuation;}
inline std::uint8_t original_region_flag(std::uint8_t version){return version&128?255:0;}
struct DisplayFillRegisters{std::uint32_t value{},destination{},count{},command{},scratch{};};
inline DisplayFillRegisters prepare_byte_fill(DisplayFillRegisters r){const auto old=r;r.value=(old.destination&0xffff0000u)|((old.destination&255)*257);r.destination=old.value;r.count=(old.command&0xffff0000u)|std::uint16_t(old.command-1);r.command=old.count;r.scratch=(old.scratch&0xffffff00u)|(old.destination&255);return r;}
inline DisplayFillRegisters clear_plane_request(){return {0,0,31,0x40000000,0};}
struct AssetDecodeCursors{std::uint32_t source{},destination{};};
inline AssetDecodeCursors restore_asset_decode_cursors(std::uint32_t saved_source,std::uint32_t saved_destination){return {saved_source,saved_destination};}
struct TitleTextState{std::uint32_t frame_hook{},resume_text{},active_text{};std::uint16_t plane{},attributes{};std::uint8_t delay{},mode{};};
inline void initialize_title_text(TitleTextState&s){s.frame_hook=0x171c;s.plane=0xc000;s.active_text=s.resume_text?s.resume_text:0x13cb2;s.attributes=0x4000;s.delay=s.mode=0;}
}
