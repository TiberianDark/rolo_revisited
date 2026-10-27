#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
inline void write_startup_pixel_range(std::span<std::uint8_t>bytes,std::uint32_t lower,std::uint32_t upper,std::uint32_t pattern){
 if(static_cast<std::int32_t>(upper)<static_cast<std::int32_t>(lower))return;
 const auto left=lower>>16,right=upper>>16;
 if(left>=8192||right>=8192)throw std::out_of_range("Startup pixel coordinate domain");
 const auto first=(left/8)*32,last=(right/8)*32;
 if(last+4>bytes.size())throw std::out_of_range("Startup pixel output extent");
 const auto leading=pattern>>((left&7)*4),trailing=pattern<<((7-(right&7))*4);
 auto store=[&](unsigned at,std::uint32_t value){for(unsigned n=0;n<4;++n)bytes[at+n]=std::uint8_t(value>>(24-n*8));};
 if(first==last){store(first,leading&trailing);return;}store(first,leading);for(auto at=first+32;at<last;at+=32)store(at,pattern);store(last,trailing);
}
}
