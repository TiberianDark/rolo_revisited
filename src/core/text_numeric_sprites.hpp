#pragma once
#include "core/text_tile_publication.hpp"
#include <array>
namespace rolo {
inline void initialize_actor_type_gates(std::span<std::uint8_t>bytes){if(bytes.size()<16)throw std::out_of_range("Actor type gates");for(unsigned i=0;i<16;++i)bytes[i]=0;for(unsigned i:{3u,4u,5u,2u})bytes[i]=255;}
inline std::array<std::uint8_t,10> decimal_text_number(std::uint32_t value){std::array<std::uint8_t,10>out{};unsigned at=0;for(std::uint32_t power=100000000;power;power/=10){out[at++]=std::uint8_t(48+value/power);value%=power;}for(unsigned i=0;i<8&&out[i]==48;++i)out[i]=32;return out;}
inline std::array<std::uint8_t,9> hexadecimal_text_number(std::uint32_t value){constexpr char digits[]="0123456789ABCDEF";std::array<std::uint8_t,9>out{};for(unsigned i=0;i<8;++i)out[i]=std::uint8_t(digits[(value>>((7-i)*4))&15]);return out;}
inline void publish_text_cell(TextLayoutState&s,std::uint8_t&mode,std::uint16_t attributes,TextTilePorts&p){
 const auto destination=std::uint16_t(s.base+2*s.x+std::uint16_t(s.y<<7));publish_text_character(destination,mode,attributes,p);mode=0;s.x=std::uint16_t(s.x+1);
}
inline void initialize_glyph_sprites(std::span<std::uint8_t>memory,std::uint16_t attributes){
 if(memory.size()<640)throw std::out_of_range("Glyph sprite table");std::size_t at=640;std::uint16_t tile=std::uint16_t((attributes|0x8000)+2),blank=std::uint16_t((attributes|0x8000)|1),link=80;
 auto word=[&](std::uint16_t v){at-=2;memory[at]=std::uint8_t(v>>8);memory[at+1]=std::uint8_t(v);};
 auto record=[&](std::uint16_t t){word(0);word(t);word(link);word(0);--link;};
 for(unsigned row=0;row<8;++row){for(unsigned col=0;col<8;++col)record(tile++);record(blank);}for(unsigned i=0;i<8;++i)record(blank);memory[635]=0;
}
}
