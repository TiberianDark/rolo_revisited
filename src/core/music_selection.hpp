#pragma once
#include "core/sound_stream_loading.hpp"
#include "core/backward_asset_codec.hpp"
#include <algorithm>
namespace rolo {
// Original FFFF8000 resource storage is represented by a native byte array;
// resource handles are offsets within that array, never executable addresses.
struct MusicSelectionState{std::uint8_t current=255,frame_gate{};SoundInterfaceState sound;SoundStreamState stream;std::array<std::uint8_t,32768>resource{};};
inline std::uint16_t terminate_music_resource(std::span<std::uint8_t>memory,std::uint16_t count){
 if(memory.size()<std::size_t(count)+5)throw std::out_of_range("Music terminator buffer extent");
 std::size_t cursor=4+count;auto remaining=count;
 for(;;){--cursor;if(memory[cursor]==0xfc)break;remaining=std::uint16_t(remaining-1);if(remaining==65535)break;}
 memory[cursor+1]=0x80;return std::uint16_t(remaining+1);
}
inline bool select_music_resource(MusicSelectionState&s,std::span<const std::uint8_t>rom,std::uint16_t id,std::uint8_t one_shot,SoundInterfacePorts&p){
 if(id>=33||std::uint8_t(id)==s.current)return false;s.current=std::uint8_t(id);s.frame_gate=0;s.sound.queued_command=std::uint16_t(0xff00|(s.sound.queued_command&255));stop_sound_interface(s.sound,p);
 std::uint32_t source=0;for(unsigned n=0;n<4;++n)source=(source<<8)|sound_resource_byte(rom,0x78a92+id*4+n);const auto decoded=decode_backward_asset(rom,source,32763);std::copy(decoded.bytes.begin(),decoded.bytes.end(),s.resource.begin()+4);auto count=std::uint16_t(decoded.bytes.size());if(one_shot)count=terminate_music_resource(s.resource,count);
 const auto end=std::uint32_t(4+((std::uint32_t(count)+255)&0xffffff00));for(unsigned n=0;n<4;++n)s.resource[n]=std::uint8_t(end>>(24-n*8));begin_sound_stream(s.sound,s.stream,s.resource,4,p);s.frame_gate=255;return true;
}
}
