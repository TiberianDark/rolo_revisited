#pragma once
#include "core/startup_pixel_range.hpp"
#include <array>
namespace rolo {
namespace startup_logo_raster_data {
inline std::array<std::uint8_t,9> heights{};
inline std::array<std::uint8_t,27> slopes{};
inline std::array<std::uint8_t,9> caps{};
}
struct StartupLogoEdges{std::uint32_t left{},right{},pattern{};std::uint16_t step{};};
inline void raster_startup_logo_edges(std::span<std::uint8_t>out,StartupLogoEdges&s){



 auto swap=[](std::uint32_t v){return (v<<16)|(v>>16);};unsigned counter=0,source=0,cap=0;std::uint32_t scratch_upper=0;
 for(unsigned row=0;row<9;++row){int height=startup_logo_raster_data::heights[row];for(unsigned slot=0;slot<6;++slot){s.pattern=0xaaaaaaaa;
  if(counter<27)s.step=startup_logo_raster_data::slopes[source++];else if(counter>27)s.step=static_cast<std::uint16_t>(0u-startup_logo_raster_data::slopes[--source]);
  const int delta=s.step<32768?s.step:int(s.step)-65536;
  s.left=(s.left&0xffff0000u)|static_cast<std::uint16_t>(s.left-delta);s.right+=static_cast<std::uint32_t>(delta);++counter;
  if(height>0){if(height==1)s.pattern=0x33333333;auto lower=s.left;const auto upper=s.right;
   if(slot==0){s.pattern=0xdddddddd;const auto low=static_cast<std::uint16_t>(lower);if((low<32768?int(low):int(low)-65536)<8)lower=8;}
   scratch_upper=swap(upper);write_startup_pixel_range(out.subspan(row*256+slot*4),swap(lower),scratch_upper,s.pattern);
  }else if(height==0){s.pattern=0x33333333;const auto b=startup_logo_raster_data::caps[cap++];const int size=b<128?b:int(b)-256;const auto upper=(scratch_upper&0xffff0000u)|static_cast<std::uint16_t>(s.left+size);scratch_upper=swap(upper);write_startup_pixel_range(out.subspan(row*256+slot*4),swap(s.left),scratch_upper,s.pattern);}
  --height;
 }}
}
}

