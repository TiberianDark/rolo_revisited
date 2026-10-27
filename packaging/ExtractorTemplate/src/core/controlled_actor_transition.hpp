#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct ControlledTransitionState{ActorState* controlled=nullptr;ActorState* live=nullptr;std::uint8_t selector=0,hit_gate=0;std::uint16_t effect=0;std::uint32_t main_state=0;};
enum class ControlledTransitionStep{FadeBlack,InitFirst,InitSecond,RetireOld,SetupForeground,SetupBackground,Camera,TerrainForeground,TerrainBackground,Scroll,FramePublication,SpritePublication,Transfer,FadeIn,PrepareForeground,PrepareBackground};
struct ControlledTransitionServices{virtual ~ControlledTransitionServices()=default;virtual void step(ControlledTransitionStep,ControlledTransitionState&)=0;virtual void transfer(ControlledTransitionState&,std::uint32_t,std::uint32_t,std::uint16_t,std::uint32_t)=0;};
// $9642/$966A: replacement initializer changes controlled identity; old A5 is restored.
inline void switch_controlled_actor(ControlledTransitionState&s,ControlledTransitionServices&services){
 services.step(ControlledTransitionStep::FadeBlack,s);auto*saved=s.controlled;
 if(s.selector>1)throw std::out_of_range("Controlled initializer selector");services.step(s.selector?ControlledTransitionStep::InitSecond:ControlledTransitionStep::InitFirst,s);
 s.live=saved;s.live->byte(116,255);s.live->byte(125,s.live->byte(125)|4);
 for(const auto step:{ControlledTransitionStep::RetireOld,ControlledTransitionStep::SetupForeground,ControlledTransitionStep::SetupBackground,ControlledTransitionStep::Camera,ControlledTransitionStep::TerrainForeground,ControlledTransitionStep::TerrainBackground,ControlledTransitionStep::Scroll,ControlledTransitionStep::FramePublication,ControlledTransitionStep::SpritePublication,ControlledTransitionStep::Transfer,ControlledTransitionStep::FadeIn}){if(step==ControlledTransitionStep::Transfer)services.transfer(s,0xffffc9bc,0xf400,0x140,0x40000000);else services.step(step,s);}
 s.hit_gate=0;s.effect=0;
}
inline void request_player_level_transition(std::uint32_t&main_state){main_state=0x1e20;}
inline void prepare_both_level_planes(ControlledTransitionState&s,ControlledTransitionServices&services){services.step(ControlledTransitionStep::PrepareForeground,s);services.step(ControlledTransitionStep::PrepareBackground,s);}
// Original transfer arguments for the Transfer service above: C9BC -> F400,
// 0140 WORDs, command40000000; hardware timing remains a device boundary.
}
