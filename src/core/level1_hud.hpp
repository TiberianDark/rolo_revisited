#pragma once
#include "core/level1_hud_data.hpp"
namespace rolo {
struct Level1HudTransfer {std::uint32_t source{};std::uint16_t destination{},words{};};
struct Level1Hud {
    std::uint32_t actor{};
    std::array<std::uint8_t,448> pixels{};
    std::array<Level1HudTransfer,6> transfers{};
    std::uint32_t publications{};
};
// $5530..$567E: typed transfers replace six14-byte video queue packets.
inline void publish_level1_rescue_counter(Level1Hud& hud,std::uint16_t resource_pattern,std::uint16_t count){
    const auto tens=count/10,units=count%10;
    const auto tens_offset=static_cast<std::uint16_t>(tens<<6),units_offset=static_cast<std::uint16_t>(units<<6);
    if(tens_offset+64>level1_hud_data::digits.size())throw std::out_of_range("Unbound HUD digit read domain");
    const auto base=static_cast<std::uint16_t>(resource_pattern<<5);
    hud.transfers={{{0x322e0,base,64},{0x32360,static_cast<std::uint16_t>(base+128),32},
        {0x27bc0,static_cast<std::uint16_t>(base+192),32},{0x32360,static_cast<std::uint16_t>(base+256),32},
        {std::uint32_t(0x27940+tens_offset),static_cast<std::uint16_t>(base+320),32},
        {std::uint32_t(0x27940+units_offset),static_cast<std::uint16_t>(base+384),32}}};
    auto copy=[&](auto source,unsigned destination){std::copy(source.begin(),source.end(),hud.pixels.begin()+destination);};
    copy(level1_hud_data::label,0);copy(level1_hud_data::blank,128);copy(level1_hud_data::icon,192);
    copy(level1_hud_data::blank,256);
    copy(std::span<const std::uint8_t>(level1_hud_data::digits).subspan(tens_offset,64),320);
    copy(std::span<const std::uint8_t>(level1_hud_data::digits).subspan(units_offset,64),384);
    ++hud.publications;
}
// $D452..$D49E. Wave[-1] is the literal negative sentinel before D4A0.
inline void update_level1_rescue_counter(ActorState& a,Level1Hud& hud){
    const auto offset=signed_word(a.word(46));
    if(offset%2||offset<-2||offset>42)throw std::out_of_range("Unbound HUD wave offset");
    const auto wave=level1_hud_data::wave.at((offset+2)/2);
    if(wave>=0){
        a.word(46,static_cast<std::uint16_t>(a.word(46)+static_cast<std::int8_t>(a.byte(48))));
        a.word(16,static_cast<std::uint16_t>(a.word(16)+(a.byte(49)?-wave:wave)));return;
    }
    if(signed_word(static_cast<std::uint16_t>(a.word(46)+1))<0){a.byte(116,255);hud.actor=0;return;}
    a.byte(50,static_cast<std::uint8_t>(a.byte(50)-1));
    if(!a.byte(50)){a.word(46,static_cast<std::uint16_t>(a.word(46)-2));a.byte(48,254);a.byte(49,255);}
}
}
