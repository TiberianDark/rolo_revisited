#pragma once
#include <array>
#include <span>
#include <vector>
#include <cstdint>
#include <stdexcept>
namespace rolo {
struct StartupImageResult {std::vector<std::uint8_t>bytes;std::array<std::uint8_t,4096>dictionary;std::size_t consumed{};std::uint16_t cursor{};};
// $BBA: forward LZSS image DATA only. Zero output length is outside original callers.
inline StartupImageResult decode_startup_image(std::span<const std::uint8_t>source,std::size_t length){
 if(!length)throw std::out_of_range("Startup image output length");
 StartupImageResult r;r.dictionary.fill(32);r.cursor=0xfee;r.bytes.reserve(length);
 std::uint8_t flags=0;unsigned remaining=0;
 auto next=[&](){if(r.consumed>=source.size())throw std::out_of_range("Startup image source extent");return source[r.consumed++];};
 auto emit=[&](std::uint8_t v){r.bytes.push_back(v);if(r.bytes.size()==length)return true;r.dictionary[r.cursor]=v;r.cursor=static_cast<std::uint16_t>((r.cursor+1)&4095);return false;};
 for(;;){
  if(!remaining){flags=next();remaining=8;}
  const bool literal=(flags&1)!=0;flags>>=1;--remaining;
  const auto first=next();
  if(literal){if(emit(first))return r;}
  else {const auto second=next();unsigned at=first|((unsigned(second)&240)<<4),count=(second&15)+3;for(unsigned n=0;n<count;++n){const auto value=r.dictionary[at];at=(at+1)&4095;if(emit(value))return r;}}
 }
}
}
