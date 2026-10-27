#pragma once
#include <array>
#include <cstdint>
namespace rolo {
// These are typed native services, not ROM instructions or callable addresses.
enum class LevelFrameService {Replay,PublishTransfers,DrainTransfers,PrepareActors,ForegroundScroll,BackgroundScroll,
 PlayerInput,ScanTriggers,BuildActive,ActorCallbacks,AdvanceHistory,TransferRiders,ReadDirection,MovePlayer,PlayerPresentation,
 PlayerEnvironment,Camera,CollectContacts,ActorAnimation,VisualEffects,AdvanceLevel,UpdateHud,RenderActors,PublishGraphics,
 ForegroundTerrain,BackgroundTerrain,DelayedMusic,ResolveContact};
enum class LevelRestartService {FadeBlack,ResetWordQueue,ResetByteQueue,ResetLevel,InitializePlanes,PrepareTerrain,ClearLookup,
 ResetPools,InitializeDefinitions,LoadPlanes,CreatePlayer,ScanMap,PreparePlayer,InitialCamera,ClearForegroundScroll,
 ClearBackgroundScroll,ForegroundTerrain,BackgroundTerrain,ForegroundScroll,BackgroundScroll,CopyParents,BuildActive,
 ActorAnimation,InitializeHud,UpdateHud,FadeIn};
struct LevelFrameControl {std::uint32_t frame_marker{};std::uint16_t display_control{};};
template<class Services>void run_original_level_frame(LevelFrameControl& state,Services& s){
 state.frame_marker=0x1c6c;
 constexpr std::array order{LevelFrameService::Replay,LevelFrameService::PublishTransfers,LevelFrameService::DrainTransfers,
 LevelFrameService::PrepareActors,LevelFrameService::ForegroundScroll,LevelFrameService::BackgroundScroll,LevelFrameService::PlayerInput,
 LevelFrameService::ScanTriggers,LevelFrameService::BuildActive,LevelFrameService::ActorCallbacks,LevelFrameService::AdvanceHistory,
 LevelFrameService::TransferRiders,LevelFrameService::ReadDirection,LevelFrameService::MovePlayer,LevelFrameService::PlayerPresentation,
 LevelFrameService::PlayerEnvironment,LevelFrameService::Camera,LevelFrameService::CollectContacts,LevelFrameService::ActorAnimation,
 LevelFrameService::VisualEffects,LevelFrameService::AdvanceLevel,LevelFrameService::UpdateHud,LevelFrameService::RenderActors,
 LevelFrameService::PublishGraphics,LevelFrameService::ForegroundTerrain,LevelFrameService::BackgroundTerrain,
 LevelFrameService::DelayedMusic,LevelFrameService::ResolveContact};
 for(const auto service:order)s.frame_service(service);
}
template<class Services>void run_original_level_restart(LevelFrameControl& state,Services& s){
 s.restart_service(LevelRestartService::FadeBlack);
 state.display_control&=0xffbf;s.publish_display_control(state.display_control);
 constexpr std::array order{LevelRestartService::ResetWordQueue,LevelRestartService::ResetByteQueue,LevelRestartService::ResetLevel,
 LevelRestartService::InitializePlanes,LevelRestartService::PrepareTerrain,LevelRestartService::ClearLookup,LevelRestartService::ResetPools,
 LevelRestartService::InitializeDefinitions,LevelRestartService::LoadPlanes,LevelRestartService::CreatePlayer,LevelRestartService::ScanMap,
 LevelRestartService::PreparePlayer,LevelRestartService::InitialCamera,LevelRestartService::ClearForegroundScroll,
 LevelRestartService::ClearBackgroundScroll,LevelRestartService::ForegroundTerrain,LevelRestartService::BackgroundTerrain,
 LevelRestartService::ForegroundScroll,LevelRestartService::BackgroundScroll,LevelRestartService::CopyParents,LevelRestartService::BuildActive,
 LevelRestartService::ActorAnimation,LevelRestartService::InitializeHud,LevelRestartService::UpdateHud,LevelRestartService::FadeIn};
 for(const auto service:order)s.restart_service(service);
 state.display_control|=0x40;s.publish_display_control(state.display_control);
}
}
