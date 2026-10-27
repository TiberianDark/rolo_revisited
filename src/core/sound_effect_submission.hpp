#pragma once
#include "core/audio_interface_state.hpp"
namespace rolo {
struct SoundEffectPorts:SoundInterfacePorts{virtual void bootstrap()=0;};
inline void submit_original_sound_effect(SoundInterfaceState&s,std::uint32_t handle,std::span<const std::uint8_t>payload,unsigned channel,SoundEffectPorts&p){if(channel!=6&&channel!=7)throw std::out_of_range("Sound effect channel");if(!s.enabled)p.bootstrap();const auto saved=s.status;s.status=0x2700;p.bus_request(256);if(p.read_driver(12))s.pending[channel-6]=handle;else{if(payload.size()<23)throw std::out_of_range("Sound effect payload");p.write_driver(12,std::uint8_t(channel));for(unsigned i=0;i<23;++i)p.write_driver(std::uint16_t(58+i),payload[i]);}p.bus_request(0);s.status=saved;s.enabled=255;}
struct SoundCommandGate{std::uint16_t gate{},delay{};std::uint8_t alternate{};};
inline void consume_sound_command(SoundInterfaceState&s,SoundCommandGate&g,std::span<const std::uint8_t>rom,SoundEffectPorts&p){if(!(g.gate&32768)){g.delay=10;return;}if(g.delay){--g.delay;return;}const auto command=s.queued_command;if(command&32768)return;s.queued_command=std::uint16_t(0xff00|(s.queued_command&255));if(command>=91)return;const unsigned table=0x78926+unsigned(command)*4;if(table+4>rom.size())throw std::out_of_range("Sound descriptor table");std::uint32_t source=0;for(unsigned i=0;i<4;++i)source=(source<<8)|rom[table+i];if(source+23>rom.size())throw std::out_of_range("Sound descriptor extent");const auto old=g.alternate&1;g.alternate^=1;submit_original_sound_effect(s,source,rom.subspan(source,23),old?6:7,p);}
}
