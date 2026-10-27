#pragma once
#include "core/level1_hud.hpp"
#include "core/actor_state.hpp"
#include "core/actor_allocation.hpp"
namespace rolo {
struct RescueHudState {std::uint8_t spawn_selector{},rescued{};std::uint16_t remaining{};};
struct RescueHudAllocation {std::uint32_t key{};ActorState* returned_a4{};};
struct RescueHudServices {virtual ~RescueHudServices()=default;virtual RescueHudAllocation allocate_rescue_hud(const ActorAllocationRequest&)=0;virtual ActorState& rescue_hud_actor(std::uint32_t)=0;virtual void append_rescue_transfers(std::span<const Level1HudTransfer>)=0;};
// 54A0 through567E: allocation/refresh then original six typed publications.
inline void request_rescue_hud(Level1Hud& hud,RescueHudState& state,RescueHudServices& services){
 if((state.spawn_selector>=128&&state.spawn_selector!=255)||state.rescued)return;
 ActorState* actor{};
 if(!hud.actor){
  const auto result=services.allocate_rescue_hud({0x1476e,0xa00000,0,0,0,0});if(!result.key)return;
  if(!result.returned_a4)throw std::logic_error("Unbound HUD allocator A4");hud.actor=result.key;actor=result.returned_a4;
  actor->byte(126,actor->byte(126)|16);actor->byte(48,2);actor->byte(50,50);actor->word(36,56);actor->word(38,16);
  actor->longword(28,0x5854524e);actor->longword(8,0x5854524e);actor->word(32,0);actor->word(34,0);
 }else{
  actor=&services.rescue_hud_actor(hud.actor);actor->byte(50,50);
  if(actor->byte(48)&128){actor->byte(48,static_cast<std::uint8_t>(0u-actor->byte(48)));actor->byte(49,0);actor->word(46,static_cast<std::uint16_t>(actor->word(46)+2));}
 }
 publish_level1_rescue_counter(hud,actor->word(2),state.remaining);services.append_rescue_transfers(hud.transfers);
}
}


