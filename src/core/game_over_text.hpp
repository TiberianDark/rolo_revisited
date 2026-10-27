#pragma once
#include "core/text_numeric_sprites.hpp"
#include <span>
namespace rolo {
inline std::uint16_t completion_rom_word(std::span<const std::uint8_t>b,std::size_t at){if(at+2>b.size())throw std::out_of_range("Completion ROM word");return std::uint16_t((b[at]<<8)|b[at+1]);}
inline std::uint32_t completion_rom_long(std::span<const std::uint8_t>b,std::size_t at){return (std::uint32_t(completion_rom_word(b,at))<<16)|completion_rom_word(b,at+2);}
inline std::uint16_t count_campaign_completion(std::span<const std::uint8_t>rom,std::span<const std::uint8_t>flags){
 std::size_t at=0x4baaa;unsigned total=0,done=0;
 for(;;){auto source=completion_rom_long(rom,at);at+=4;if(!source)break;const auto width=completion_rom_word(rom,at);at+=4;if(!width)throw std::out_of_range("Unadmitted zero completion width");
  const auto count=std::uint16_t(width*4-1);for(unsigned i=0;i<=count;++i){if(source+i>=rom.size())throw std::out_of_range("Completion table extent");const auto id=rom[source+i];if(!id)continue;if(id>=flags.size())throw std::out_of_range("Completion flags extent");total=std::uint16_t(total+1);if(flags[id]&2)done=std::uint16_t(done+1);}
 }
 return total?std::uint16_t((done*100)/total):std::uint16_t(done);
}
struct GameOverTextState{std::uint32_t score{};std::uint16_t percent{};std::uint8_t show_complete{};std::array<std::uint8_t,8>digits{};};
inline void format_game_over_text(GameOverTextState&s,std::span<const std::uint8_t>rom,std::span<const std::uint8_t>flags,std::span<std::uint8_t>out){
 s.percent=count_campaign_completion(rom,flags);std::size_t destination=0;
 auto append=[&](std::size_t source){for(;;){if(source>=rom.size()||destination>=out.size())throw std::out_of_range("Gameover text extent");const auto v=rom[source++];out[destination++]=v;if(!v){--destination;return;}}};
 auto convert=[&](std::uint32_t value){unsigned i=0;for(std::uint32_t divisor=10000000;divisor;divisor/=10){s.digits[i++]=std::uint8_t(value/divisor);value%=divisor;}};
 auto digits=[&](unsigned start,unsigned count){for(unsigned i=0;i<count;++i){if(destination>=out.size())throw std::out_of_range("Gameover digits extent");out[destination++]=std::uint8_t(s.digits[start+i]+48);}};
 append(0x13c66);convert(s.score);digits(0,8);
 if(s.percent==100){if(s.show_complete){append(0x13c98);return;}--s.percent;}
 append(0x13c81);convert(s.percent);digits(6,2);append(0x13c85);
}
inline std::uint32_t publish_plain_text(TextLayoutState&s,std::span<const std::uint8_t>bytes,std::uint16_t attributes,TextTilePorts&p){
 initialize_text_layout(s);auto address=std::uint32_t(s.destination);std::size_t at=0;
 for(;;){if(at>=bytes.size())throw std::out_of_range("Plain text terminator");const auto c=bytes[at++];if(!c)return std::uint32_t(at);
  if(c==13){s.x=s.saved_x;s.y=std::uint16_t(s.y+1);address=(address&0xffff0000u)|std::uint16_t(((std::uint16_t(s.y<<7)+2*s.x)&0xffe)+s.base);continue;}
  if(c==8){s.x=std::uint16_t(s.x-1);if(s.x&32768){s.x=0;continue;}address=(address&0xffff0000u)|std::uint16_t(address-2);publish_text_character(address,32,attributes,p);continue;}
  publish_text_character(address,c,attributes,p);s.x=std::uint16_t(s.x+1);address=(address&0xffff0000u)|std::uint16_t(address+2);
  if(s.x<64)continue;s.x=0;s.y=std::uint16_t(s.y+1);if(s.y<32)continue;s.y=0;address=(address&0xffff0000u)|s.base;s.destination=s.base;
 }
}
}
