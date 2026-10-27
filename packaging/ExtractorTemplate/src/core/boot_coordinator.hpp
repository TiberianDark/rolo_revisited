#pragma once
#include <cstdint>
namespace rolo {
// Partial $200 caller layer. Hardware cold initialization remains a pending service.
struct BootState{std::uint32_t expansion_ports{};std::uint16_t third_port{},completion{};};
struct BootServices{virtual ~BootServices()=default;virtual void cold_hardware(BootState&)=0;virtual void boot_checksum(BootState&)=0;virtual void reset_startup(BootState&)=0;virtual void enable_startup_display()=0;virtual void wait_display_edge(BootState&)=0;virtual void animation(BootState&)=0;virtual void admit_main(BootState&)=0;};
inline void coordinate_native_boot(BootState&s,BootServices&v){
 if(!s.expansion_ports&&!s.third_port)v.cold_hardware(s);
 v.boot_checksum(s);
 if(!s.expansion_ports&&!s.third_port){v.reset_startup(s);v.enable_startup_display();s.completion=0;do{v.wait_display_edge(s);if(!s.completion)v.animation(s);}while(!(s.completion&0xff00));}
 s.completion=static_cast<std::uint16_t>(s.completion|0xff00);v.admit_main(s);
}
}
