#pragma once
#include <array>
#include <algorithm>
#include <cstdint>
namespace rolo {
struct StartupResetPorts {
 virtual ~StartupResetPorts()=default;
 virtual void control_word(std::uint16_t)=0;
 virtual void control_long(std::uint32_t)=0;
 virtual void data_long(std::uint32_t)=0;
 virtual void data_word(std::uint16_t)=0;
 virtual std::uint16_t generate_startup_patterns(std::uint16_t)=0;
 virtual void begin_display_reset()=0;
 virtual void end_display_reset()=0;
};
// $8E0: preserve the final 36 bytes of work RAM, as the original DBF does.
inline std::uint16_t reset_startup_display(std::array<std::uint8_t,65536>& ram,StartupResetPorts& ports) {
 std::fill_n(ram.begin(),65500,0);
 ports.begin_display_reset();
 constexpr std::array<std::uint16_t,15> registers{0x8004,0x8134,0x8228,0x8330,0x8405,0x856e,0x8700,0x8b03,0x9003,0x8c81,0x8d08,0x8f02,0x9100,0x9200,0x8a01};
 for(auto word:registers)ports.control_word(word);
 ports.control_long(0x40000000);
 for(unsigned i=0;i<16384;++i)ports.data_long(0);
 ports.control_long(0x40000010);
 const auto generated=ports.generate_startup_patterns(0);
 ports.control_long(0x60000000);
 const auto result=static_cast<std::uint16_t>(0u-generated);
 ports.end_display_reset();
 return result;
}
// $BB0: sequential writes go to the same auto-incrementing data port.
inline std::uint16_t publish_startup_tile_pair(std::uint16_t tile,StartupResetPorts& ports) {
 ports.data_word(tile);tile=static_cast<std::uint16_t>(tile+1);
 ports.data_word(tile);return static_cast<std::uint16_t>(tile+1);
}
}
