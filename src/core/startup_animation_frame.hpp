#pragma once
#include "core/text_tile_publication.hpp"
namespace rolo {
// Partial $3FC translation: the phase drawing service is still pending.
struct StartupAnimationFrame{std::uint16_t scroll{},divider{},phase{},loop{};std::uint8_t done{};};
struct StartupAnimationServices:TextTilePorts{virtual void upload_logo_plane()=0;virtual void draw_phase(StartupAnimationFrame&,std::uint16_t)=0;};
inline int startup_animation_signed(std::uint16_t v){return v<32768?int(v):int(v)-65536;}
inline void update_startup_animation_frame(StartupAnimationFrame&s,StartupAnimationServices&p){
 if(startup_animation_signed(s.scroll)>=0){const auto old=s.scroll;--s.scroll;p.control_long(0x60000000);for(unsigned i=0;i<112;++i){p.data_word(static_cast<std::uint16_t>(0u-old));p.data_word(320);p.data_word(old);p.data_word(320);}}
 --s.divider;if(startup_animation_signed(s.divider)>=0){p.control_word(0x8f02);return;}
 s.divider=2;
 if(!s.phase&&startup_animation_signed(s.scroll)<0){s.done=255;return;}
 ++s.phase;const auto phase=s.phase;p.upload_logo_plane();
 if(startup_animation_signed(phase)>24){s.phase=0;++s.loop;if(startup_animation_signed(s.loop)>2){s.loop=0;s.divider=180;}}
 else p.draw_phase(s,phase);
 p.control_word(0x8f02);
}
}
