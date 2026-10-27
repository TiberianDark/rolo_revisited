#pragma once
#include "core/palette_effect.hpp"
namespace rolo {
struct MenuPaletteTransitionState{std::array<std::uint16_t,64>colours{};std::array<PaletteEffect,2>effects{};std::uint8_t inhibited=255,dirty{};};
enum class MenuPaletteService{Publish,Highlight,PrepareActors,RenderActors,PublishGraphics,RestorePalette};
struct MenuPaletteTransitionServices{virtual ~MenuPaletteTransitionServices()=default;virtual void service(MenuPaletteService)=0;virtual void palette_clock(MenuPaletteTransitionState&)=0;};
inline void await_menu_palette(MenuPaletteTransitionState&s,MenuPaletteTransitionServices&v){s.inhibited=0;while(s.effects[1].active)v.palette_clock(s);s.inhibited=255;}
// $2158: white only entries1..31, publish/highlight before sampling sources.
inline void enter_menu_palette(MenuPaletteTransitionState&s,std::span<const std::uint16_t>target,MenuPaletteTransitionServices&v){
 if(target.size()!=32)throw std::out_of_range("Menu palette target extent");
 for(unsigned n=1;n<32;++n)s.colours[n]=0xeee;s.dirty=255;v.service(MenuPaletteService::Publish);v.service(MenuPaletteService::Highlight);
 for(unsigned n=0;n<2;++n)initialize_palette_effect(s.effects[n],std::span<const std::uint16_t>(s.colours).subspan(n*16,16),target.subspan(n*16,16));await_menu_palette(s,v);
}
// $21C6: palette entry0 is deliberately excluded from the first15-colour job.
inline void leave_menu_palette(MenuPaletteTransitionState&s,std::span<const std::uint16_t>black,MenuPaletteTransitionServices&v){
 if(black.size()!=16)throw std::out_of_range("Menu black target extent");
 initialize_palette_effect(s.effects[0],std::span<const std::uint16_t>(s.colours).subspan(1,15),black.first(15));
 initialize_palette_effect(s.effects[1],std::span<const std::uint16_t>(s.colours).subspan(16,16),black);
 await_menu_palette(s,v);for(auto op:{MenuPaletteService::PrepareActors,MenuPaletteService::RenderActors,MenuPaletteService::PublishGraphics,MenuPaletteService::RestorePalette})v.service(op);
}
struct MenuBeginState{std::uint32_t frame_hook{},controlled{};std::uint8_t ready{},closing{},edge{};std::uint16_t window{};};
enum class MenuBeginService{ClearWindow,DrawMenu,ClearBlink,PrepareActorGraphics,PublishGraphics};
struct MenuBeginServices{virtual ~MenuBeginServices()=default;virtual void service(MenuBeginService,std::uint32_t=0)=0;};
inline void initialize_menu_begin(MenuBeginState&s,MenuBeginServices&v){s.frame_hook=0x1e20;s.ready=s.closing=0;s.window=0x9200;v.service(MenuBeginService::ClearWindow);v.service(MenuBeginService::DrawMenu);s.edge=0;v.service(MenuBeginService::ClearBlink,s.controlled);v.service(MenuBeginService::PrepareActorGraphics);v.service(MenuBeginService::PublishGraphics);}
}
