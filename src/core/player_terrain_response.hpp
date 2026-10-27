#pragma once
#include "core/actor_terrain.hpp"
#include "core/actor_contact.hpp"
namespace rolo {
inline std::array<std::uint8_t,4> player_terrain_bob{};
struct PlayerTerrainResponseState {
    std::uint32_t& drag;std::uint32_t& override_acceleration;std::uint16_t& previous_x_shift;
};
struct PlayerTerrainResponseServices {
    virtual ~PlayerTerrainResponseServices()=default;
    virtual void terrain_response_handler(unsigned slot,ActorState&,PlayerTerrainResponseState)=0;
};
struct BoundPlayerTerrainResponseServices final:PlayerTerrainResponseServices {
    const std::uint16_t& controlled_type;const std::uint16_t& frame_counter;
    const std::uint8_t& c5e8;std::uint8_t& c516;ContactGlobals& contact;
    BoundPlayerTerrainResponseServices(const std::uint16_t& type,const std::uint16_t& frame,
            const std::uint8_t& gate,std::uint8_t& effect,ContactGlobals& c)
        :controlled_type(type),frame_counter(frame),c5e8(gate),c516(effect),contact(c){}
    void terrain_response_handler(unsigned slot,ActorState& actor,PlayerTerrainResponseState state) override {
        const auto latch=[&]{if(!contact.override_c512)contact.action_latch_c517=255;};
        const auto effect=[&]{c516=255;actor.byte(125,static_cast<std::uint8_t>(actor.byte(125)|4));};
        switch(slot) {
        case 0:latch();return; //9476
        case 1: //9434, other controlled types share9420.
            if(controlled_type!=12){effect();return;}
            actor.byte(124,static_cast<std::uint8_t>((actor.byte(124)&~16u)|1));actor.longword(62,0);
            {
             auto y=static_cast<std::uint16_t>(actor.word(16)&0xfff0);
             const auto phase=static_cast<std::uint16_t>((frame_counter>>3)&3); //ASR.W low two bits match.
             y=static_cast<std::uint16_t>((y&0xff00)|static_cast<std::uint8_t>(y+player_terrain_bob[phase]));actor.word(16,y);}
            return;
        case 2:if(!c5e8)latch();return; //9250
        case 3:effect();return; //9420
        case 4: //920A; bounded original byte table924C={0,1,2,3}.
            state.drag=0x300;state.override_acceleration=0x800;
            {std::uint16_t index=0;
             if(!((actor.byte(121)^actor.byte(118))&8)) {
                 index=actor.word(58);if(signed_word(index)>3)index=3;
             }
             if(index>3)throw std::out_of_range("Unproved negative surface animation index");
             actor.byte(115,static_cast<std::uint8_t>(index));}
            return;
        case 6:case 7:return; // Both dispatch to literal RTS9488.
        default:throw std::out_of_range("Unbound native surface handler slot");
        }
    }
};
// $9196..$91D4 plus literal slot5 $91F4. All other handlers remain required.
inline void update_player_terrain_response(ActorState& controlled,const ActorTerrain& terrain,
        PlayerTerrainResponseState state,PlayerTerrainResponseServices& services) {
    state.drag=0x3000;state.override_acceleration=0;
    const auto value=static_cast<std::uint16_t>((actor_terrain_word(terrain,controlled.word(12),controlled.word(16))&0x2e00)-0x2000);
    if(signed_word(value)>=0) {
        const auto slot=static_cast<unsigned>(value>>9);
        if(slot==5){state.drag=0xf0000;state.override_acceleration=0x8000;}
        else services.terrain_response_handler(slot,controlled,state);
    }
    state.previous_x_shift=terrain.x_shift; // Read after the handler's possible mutation.
}
}
