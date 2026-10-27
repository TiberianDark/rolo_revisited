#pragma once
#include "core/sound_stream_loading.hpp"
namespace rolo {
inline void initialize_original_sound_resource(SoundInterfaceState&s,SoundStreamState&stream,std::span<const std::uint8_t>rom,std::uint8_t version,SoundInterfacePorts&p){bootstrap_sound_driver(s,stream,rom,version,p,true,0x7c37e,0x480);}
}
