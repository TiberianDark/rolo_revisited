#pragma once
#include <array>
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
struct SoundInterfaceState{std::uint16_t status{},queued_command{},frame{},seed{};std::uint8_t enabled{},seed_gate{};std::array<std::uint32_t,2>pending{};};
struct SoundInterfacePorts{virtual ~SoundInterfacePorts()=default;virtual void bus_request(std::uint16_t)=0;virtual void reset_request(std::uint16_t)=0;virtual void write_driver(std::uint16_t,std::uint8_t)=0;virtual std::uint8_t read_driver(std::uint16_t)=0;virtual void delay_iterations(unsigned)=0;virtual void queued_job(unsigned,std::uint32_t)=0;virtual void refill()=0;};
inline void queue_sound_command(SoundInterfaceState&s,std::uint32_t command){s.queued_command=std::uint16_t(command);}
inline std::uint32_t publish_sound_address(std::uint32_t value,SoundInterfacePorts&p){p.write_driver(384,std::uint8_t(value));const auto rotate=(value>>8)|(value<<24);p.write_driver(383,std::uint8_t(rotate));const auto swapped=(rotate&0xffff0000u)|((rotate&255)<<8)|((rotate>>8)&255);p.write_driver(382,std::uint8_t(swapped));return swapped;}
inline void begin_sound_bus(SoundInterfaceState&s,SoundInterfacePorts&p){s.status=0x2700;p.bus_request(0x100);}
inline void prepare_sound_address(SoundInterfaceState&s,std::uint32_t address,SoundInterfacePorts&p){begin_sound_bus(s,p);(void)publish_sound_address(address,p);p.write_driver(396,0);}
inline void sound_address_request(SoundInterfaceState&s,std::uint32_t address,std::uint8_t argument,bool special,bool forced,SoundInterfacePorts&p){const auto saved=s.status;prepare_sound_address(s,address,p);if(special)p.write_driver(11,0x12);p.write_driver(10,forced?255:(argument?argument:1));p.bus_request(0);s.status=saved;}
inline void sound_parameter_request(SoundInterfaceState&s,unsigned offset,std::uint32_t value,SoundInterfacePorts&p){if(offset!=86&&offset!=87&&offset!=88)throw std::out_of_range("Sound parameter offset");const auto saved=s.status;begin_sound_bus(s,p);p.write_driver(std::uint16_t(offset),std::uint8_t(value));p.bus_request(0);s.status=saved;}
inline std::uint32_t sound_status_request(SoundInterfaceState&s,bool channel11,SoundInterfacePorts&p){if(channel11&&!s.enabled)return 0;const auto saved=s.status;begin_sound_bus(s,p);const auto value=p.read_driver(channel11?11:10);p.bus_request(0);s.status=saved;return value;}
inline void stop_sound_interface(SoundInterfaceState&s,SoundInterfacePorts&p){s.enabled=0;const auto saved=s.status;begin_sound_bus(s,p);p.write_driver(11,0);p.write_driver(10,0);p.reset_request(0);p.bus_request(0);p.delay_iterations(451);p.reset_request(0x100);s.status=saved;}
inline void service_pending_sound_jobs(SoundInterfaceState&s,SoundInterfacePorts&p){for(unsigned i=0;i<2;++i){const auto key=s.pending[i];if(key){s.pending[i]=0;p.queued_job(i,key);}}}
inline void update_sound_interface_frame(SoundInterfaceState&s,SoundInterfacePorts&p){if(s.seed_gate)s.seed=std::uint16_t(s.seed+0x33);p.bus_request(0x100);s.seed=std::uint16_t(s.seed+0x100);p.write_driver(230,std::uint8_t(s.seed>>8));p.bus_request(0);service_pending_sound_jobs(s,p);s.frame=std::uint16_t(s.frame+1);if(!(s.frame&15))p.refill();}
inline void copy_sound_bytes(std::span<std::uint8_t>bytes,std::size_t&source,std::size_t&destination,std::uint16_t&counter,bool predecrement){const auto count=unsigned(counter)+(predecrement?0:1);for(unsigned i=0;i<count;++i){if(source>=bytes.size()||destination>=bytes.size())throw std::out_of_range("Sound data copy extent");const auto value=bytes[source++];bytes[destination++]=value;}counter=65535;}
}
