#pragma once
#include "core/player_terrain_response.hpp"
#include "core/player_trigger_pool.hpp"
namespace rolo {
struct PlayerTriggerGlobals {
    const std::uint16_t& controlled_type;
    std::uint16_t& checkpoint_x;std::uint16_t& checkpoint_y; //C4FE/C500
    std::uint16_t& next_selector; //F2F6
    std::uint8_t& selector_flag;std::uint8_t& transition_latch;std::uint8_t& player_latch; //F26C/F26D/C522
};
enum class TriggerTransitionPhase {
    Reset63FA,History684E,History6864,Camera4CB8,Foreground7292,Background72A2,
    State6960,State6AA6,Graphics31D6,Display25A8,State66DE,RoloAC34
};
struct TriggerDestination {bool negative{};std::uint16_t x{},y{};};
struct PlayerTriggerDispatchServices {
    virtual ~PlayerTriggerDispatchServices()=default;
    virtual ActorState& controlled_actor()=0;
    virtual void sound_command(std::uint16_t command)=0;
    virtual TriggerDestination lookup_destination(std::uint8_t parameter)=0; //3EE4, D6/D7 plus N
    virtual void transition_phase(TriggerTransitionPhase phase)=0;
};
// $92F2 table and $933A/$937A/$93FE. Required transition phases are native services,
// not addresses executed by a CPU interpreter. Read live controlled actor after63FA.
inline void dispatch_player_trigger(unsigned slot,std::uint8_t parameter,PlayerTriggerGlobals globals,
        PlayerTerrainResponseState response_state,PlayerTerrainResponseServices& surfaces,
        PlayerTriggerDispatchServices& services){
    switch(slot){
    case 0:
        if(globals.controlled_type==4){auto& actor=services.controlled_actor();globals.checkpoint_x=actor.word(12);globals.checkpoint_y=actor.word(16);}return;
    case 1:surfaces.terrain_response_handler(3,services.controlled_actor(),response_state);return;
    case 2:surfaces.terrain_response_handler(1,services.controlled_actor(),response_state);return;
    case 3:surfaces.terrain_response_handler(0,services.controlled_actor(),response_state);return;
    case 4:case 5:case 6:case 7:case 8:case 9:case 10:case 11:case 12:case 13:case 14:case 15:return; //9486/9488 literalRTS
    case 16:
        if(globals.controlled_type!=4)return;
        globals.next_selector=parameter&127;globals.selector_flag=(parameter>>7)&1;
        globals.transition_latch=255;globals.player_latch=255;services.sound_command(0x1d);return;
    case 17:{
        const auto destination=services.lookup_destination(parameter);if(destination.negative)return;
        services.sound_command(0x1d);services.transition_phase(TriggerTransitionPhase::Reset63FA);
        auto& actor=services.controlled_actor();actor.word(12,destination.x);actor.word(14,0);
        actor.word(16,destination.y);actor.word(18,0);actor.byte(121,0);actor.longword(58,0);actor.byte(122,0);actor.longword(62,0);
        for(const auto phase:{TriggerTransitionPhase::History684E,TriggerTransitionPhase::History6864,
                TriggerTransitionPhase::Camera4CB8,TriggerTransitionPhase::Foreground7292,TriggerTransitionPhase::Background72A2,
                TriggerTransitionPhase::State6960,TriggerTransitionPhase::State6AA6,TriggerTransitionPhase::Graphics31D6,
                TriggerTransitionPhase::Display25A8,TriggerTransitionPhase::State66DE})services.transition_phase(phase);
        if(globals.controlled_type==4)services.transition_phase(TriggerTransitionPhase::RoloAC34);
        return;
    }
    default:throw std::out_of_range("Unproved trigger slot");
    }
}
struct BoundPooledPlayerTriggerServices final:PooledPlayerTriggerServices {
    PlayerTriggerGlobals globals;PlayerTerrainResponseState response_state;
    PlayerTerrainResponseServices& surfaces;PlayerTriggerDispatchServices& dispatch;
    BoundPooledPlayerTriggerServices(PlayerTriggerPool& pool,TriggerMarkerServices& markers,
            PlayerTriggerGlobals state,PlayerTerrainResponseState response,
            PlayerTerrainResponseServices& effects,PlayerTriggerDispatchServices& transitions)
        :PooledPlayerTriggerServices(pool,markers),globals(state),response_state(response),surfaces(effects),dispatch(transitions){}
    void dispatch_trigger(unsigned slot,std::uint16_t identity)override {
        dispatch_player_trigger(slot,pool.record(identity).byte(10),globals,response_state,surfaces,dispatch);
    }
};
}
