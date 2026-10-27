#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
struct TextTilePorts{virtual ~TextTilePorts()=default;virtual void control_word(std::uint16_t)=0;virtual void control_long(std::uint32_t)=0;virtual void data_word(std::uint16_t)=0;virtual void data_long(std::uint32_t)=0;};
inline std::uint32_t text_vram_command(std::uint16_t address){return 0x40000000u|(std::uint32_t(address&0x3fff)<<16)|(address>>14);}
inline int text_signed_word(std::uint16_t v){return v<32768?int(v):int(v)-65536;}
inline std::uint16_t text_scroll_row(std::uint32_t cursor){const auto v=text_signed_word(std::uint16_t(cursor));return std::uint16_t(v>=0?v/8:-((7-v)/8));}
struct TextTileState{std::uint32_t cursor{};std::uint16_t column{},row{},attributes{},base{},row_mask{},erase_row{};};
inline void erase_text_scroll_row(const TextTileState&s,TextTilePorts&p){
 if((s.cursor&0x7ffff)||!s.erase_row)return;
 auto row=std::uint16_t(text_scroll_row(s.cursor)+s.erase_row);row&=s.row_mask;
 const auto address=std::uint16_t((row<<7)+s.base);p.control_long(text_vram_command(address));
 for(unsigned i=0;i<32;++i)p.data_long(0);
}
inline void publish_text_glyph(std::uint16_t glyph,const TextTileState&s,TextTilePorts&p){
 p.control_word(0x8f02);auto tile=std::uint16_t(std::uint16_t(glyph*4)|s.attributes);
 for(unsigned r=0;r<2;++r){const auto row=std::uint16_t(text_scroll_row(s.cursor)+s.row+r)&s.row_mask;
  const auto address=std::uint16_t((row<<7)+s.column+s.base);p.control_long(text_vram_command(address));
  tile=std::uint16_t(tile+(r?1:2));p.data_word(tile);tile=std::uint16_t(tile+1);p.data_word(tile);
 }
}
inline void publish_text_character(std::uint32_t address,std::uint16_t character,std::uint16_t attributes,TextTilePorts&p){
 const auto tile=std::uint16_t(std::uint16_t(character-32+0x7b4)|attributes);
 p.control_long(text_vram_command(std::uint16_t(address)));p.data_word(tile);
}
struct TextLayoutState{std::uint16_t x{},y{},base{};std::uint32_t source{};std::uint16_t saved_x{},saved_y{},destination{};};
inline std::uint32_t initialize_text_layout(TextLayoutState&s){s.saved_x=s.x;s.saved_y=s.y;s.destination=std::uint16_t(s.base+2*s.x+std::uint16_t(s.y<<7));return s.source;}
struct TextRectangleResult{std::size_t source{};std::uint32_t destination{};std::uint16_t columns{},rows{};};
inline TextRectangleResult publish_text_rectangle(std::span<const std::uint16_t> source,std::uint32_t destination,
        std::uint16_t attributes,std::uint16_t columns,std::uint16_t rows,TextTilePorts&p){
 const auto width=unsigned(columns)+1,height=unsigned(rows)+1;
 if(std::uint64_t(width)*height>source.size())throw std::out_of_range("Text rectangle source extent");
 p.control_word(0x8f02);std::size_t at=0;
 for(unsigned y=0;y<height;++y){p.control_long(text_vram_command(std::uint16_t(destination)));
  for(unsigned x=0;x<width;++x)p.data_word(std::uint16_t((source[at++]&2047)+attributes));destination+=128;
 }
 return {at,destination,columns,65535};
}
}
