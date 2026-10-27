#pragma once
#include "core/boot_coordinator.hpp"
#include <algorithm>
#include <array>
#include <span>
#include <stdexcept>
namespace rolo {
// Logical initialization requests only. No MMIO, CPU or sound-driver execution.
struct ColdBootPorts{
 virtual ~ColdBootPorts()=default;
 virtual void write_byte(std::uint32_t,std::uint8_t)=0;
 virtual void write_word(std::uint32_t,std::uint16_t)=0;
 virtual void write_long(std::uint32_t,std::uint32_t)=0;
 virtual void read_display_status()=0;
 virtual void acquire_sound_staging()=0;
};
inline void initialize_native_cold_boot(std::span<const std::uint8_t>rom,std::uint8_t hardware_version,std::array<std::uint8_t,65536>&ram,std::array<std::uint8_t,8192>&sound_staging,ColdBootPorts&p){
 if(rom.size()<0x2fa)throw std::out_of_range("Cold boot data table");
 if(hardware_version&15)p.write_long(0xa14000,0x53454741);
 p.read_display_status();
 std::uint16_t reg=0x8000;for(unsigned n=0;n<24;++n){reg=std::uint16_t((reg&0xff00)|rom[0x2a8+n]);p.write_word(0xc00004,reg);reg=std::uint16_t(reg+256);}
 auto table_long=[&](unsigned a){std::uint32_t v=0;for(unsigned i=0;i<4;++i)v=(v<<8)|rom[a+i];return v;};
 p.write_long(0xc00004,table_long(0x2c0));p.write_word(0xc00000,0);
 p.write_word(0xa11100,0x100);p.write_word(0xa11200,0x100);p.acquire_sound_staging();
 for(unsigned n=0;n<38;++n){sound_staging[n]=rom[0x2c4+n];p.write_byte(0xa00000+n,sound_staging[n]);}
 p.write_word(0xa11200,0);p.write_word(0xa11100,0);p.write_word(0xa11200,0x100);
 ram.fill(0);
 p.write_long(0xc00004,table_long(0x2ea));p.write_long(0xc00004,table_long(0x2ee));
 for(unsigned n=0;n<32;++n)p.write_long(0xc00000,0);
 p.write_long(0xc00004,table_long(0x2f2));for(unsigned n=0;n<20;++n)p.write_long(0xc00000,0);
 for(unsigned n=0;n<4;++n)p.write_byte(0xc00011,rom[0x2f6+n]);p.write_word(0xa11200,0);
}
}
