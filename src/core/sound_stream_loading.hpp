#pragma once
#include "core/audio_interface_state.hpp"
namespace rolo {
struct SoundStreamState{std::uint32_t base{},end{},source{},destination{};std::uint8_t page{};};
inline std::uint8_t sound_resource_byte(std::span<const std::uint8_t>data,std::uint32_t at){if(at>=data.size())throw std::out_of_range("Sound resource extent");return data[at];}
inline void upload_sound_resource(std::span<const std::uint8_t>data,std::uint32_t&source,std::uint32_t&destination,unsigned count,SoundInterfacePorts&p){for(unsigned i=0;i<count;++i)p.write_driver(static_cast<std::uint16_t>(destination++),sound_resource_byte(data,source++));}
// Driver code remains opaque bytes. No driver/ROM instructions are executed.
inline void bootstrap_sound_driver(SoundInterfaceState&s,SoundStreamState&stream,std::span<const std::uint8_t>rom,std::uint8_t version,SoundInterfacePorts&p,bool append=false,std::uint32_t extra=0,std::uint16_t count=0){
 const auto saved=s.status;s.enabled=0;s.seed_gate=(version&64)?255:0;stream.base=0;s.pending.fill(0);s.status=0x2700;p.reset_request(256);p.bus_request(256);std::uint32_t source=0x7e7a0,destination=0;upload_sound_resource(rom,source,destination,0x1120,p);if(append){source=extra;upload_sound_resource(rom,source,destination,count,p);}p.reset_request(0);p.bus_request(0);p.delay_iterations(501);p.reset_request(256);s.status=saved;
}
inline std::uint32_t preload_sound_stream(SoundStreamState&s,std::span<const std::uint8_t>rom,std::uint32_t source,std::uint32_t incoming_a1,SoundInterfacePorts&p){
 s.destination=0x1a00;s.page=0x1a;p.bus_request(256);p.write_driver(218,0x1a);auto target=s.destination;upload_sound_resource(rom,source,target,1024,p);p.bus_request(0);s.source=source;return incoming_a1;
}
inline void begin_sound_stream(SoundInterfaceState&g,SoundStreamState&s,std::span<const std::uint8_t>rom,std::uint32_t source,SoundInterfacePorts&p){
 if(source<4)throw std::out_of_range("Sound stream prefix");s.base=source;s.end=0;for(unsigned i=0;i<4;++i)s.end=(s.end<<8)|sound_resource_byte(rom,source-4+i);const auto saved=g.status;g.status=0x2700;(void)preload_sound_stream(s,rom,source,0,p);p.bus_request(256);p.write_driver(11,13);p.write_driver(10,0);p.bus_request(0);g.status=saved;g.enabled=255;
}
inline void refill_sound_stream(SoundInterfaceState&g,SoundStreamState&s,std::span<const std::uint8_t>rom,SoundInterfacePorts&p){
 if(!g.enabled)return;const auto saved=g.status;begin_sound_bus(g,p);if(p.read_driver(11)){const auto page=p.read_driver(218);if(page!=s.page){s.page=page;auto source=s.source,destination=s.destination;upload_sound_resource(rom,source,destination,256,p);s.source=source;s.destination=destination;if(source==s.end)s.source=s.base;if(static_cast<std::int32_t>(destination)>=0x1e00)s.destination=0x1a00;}}p.bus_request(0);g.status=saved;
}
}
