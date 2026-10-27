#pragma once
#include "core/level1_enemy_slice.hpp"
#include "core/player_trigger_continuation.hpp"
#include "core/trigger_destination.hpp"
#include "core/transporter_continuation.hpp"
#include "core/transporter_companions.hpp"
#include "core/palette_effect.hpp"
#include "core/plane_scroll.hpp"
namespace rolo {
// Native Level1 binding. Device/queue completion timing and full SAT capacity
// remain fidelity gaps; no ROM instructions or device emulation are performed.
struct Level1TransportWorld final:Level1TransportHooks,TriggerMarkerServices,
        PlayerTriggerServices,TransportContinuationServices {
    Level1EnemySlice& world;PlayerTriggerPool triggers;
    PlayerTriggerContinuation scan;TransporterContinuation transport;
    NativePaletteEffects effects;
    std::vector<TriggerTransitionPhase> phases;
    std::vector<ActorSpriteView> prepared_sprites,published_sprites;
    std::array<std::uint16_t,512> horizontal{};std::array<std::uint16_t,2> vertical{};
    unsigned transports{},vblanks{};std::uint8_t scroll_mode{};
    explicit Level1TransportWorld(Level1EnemySlice& w):world(w){
        triggers.initialize();effects.colours=world.palette;effects.inhibited_c48d=0;
        world.transport_hooks=this;
        auto& pending=world.pending_markers;
        pending.erase(std::remove_if(pending.begin(),pending.end(),[&](const auto& record){return transport_marker(record);}),pending.end());
    }
    bool busy()const{return transport.waiting_black;}
    std::uint8_t marker_byte(std::uint32_t identity)override{
        if(identity<world.map_identity||identity-world.map_identity>=world.map_storage.size())throw std::out_of_range("Transport marker byte extent");
        return world.map_storage[identity-world.map_identity];
    }
    void marker_byte(std::uint32_t identity,std::uint8_t value)override{
        (void)marker_byte(identity);world.map_storage[identity-world.map_identity]=value;
    }
    bool transport_marker(const TerrainDescriptorRecord& record)override{
        const auto category=record.type>>8;if(category!=7&&category!=8&&category!=10)return false;
        const auto identity=world.map_identity+record.record_offset;
        if(marker_byte(identity)!=category)return true;
        const TerrainMapView map{world.map_storage};std::uint16_t row=0;
        for(;row<map.word(6)/8;row=static_cast<std::uint16_t>(row+2))
            if(record.record_offset>=map.word(8+row)&&record.record_offset<map.word(10+row))break;
        if(row>=map.word(6)/8)throw std::out_of_range("Transport row extent");
        if(category==10){
            // $483E: these exported Level markers use parameter4 -> literal RTS slot4.
            const auto parameter=record.type&255;if(parameter!=4)throw std::out_of_range("Unbound class10 parameter");
            (void)triggers.allocate(record.x,row,std::uint16_t(parameter*4),0,0,static_cast<std::uint16_t>(identity),*this);
        }else (void)triggers.allocate(record.x,row,category==7?64:68,static_cast<std::uint8_t>(record.type),0,static_cast<std::uint16_t>(identity),*this);
        return true; // Original empty-pool failure leaves marker unchanged.
    }
    std::uint16_t trigger_word(std::uint16_t identity,unsigned offset)override{return triggers.word(identity,offset);}
    std::uint8_t trigger_byte(std::uint16_t identity,unsigned offset)override{return triggers.record(identity).byte(offset);}
    void release_trigger_restore_marker(std::uint16_t identity)override{
        triggers.unlink(identity);auto& record=triggers.record(identity);
        marker_byte(0xffff0000u|record.word(12),record.byte(14));
    }
    std::uint16_t consume_trigger(std::uint16_t identity)override{return triggers.unlink(identity);}
    void dispatch_trigger(unsigned slot,std::uint16_t identity)override{
        if(slot==16){
            if(world.movement.controlled_type!=4)return;const auto parameter=triggers.record(identity).byte(10);
            world.next_level_selector=parameter&127;world.next_entry_selector=(parameter>>7)&1;
            world.level_transition_latch=world.transition=255;world.sound=0x1d;return;
        }
        if(slot>=4&&slot<=15)return; // Original $9486/$9488 RTS, retaining pooled marker lifecycle.
        if(slot!=17)throw std::out_of_range("Unbound Level1 trigger family");
        (void)transport.begin(triggers.record(identity).byte(10),*this);
    }
    TriggerDestination destination(std::uint8_t parameter)override{return find_trigger_destination({world.map_storage},parameter);}
    void transport_sound(std::uint16_t command)override{world.sound=command;}
    void begin_black_fade()override{phases.clear();effects.colours=world.palette;effects.begin_black();}
    bool black_fade_finished()override{return effects.complete_black();}
    ActorState& live_controlled_actor()override{return world.pool.resolve(world.movement.controlled);}
    std::uint16_t live_controlled_type()override{return world.movement.controlled_type;}
    void publish_palette(){effects.publish([&](auto words){std::copy(words.begin(),words.end(),world.palette.begin());});}
    bool resume_transport_frame(std::uint8_t pressed)override{
        ++vblanks;effects.interrupt_palette_step();publish_palette();
        if(!busy()){effects.inhibited_c48d=255;return false;}
        ++world.frame;map_player_input(world.buttons,pressed); // Interrupt input continues during63FAwait.
        if(transport.resume(*this)){
            ++transports;
            if(scan.advance(*this,[&]{return busy();}))world.finish_after_presentation();
        }
        return true; // Caller is suspended, or its saved frame just completed.
    }
    bool scan_transport_triggers()override{
        const auto& actor=live_controlled_actor();
        scan.begin(actor.word(12),actor.word(16),world.camera.x,world.camera.y,16);
        return !scan.advance(*this,[&]{return busy();});
    }
    void transport_frame_returned()override{effects.inhibited_c48d=0;}
    void rebuild_phase(TriggerTransitionPhase phase)override{
        phases.push_back(phase);
        switch(phase){
        case TriggerTransitionPhase::History684E:world.display.names.fill(0);break;
        case TriggerTransitionPhase::History6864:world.background_display.names.fill(0);break;
        case TriggerTransitionPhase::Camera4CB8:
            initialize_camera(world.camera,world.camera_input());world.plane.word(22,0xffff);world.background_plane.word(22,0xffff);break;
        case TriggerTransitionPhase::Foreground7292:
            world.plane.word(18,world.camera.foreground_x);world.plane.word(20,world.camera.foreground_y);
            update_foreground_terrain_camera(world.plane,world.terrain_globals,world.streaming);break;
        case TriggerTransitionPhase::Background72A2:
            world.background_plane.word(18,world.camera.background_x);world.background_plane.word(20,world.camera.background_y);
            update_background_terrain_camera(world.background_plane,255,world.terrain_globals,world.background_streaming);break;
        case TriggerTransitionPhase::State6960:{
            struct Scroll final:NativeScrollStorageServices {
                using NativeScrollStorageServices::NativeScrollStorageServices;
                void queue_line_scroll_512_words()override{throw std::logic_error("Line scroll mode outside Level1 transport");}
            } service(horizontal,vertical,world.camera.row_scroll,scroll_mode);
            const auto fx=static_cast<std::uint16_t>(0-world.camera.foreground_x),bx=static_cast<std::uint16_t>(0-world.camera.background_x);
            publish_horizontal_scroll(world.camera.scroll_mode,{fx,bx,world.camera.foreground_y,world.camera.background_y},service);break;
        }
        case TriggerTransitionPhase::State6AA6:
            vertical={static_cast<std::uint16_t>(0-world.camera.foreground_y),static_cast<std::uint16_t>(0-world.camera.background_y)};break;
        case TriggerTransitionPhase::Graphics31D6:
            prepared_sprites.clear();
            for(const auto& actor:world.pool.actors)if(signed_word(actor.word(0))>=0&&actor.longword(28)&&!(actor.byte(125)&2))
                prepared_sprites.push_back(actor_sprite_view(actor,world.camera.foreground_x,world.camera.foreground_y));break;
        case TriggerTransitionPhase::Display25A8:published_sprites=prepared_sprites;break;
        case TriggerTransitionPhase::State66DE:effects.begin_level_palette(world.level_assets.target_palette);break;
        case TriggerTransitionPhase::RoloAC34:
            reposition_transporter_companions(world.pool,world.companion_state.slots,live_controlled_actor(),world.history);break;
        default:throw std::logic_error("Unbound transport phase");
        }
    }
};
}
