#pragma once
#include "core/backward_asset_codec.hpp"
#include "core/display_setup.hpp"
#include <algorithm>
#include <vector>
namespace rolo {
inline std::uint16_t menu_word(std::span<const std::uint8_t>b,std::size_t at){if(at>b.size()||b.size()-at<2)throw std::out_of_range("Menu word extent");return std::uint16_t((b[at]<<8)|b[at+1]);}
inline std::uint32_t menu_long(std::span<const std::uint8_t>b,std::size_t at){return (std::uint32_t(menu_word(b,at))<<16)|menu_word(b,at+2);}
inline void menu_put_word(std::vector<std::uint8_t>&b,std::uint16_t value){b.push_back(value>>8);b.push_back(value);}
inline void menu_put_long(std::vector<std::uint8_t>&b,std::uint32_t value){menu_put_word(b,value>>16);menu_put_word(b,value);}
inline std::size_t menu_signed_address(std::size_t base,std::uint16_t displacement){const auto at=std::int64_t(base)+signed_word(displacement);if(at<0)throw std::out_of_range("Menu signed table address");return std::size_t(at);}
struct LevelBankPublicationState{std::uint8_t bank{};std::uint32_t quads{},macros{},metadata{};std::vector<std::uint8_t>graphics;std::vector<std::uint16_t>macro_sizes;};
inline void select_level_quad_bank(LevelBankPublicationState&g,std::span<const std::uint8_t>rom){g.quads=menu_long(rom,0x4af6e+g.bank*4);}
inline void select_level_macro_bank(LevelBankPublicationState&g,std::span<const std::uint8_t>rom){g.macros=menu_long(rom,0x4afb2+g.bank*4);}
inline void select_level_metadata_bank(LevelBankPublicationState&g,std::span<const std::uint8_t>rom){g.metadata=menu_long(rom,0x4aff6+g.bank*4);}
inline void decode_level_graphics_bank(LevelBankPublicationState&g,std::span<const std::uint8_t>rom){g.graphics=decode_backward_asset(rom,menu_long(rom,0x4af2a+g.bank*4),65536).bytes;}
inline void initialize_level_bank_publication(LevelBankPublicationState&g,std::span<const std::uint8_t>rom){
 select_level_quad_bank(g,rom);select_level_macro_bank(g,rom);select_level_metadata_bank(g,rom);decode_level_graphics_bank(g,rom);
 const auto count=menu_word(rom,std::size_t(g.macros)+4);const unsigned iterations=count?count:65536;g.macro_sizes.clear();g.macro_sizes.reserve(iterations);
 for(unsigned i=0;i<iterations;++i){const auto offset=menu_word(rom,std::size_t(g.macros)+6+i*2);const auto at=menu_signed_address(g.macros,offset);if(at>=rom.size()||rom.size()-at<2)throw std::out_of_range("Macro dimensions extent");g.macro_sizes.push_back(std::uint16_t(unsigned(rom[at])*2*rom[at+1]));}
}
// $66CC: eight LONG transfers, retaining sequential alias behaviour.
inline void copy_selected_palette_bank(std::span<const std::uint8_t>source,std::size_t&read,std::span<std::uint8_t>destination,std::size_t&write){
 for(unsigned i=0;i<8;++i){auto value=menu_long(source,read);read+=4;if(write>destination.size()||destination.size()-write<4)throw std::out_of_range("Palette destination extent");for(unsigned j=0;j<4;++j)destination[write+j]=std::uint8_t(value>>((3-j)*8));write+=4;}
}
struct LevelMenuPublicationServices{virtual ~LevelMenuPublicationServices()=default;virtual void menu_transfer(GraphicsTransferRequest)=0;virtual void menu_control_word(std::uint16_t)=0;virtual void menu_control_long(std::uint32_t)=0;virtual void menu_name_word(std::uint16_t)=0;virtual void palette_publish(std::span<const std::uint8_t>,std::uint8_t&)=0;};
inline void publish_selected_level_palettes(std::span<const std::uint8_t>rom,std::uint16_t selector,std::span<std::uint8_t>palette,std::uint8_t&pending,LevelMenuPublicationServices&s){
 const auto at=menu_signed_address(0x4b08a,std::uint16_t(selector<<4));std::size_t write=0;for(unsigned i=0;i<4;++i){std::size_t read=menu_long(rom,at+i*4);copy_selected_palette_bank(rom,read,palette,write);}pending=255;s.palette_publish(palette.first(128),pending);
}
inline void publish_menu_name_plane(std::span<const std::uint8_t>rom,std::uint16_t fill,LevelMenuPublicationServices&s){s.menu_control_word(0x8f02);s.menu_control_long(0x50000003);std::size_t at=0x54b22;for(unsigned row=0;row<28;++row){for(unsigned x=0;x<40;++x){s.menu_name_word(std::uint16_t(menu_word(rom,at)+0xe5dd));at+=2;}for(unsigned x=0;x<24;++x)s.menu_name_word(fill);}}
struct LevelMenuSatState{std::vector<std::uint8_t>bytes;std::uint8_t link=0,action=0,rescued=0;std::uint16_t remaining=0,choice=0;std::array<const ActorState*,3>companions{};};
inline void publish_menu_remaining_digits(const LevelMenuSatState&g,LevelMenuPublicationServices&s){const unsigned count=g.rescued?0:g.remaining;const auto tens=std::uint16_t((count/10)<<6),ones=std::uint16_t((count%10)<<6);s.menu_transfer({0x27940u+tens,0xb200,0x40000000,32});s.menu_transfer({0x27940u+ones,0xb240,0x40000000,32});}
inline void copy_menu_initial_sprites(LevelMenuSatState&g,std::span<const std::uint8_t>sat){if(sat.size()<40)throw std::out_of_range("Menu initial sprite extent");g.bytes.insert(g.bytes.end(),sat.begin(),sat.begin()+40);g.bytes[g.bytes.size()-5]=5;g.link=std::uint8_t(g.link+5);}
inline void append_menu_record(LevelMenuSatState&g,std::uint32_t first,std::uint32_t second){menu_put_long(g.bytes,(first&0xffffff00)|g.link);g.link=std::uint8_t(g.link+1);menu_put_long(g.bytes,second);}
inline void append_menu_static_sprites(LevelMenuSatState&g,std::span<const std::uint8_t>rom){std::size_t at=0x3aa4;for(;;){auto first=menu_long(rom,at);at+=4;if(first&0x80000000)return;append_menu_record(g,first,menu_long(rom,at));at+=4;}}
inline void append_menu_action_sprites(LevelMenuSatState&g,std::span<const std::uint8_t>rom){auto index=std::uint8_t(g.action-1);if(index&128)return;for(unsigned slot=0;slot<3;++slot)if(2-slot!=index)append_menu_record(g,menu_long(rom,0x3bde+slot*8),menu_long(rom,0x3be2+slot*8));}
inline void append_menu_choice_sprites(LevelMenuSatState&g,std::span<const std::uint8_t>rom){const auto at=menu_signed_address(0x3b06,std::uint16_t(g.choice<<5));for(unsigned i=0;i<4;++i)append_menu_record(g,menu_long(rom,at+i*8),menu_long(rom,at+i*8+4));}
inline void append_menu_companion_sprites(LevelMenuSatState&g,std::span<const std::uint8_t>rom){
 for(unsigned slot=0;slot<3;++slot){auto*actor=g.companions[slot];if(!actor)continue;const auto at=0x3bc6+slot*8;auto first=menu_long(rom,at);auto width=actor->word(36);if(std::bit_cast<std::int8_t>(std::uint8_t(width))>32)width=std::uint16_t((width&0xff00)|32);const auto center_y=std::uint16_t(std::uint8_t(32-width)>>1);auto packed=std::uint16_t(std::uint16_t(width-1)<<5);auto height=actor->byte(39);if(std::bit_cast<std::int8_t>(height)>32)height=32;const auto center_x=std::uint16_t(std::uint8_t(32-height)>>1);packed=std::uint16_t((packed&0xff00)|height);packed=std::uint16_t((packed&0xff00)|std::uint8_t(std::uint8_t(height-1)<<3));packed=std::uint16_t(packed*4);first=(first&0xffff0000)|packed;append_menu_record(g,first,(std::uint32_t(actor->word(2)|menu_word(rom,at+4))<<16)|menu_word(rom,at+6));const auto start=g.bytes.size()-8;auto y=std::uint16_t(menu_word(g.bytes,start)+center_y),x=std::uint16_t(menu_word(g.bytes,start+6)+center_x);g.bytes[start]=y>>8;g.bytes[start+1]=y;g.bytes[start+6]=x>>8;g.bytes[start+7]=x;
 }
}
inline void publish_menu_sprite_transfer(LevelMenuPublicationServices&s){s.menu_transfer({0xffff7188,0xf400,0x40000000,0x140});}
inline void publish_companion_menu_sprites(LevelMenuSatState&g,std::span<const std::uint8_t>initial,std::span<const std::uint8_t>rom,LevelMenuPublicationServices&s){publish_menu_remaining_digits(g,s);g.link=1;g.bytes.clear();copy_menu_initial_sprites(g,initial);append_menu_choice_sprites(g,rom);append_menu_static_sprites(g,rom);append_menu_action_sprites(g,rom);append_menu_companion_sprites(g,rom);g.bytes[g.bytes.size()-5]=0;publish_menu_sprite_transfer(s);}
}
