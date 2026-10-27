#pragma once
#include <span>
#include <cstdint>
#include <stdexcept>
namespace rolo {
struct TextStripState{std::uint32_t cursor{},source{};std::uint16_t glyph_offset{};};
struct TextStripServices{virtual ~TextStripServices()=default;virtual void glyph(std::uint8_t)=0;virtual void scroll()=0;virtual void control_word(std::uint16_t)=0;virtual void control_long(std::uint32_t)=0;virtual void data_long(std::uint32_t)=0;virtual void data_word(std::uint16_t)=0;};
inline void center_text_strip(TextStripState&s,std::span<const std::uint8_t>b){
 unsigned n=0;for(;n<65536;++n){if(n>=b.size())throw std::out_of_range("Text centering source");if(b[n]==1)break;}
 const auto count=std::uint16_t(n==65536?0:n);const auto delta=std::uint16_t(20-count);
 const auto signed_delta=delta<32768?int(delta):int(delta)-65536;
 const auto half=signed_delta>=0?signed_delta/2:-((-signed_delta+1)/2);
 s.glyph_offset=std::uint16_t(half*4+((count&1)?2:0));
}
inline void clear_text_strip(TextStripState&s,TextStripServices&v){s.glyph_offset=0;for(unsigned i=0;i<20;++i){v.glyph(0);s.glyph_offset=std::uint16_t(s.glyph_offset+4);}}
inline void write_text_strip(TextStripState&s,std::span<const std::uint8_t>b,TextStripServices&v){
 std::size_t i=0;for(;;){if(i>=b.size())throw std::out_of_range("Text strip terminator");const auto raw=b[i++];const auto glyph=std::uint8_t(raw-32);
 if(glyph<128){v.glyph(glyph);s.glyph_offset=std::uint16_t(s.glyph_offset+4);continue;}
 s.source=raw==0?0:raw==2?0xffffffffu:s.source+std::uint32_t(i);return;}
}
inline void publish_text_strip(TextStripState&s,TextStripServices&v){
 v.control_word(0x8f02);v.control_long(0x70000003);v.data_long(0);v.control_long(0x40000010);
 s.cursor+=0x2000;const auto low=std::uint16_t(s.cursor)&0x7ff;s.cursor=(s.cursor&0xffff0000u)|low;v.data_word(low);
}
inline void update_text_strip(TextStripState&s,std::span<const std::uint8_t>b,TextStripServices&v){
 if(!(s.cursor&0xfffff)){clear_text_strip(s,v);if(s.source&0x80000000u)return;if(s.source){center_text_strip(s,b);write_text_strip(s,b,v);}}
 v.scroll();publish_text_strip(s,v);
}
// Shared storage is intentional: each byte is read after the previous write.
inline void copy_text_terminated(std::span<std::uint8_t>b,std::size_t&source,std::size_t&dest){
 for(;;){if(source>=b.size()||dest>=b.size())throw std::out_of_range("Text copy extent");const auto v=b[source++];b[dest++]=v;if(!v){--dest;return;}}
}
inline void copy_text_digits(std::span<std::uint8_t>b,std::size_t&source,std::size_t&dest,std::uint16_t&count){
 const unsigned n=unsigned(count)+1;for(unsigned i=0;i<n;++i){if(source>=b.size()||dest>=b.size())throw std::out_of_range("Digit copy extent");const auto v=b[source++];b[dest++]=std::uint8_t(v+48);}count=65535;
}
}
