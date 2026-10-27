#pragma once
#include "core/level1_companion_selection.hpp"
#include "core/world_map_cursor.hpp"
#include "core/startup_display_contracts.hpp"
namespace rolo {
struct SceneCastState{std::uint16_t camera_x{},camera_y{};std::uint32_t rolo{},controlled{},base{},squirrel{},rabbit{},monkey{},beaver{},falling{};};
inline std::uint32_t allocate_cast_actor(ActorPool&p,ActorAllocationServices&s,std::uint32_t def,std::uint32_t x,std::uint32_t y,std::uint8_t facing){auto result=allocate_actor_chain(p,{def,x,y,0,0,facing},s);if(!result.success)throw std::out_of_range("Scene cast requires successful original allocation domain");return result.head;}
inline void spawn_entrance_cast(ActorPool&p,SceneCastState&g,ActorAllocationServices&s){g.camera_x=g.camera_y=100;g.rolo=g.controlled=g.base=allocate_cast_actor(p,s,0x13ecc,0x1de0000,0xf10000,255);p.resolve(g.rolo).byte(126,p.resolve(g.rolo).byte(126)|2);
 g.squirrel=allocate_cast_actor(p,s,0x13f76,0xef0000,0xa20000,0);p.resolve(g.squirrel).word(50,250);p.resolve(p.resolve(g.squirrel).longword(84)).byte(116,255);
 g.rabbit=allocate_cast_actor(p,s,0x13f54,0x2100000,0xef0000,255);p.resolve(g.rabbit).word(50,200);p.resolve(p.resolve(g.rabbit).longword(84)).byte(116,255);
 g.monkey=allocate_cast_actor(p,s,0x13f32,0x1690000,0xed0000,0);p.resolve(g.monkey).word(70,56);p.resolve(p.resolve(g.monkey).longword(84)).byte(116,255);
 g.beaver=allocate_cast_actor(p,s,0x13f10,0x4e0000,0xf90000,0);auto&a=p.resolve(g.beaver);a.word(70,52);a.word(50,1);a.longword(58,0x2000);a.longword(62,0x400);p.resolve(a.longword(84)).byte(116,255);
}
struct AttractCastServices:ActorAllocationServices{virtual std::uint32_t create_player()=0;};
inline void spawn_attract_cast(ActorPool&p,SceneCastState&g,std::uint32_t&camera_x,std::uint32_t&camera_y,AttractCastServices&s){camera_x=camera_y=0;const auto player=s.create_player();p.resolve(player).word(12,160);p.resolve(player).word(16,151);(void)allocate_cast_actor(p,s,0x14f00,0x400000,0x970000,0);(void)allocate_cast_actor(p,s,0x14f44,0x600000,0x970000,0);g.falling=allocate_cast_actor(p,s,0x14f66,0x600000,0x730000,0);(void)allocate_cast_actor(p,s,0x14f88,0xf00000,0x970000,0);}
inline std::uint32_t choose_companion_actor_entry(std::uint16_t choice,ActorPool&pool,Level1CompanionState&companions,Level1ProgressState&progress,CompanionControlState&control,CompanionControlServices&s){if(choice>2)throw std::out_of_range("Companion slot entry");return select_level1_companion_menu_choice(choice,pool,companions,progress,control,s)?0:0xffffffffu;}
enum class FreshLevelStep{FadeBlack,ResetWordQueue,ResetByteQueue,ResetLevel,ClearForeground,ClearBackground,MenuNames,LoadPlanes,ScanLookup,ClearScratch,ResetActors,ResetGraphics,CreatePlayer,ScanStart,EntryMarker,ForegroundTerrain,BackgroundTerrain,ForegroundScroll,BackgroundScroll,CopyParents,BuildActive,Animate,InitializeHud,UpdateHud,FadeIn,Music};
struct FreshLevelState{std::uint16_t display{},pattern_base{},selection{};std::uint32_t main_state{};};
struct FreshLevelServices:VideoSetupPorts{virtual void step(FreshLevelStep)=0;};
inline void initialize_fresh_level(FreshLevelState&g,FreshLevelServices&s){s.step(FreshLevelStep::FadeBlack);g.display&=0xffbf;s.control(g.display);for(auto op:{FreshLevelStep::ResetWordQueue,FreshLevelStep::ResetByteQueue,FreshLevelStep::ResetLevel,FreshLevelStep::ClearForeground,FreshLevelStep::ClearBackground})s.step(op);g.pattern_base=1;for(auto op:{FreshLevelStep::MenuNames,FreshLevelStep::LoadPlanes,FreshLevelStep::ScanLookup,FreshLevelStep::ClearScratch,FreshLevelStep::ResetActors,FreshLevelStep::ResetGraphics,FreshLevelStep::CreatePlayer,FreshLevelStep::ScanStart,FreshLevelStep::EntryMarker,FreshLevelStep::ForegroundTerrain,FreshLevelStep::BackgroundTerrain,FreshLevelStep::ForegroundScroll,FreshLevelStep::BackgroundScroll})s.step(op);g.main_state=0x1c6c;for(auto op:{FreshLevelStep::CopyParents,FreshLevelStep::BuildActive,FreshLevelStep::Animate})s.step(op);g.selection=3;for(auto op:{FreshLevelStep::InitializeHud,FreshLevelStep::UpdateHud,FreshLevelStep::FadeIn,FreshLevelStep::Music})s.step(op);g.display|=64;s.control(g.display);}
}
