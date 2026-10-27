#include "core/resource_bindings.hpp"
#include "core/ending_sequence.hpp"
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include "host_gamepad.hpp"
#include "host_music.hpp"
#include "host_presentation.hpp"
#include "host_resource_setup.hpp"
#include "host_widescreen.hpp"
#include "host_renderer.hpp"
#include "host_issue_capture.hpp"
#include "core/entrance.hpp"
#include "core/opening_sequence.hpp"
#include "core/preview_assets.hpp"
#include "core/player.hpp"
#include "core/camera.hpp"
#include "core/level1_enemy_slice.hpp"
#include "core/terrain_viewport.hpp"
#include "core/world_map_raster.hpp"
#include "core/world_map_cursor_world.hpp"
#include "core/world_route_map.hpp"
#include "core/world_camera.hpp"
#include "core/world_palette.hpp"
#include "core/world_level_admission.hpp"
#include "core/actor_palette_raster.hpp"
#include "core/actor_paint_order.hpp"
#include "core/forest_log_raster.hpp"
#include "core/level1_background_palette.hpp"
#include "core/palette_effect.hpp"
#include "core/level1_transport_world.hpp"
#include "core/level1_menu_world.hpp"
#include "core/demo_progress_save.hpp"
#include "core/demo_life_cycle.hpp"
#include "core/frame_timing_log.hpp"
#include "core/scene_control_entries.hpp"
#include <fstream>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <memory>
#include <string>
#include <vector>

static bool host_fullscreen=false,host_widescreen=true,host_debug_flight=false;
static std::string host_renderer;
static std::filesystem::path host_data_root;
// Own the display across scene hosts. Destroy scene textures before the renderer,
// and destroy the renderer/window before shutting SDL down.
struct HostDisplay {
    std::unique_ptr<SDL_Window,decltype(&SDL_DestroyWindow)> window{nullptr,SDL_DestroyWindow};
    std::unique_ptr<SDL_Renderer,decltype(&SDL_DestroyRenderer)> renderer{nullptr,SDL_DestroyRenderer};
    bool vsync_requested=true;
    ~HostDisplay(){renderer.reset();window.reset();SDL_Quit();}
};
struct PreviewTexture {
    std::uint32_t kind,source,palette,width,height;
    std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> texture;
    std::array<std::uint16_t,64> cached_colours{};
    std::uint64_t cached_macro{};bool pixels_current{};
};
int run_preview(int argc,char** argv,std::string& start_map,HostDisplay& display) {
    bool handoff_test=false;
    std::string asset_path,smoke_path;int fps=60,browse_level=-1;std::uint16_t start_level=0;bool four_k=false;bool& widescreen=host_widescreen;bool static_preview=false,map_preview=false,player_preview=false,enemy_preview=false,native_campaign=false;
    for (int i=1;i<argc;++i) {
        const std::string option=argv[i];
        if(option=="--handoff-test"){handoff_test=true;continue;}
        if(option=="--campaign"){native_campaign=true;static_preview=map_preview=player_preview=enemy_preview=true;continue;}
        if(option=="--resources-ready")continue;
        if(option=="--resource-root"&&i+1<argc){++i;continue;}
        if(option=="--debug-flight"){host_debug_flight=true;continue;}
        if(option=="--4k"){four_k=true;continue;}
        if(option=="--widescreen"){widescreen=true;continue;}
        if ((option=="--entrance-preview" || option=="--asset-preview" || option=="--map-preview" || option=="--player-preview" || option=="--enemy-preview" || option=="--fps" || option=="--smoke-test" || option=="--start-level" || option=="--browse-level" || option=="--renderer") && i+1<argc) {
            const std::string value=argv[++i];
            if(option=="--renderer"){if(!rolo::valid_renderer(value))return 2;host_renderer=value;}
            else if (option=="--entrance-preview") asset_path=value;
            else if (option=="--asset-preview") {asset_path=value;static_preview=true;}
            else if (option=="--map-preview") {asset_path=value;static_preview=true;map_preview=true;}
            else if (option=="--player-preview") {asset_path=value;static_preview=true;map_preview=true;player_preview=true;}
            else if (option=="--enemy-preview") {asset_path=value;static_preview=true;map_preview=true;player_preview=true;enemy_preview=true;}
            else if (option=="--fps") {if(value!="50" && value!="60") {std::fprintf(stderr,"Preview cadence must be 50 or 60.\n");return 2;}fps=std::atoi(value.c_str());}
            else if(option=="--start-level"){if(value.empty()||value.find_first_not_of("0123456789")!=std::string::npos||std::atoi(value.c_str())<1||std::atoi(value.c_str())>79)return 2;start_level=static_cast<std::uint16_t>(std::atoi(value.c_str()));}
            else if(option=="--browse-level"){if(value.empty()||value.find_first_not_of("0123456789")!=std::string::npos)return 2;browse_level=std::atoi(value.c_str());if(browse_level<0||browse_level>=80)return 2;}
            else smoke_path=value;
        } else {std::fprintf(stderr,"Usage: rolo_native [--entrance-preview pack.rla] [--fps 50|60] [--smoke-test directory]\n       rolo_native --asset-preview title.bmp\n");return 2;}
    }
    if(start_level&&!rolo::native_level_connected(start_level)){std::fprintf(stderr,"Selector is not a world-linked native level.\n");return 2;}
    if (!SDL_WasInit(SDL_INIT_VIDEO)&&!SDL_Init(SDL_INIT_VIDEO|SDL_INIT_EVENTS|SDL_INIT_GAMEPAD)) {std::fprintf(stderr,"SDL: %s\n",SDL_GetError());return 1;}
    int result=0;
    {
        rolo::HostGamepad gamepad;
        rolo::HostMusic music(fps,smoke_path.empty());
        rolo::LevelMusicAssignment level_music;
        if(asset_path.empty()) asset_path=(host_data_root/"entrance-assets.rla").string();
        const auto flags=static_cast<SDL_WindowFlags>(SDL_WINDOW_RESIZABLE|(host_fullscreen?SDL_WINDOW_FULLSCREEN:0)|(smoke_path.empty()?0:SDL_WINDOW_HIDDEN));
        const int artwork_height=player_preview?224:160;
        const int logical_height=player_preview&&!enemy_preview?288:224;
        auto& window=display.window;auto& renderer=display.renderer;
        const bool reused_window=bool(window);
        if(!window)window.reset(SDL_CreateWindow("Rolo to the Rescue",four_k?3840:1280,four_k?2160:900,flags));
        if(window&&!renderer)renderer.reset(SDL_CreateRenderer(window.get(),host_renderer=="auto"?nullptr:host_renderer.c_str()));
        bool renderer_fallback=false;
        if(window&&!renderer&&host_renderer!="auto"){
            renderer.reset(SDL_CreateRenderer(window.get(),"direct3d11"));renderer_fallback=bool(renderer);
            if(renderer_fallback&&smoke_path.empty())SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_WARNING,"Graphics renderer","The selected renderer is unavailable. Rolo is using Direct3D 11. Press F8 to choose another renderer.",window.get());
        }
        rolo::FrameTimingLog timing(host_data_root/"debug-logs");
        if(reused_window)timing.event("SCENE_HANDOFF_DISPLAY_REUSED");
        if(renderer)timing.event((std::string("RENDERER_")+SDL_GetRendererName(renderer.get())).c_str());
        if(renderer_fallback)timing.event("RENDERER_FALLBACK_DIRECT3D11");
        bool vsync_enabled=false;bool& vsync_requested=display.vsync_requested;
        const auto configure_vsync=[&]{
            const int desired=vsync_requested?1:0;int actual=0;
            const bool applied=renderer&&SDL_SetRenderVSync(renderer.get(),desired);
            vsync_enabled=vsync_requested&&applied&&SDL_GetRenderVSync(renderer.get(),&actual)&&actual==1;
            timing.event(vsync_enabled?"VSYNC_ENABLED":"VSYNC_UNAVAILABLE_FRAME_LIMIT_FALLBACK");
            if(vsync_enabled)timing.event("PRESENTATION_FOLLOWS_DISPLAY_REFRESH");
        };
        configure_vsync();
        timing.event(fps==60?"FRAME_LIMIT_60_FPS":"FRAME_LIMIT_50_FPS");
        std::uint64_t next_present=SDL_GetTicksNS();
        if(!window||!renderer) {std::fprintf(stderr,"Window: %s\n",SDL_GetError());result=1;}
        else if(!SDL_SetRenderLogicalPresentation(renderer.get(),320,logical_height,SDL_LOGICAL_PRESENTATION_LETTERBOX)) result=1;
        else {
            rolo::HostPresentation presentation(renderer.get(),logical_height);
            rolo::LocalAchievements achievements;
            const auto achievement_file=host_data_root/"rolo-achievements.sav";
            if(smoke_path.empty())achievements.load(achievement_file);
            if(!presentation.valid()){std::fprintf(stderr,"Presentation: %s\n",SDL_GetError());return 1;}
            std::vector<PreviewTexture> textures;
            std::vector<PreviewTexture> player_textures;
            const auto background_path=std::filesystem::path(asset_path).parent_path()/"background.bmp";
            const bool map_background=native_campaign || (map_preview && std::filesystem::exists(background_path));
            if(native_campaign) {
                // Native terrain comes from the external pack, without preview BMP files.
                // Retain map dimensions for the existing pan/reset controls.
                const auto level=rolo::all_native_level_data::level(1);
                textures.push_back({4,0,0,level.width,level.height,{SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,1,1),SDL_DestroyTexture}});
                textures.push_back({5,0,0,512,272,{nullptr,SDL_DestroyTexture}});
            } else if(static_preview) {
                const auto foreground_path=map_background?(std::filesystem::path(asset_path).parent_path()/"foreground-alpha.bmp").string():asset_path;
                std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> surface(SDL_LoadBMP(foreground_path.c_str()),SDL_DestroySurface);
                if(!surface || (map_preview?(surface->w<320||surface->h<160||surface->w>8192||surface->h>8192):(surface->w!=320||surface->h!=160))) result=1;
                else textures.push_back({4,0,0,static_cast<std::uint32_t>(surface->w),static_cast<std::uint32_t>(surface->h),{SDL_CreateTextureFromSurface(renderer.get(),surface.get()),SDL_DestroyTexture}});
                if(map_background && result==0) {
                    std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> background(SDL_LoadBMP(background_path.string().c_str()),SDL_DestroySurface);
                    if(!background||background->w!=512||background->h!=272) result=1;
                    else textures.push_back({5,0,0,512,272,{SDL_CreateTextureFromSurface(renderer.get(),background.get()),SDL_DestroyTexture}});
                }
            } else {
                auto records=rolo::load_preview_assets(asset_path);
                if(!records) {std::fprintf(stderr,"Missing or invalid preview asset pack: %s\n",asset_path.c_str());result=1;}
                else for (auto& record:*records) {
                    std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> surface(SDL_CreateSurfaceFrom(static_cast<int>(record.width),static_cast<int>(record.height),SDL_PIXELFORMAT_RGBA32,record.rgba.data(),static_cast<int>(record.width*4)),SDL_DestroySurface);
                    auto* texture=surface?SDL_CreateTextureFromSurface(renderer.get(),surface.get()):nullptr;
                    textures.push_back({record.kind,record.source,record.palette,record.width,record.height,{texture,SDL_DestroyTexture}});
                }
            }
            if(enemy_preview&&map_background&&textures.size()==2)
                textures[1].texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,512,272));
            for(auto& texture:textures) if(!texture.texture || !SDL_SetTextureScaleMode(texture.texture.get(),SDL_SCALEMODE_NEAREST) ||
                !SDL_SetTextureBlendMode(texture.texture.get(),SDL_BLENDMODE_BLEND)) result=1;
            if(player_preview) {
              for(const auto* filename:{enemy_preview?"level1-player-assets.rla":"player-assets.rla","first-enemy-assets.rla","level1-object-assets.rla","world-cursor-assets.rla","world-bunny-assets.rla","forest-log-assets.rla"}) {
                if(!enemy_preview&&(std::string(filename)=="level1-object-assets.rla"||std::string(filename)=="world-cursor-assets.rla"||std::string(filename)=="world-bunny-assets.rla"))continue;
                const auto pack=(host_data_root/filename).string();
                auto records=rolo::load_preview_assets(pack);
                if(!records){std::fprintf(stderr,"Missing or invalid actor pack: %s\n",pack.c_str());result=1;}
                else for(auto& record:*records) {
                    std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> surface(SDL_CreateSurfaceFrom(static_cast<int>(record.width),static_cast<int>(record.height),SDL_PIXELFORMAT_RGBA32,record.rgba.data(),static_cast<int>(record.width*4)),SDL_DestroySurface);
                    auto* texture=surface?SDL_CreateTextureFromSurface(renderer.get(),surface.get()):nullptr;
                    if(!texture||!SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST)||!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND))result=1;
                    player_textures.push_back({record.kind,record.source,record.palette,record.width,record.height,{texture,SDL_DestroyTexture}});
                }
              }
            }
            if(!static_preview) for(std::uint32_t kind=0;kind<3;++kind) {
                const auto count=std::count_if(textures.begin(),textures.end(),[&](const auto& t){return t.kind==kind;});
                if(count!=1) result=1;
            }
            std::unique_ptr<rolo::OpeningSequence> opening;
            std::unique_ptr<rolo::EndingSequence> ending;bool ending_start_held=false;
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> ending_texture{nullptr,SDL_DestroyTexture};
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> opening_texture(nullptr,SDL_DestroyTexture);
            if(!static_preview){opening=std::make_unique<rolo::OpeningSequence>();opening_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,320,224));if(!opening_texture){result=1;}}
            rolo::EntranceState state;bool paused=false,running=result==0;double accumulator=0;
            rolo::PlayerState player;
            rolo::CameraState camera;
            std::unique_ptr<rolo::Level1EnemySlice> shared_world;
            std::unique_ptr<rolo::Level1TransportWorld> transport_host;
            if(enemy_preview){shared_world=std::make_unique<rolo::Level1EnemySlice>();transport_host=std::make_unique<rolo::Level1TransportWorld>(*shared_world);}
            bool world_map_scene=enemy_preview&&(smoke_path.empty()||handoff_test);
            if(world_map_scene)music.play(16,true);
            std::array<std::uint8_t,80> campaign_flags{};campaign_flags[1]=1;
            rolo::WorldMapCursor world_cursor;
            std::unique_ptr<rolo::WorldMapCursorWorld> world_actors;
            if(enemy_preview){world_actors=std::make_unique<rolo::WorldMapCursorWorld>(world_cursor,0x200);world_actors->step();}
            std::unique_ptr<rolo::Level1MenuWorld> menu_host;
            bool world_map_dirty=true;unsigned world_animation_tick=0;
            std::array<std::uint16_t,64> world_palette{};
            rolo::WorldPaletteCycle world_palette_cycle;
            rolo::WorldRouteState world_route_state;
            rolo::WorldLevelAdmission world_admission;
            bool world_level_pending=false;
            rolo::PlayerInputMapping world_buttons;
            std::uint8_t world_button_latch=0;
            auto world_camera_state=rolo::initialize_world_camera(world_cursor,1280,1280);
            std::unique_ptr<rolo::WorldRouteMap> world_routes;
            auto initialize_world_routes=[&]{
                world_route_state={};world_route_state.anchor_x=world_route_state.snapshot_x=world_cursor.x;
                world_level_pending=false;world_palette_cycle={};
                for(unsigned n=0;n<64;++n)world_palette[n]=rolo::world_map_word(rolo::world_map_data::palette,n*2);
                world_route_state.anchor_y=world_route_state.snapshot_y=world_cursor.y;
                world_buttons={};world_button_latch=0;world_camera_state=rolo::initialize_world_camera(world_cursor,1280,1280);
                world_routes=std::make_unique<rolo::WorldRouteMap>(campaign_flags);
                const auto position=rolo::world_camera_integer(world_camera_state);world_routes->stream(position.x,position.y);
            };
            if(enemy_preview)initialize_world_routes();
            rolo::Level1StatusHud world_status;
            for(unsigned n=0;n<64;++n)world_palette[n]=rolo::world_map_word(rolo::world_map_data::palette,n*2);
            rolo::ScoreAwardState campaign_awards;
            std::uint32_t campaign_score=0;std::uint8_t campaign_lives=3;
            bool jump_key_down=false;
            bool extracted_scene=false,extracted_background=false;
            unsigned extracted_selector=1;float extracted_x=0,extracted_y=0,extracted_width=0,extracted_height=0;
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> extracted_texture(nullptr,SDL_DestroyTexture);
            auto open_extracted=[&](unsigned selector,bool background=false){
                if(selector>=80)return false;
                char folder[24];std::snprintf(folder,sizeof(folder),"selector-%02u",selector);
                const auto file=host_data_root/"../assets/extracted/all-levels"/folder/(background?"background.bmp":"foreground.bmp");
                std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> image(SDL_LoadBMP(file.string().c_str()),SDL_DestroySurface);
                if(!image){SDL_SetWindowTitle(window.get(),"Rolo - extracted preview file missing");return false;}
                std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> texture(SDL_CreateTextureFromSurface(renderer.get(),image.get()),SDL_DestroyTexture);
                if(!texture||!SDL_SetTextureScaleMode(texture.get(),SDL_SCALEMODE_NEAREST))return false;
                extracted_width=static_cast<float>(image->w);extracted_height=static_cast<float>(image->h);
                extracted_texture=std::move(texture);extracted_selector=selector;extracted_background=background;
                extracted_x=0;extracted_y=std::max(0.0f,extracted_height-224);extracted_scene=true;accumulator=0;
                const auto title="Rolo slot "+std::to_string(selector)+(background?" background":" foreground")+(rolo::native_level_connected(static_cast<std::uint16_t>(selector))?" - LEVEL PREVIEW | Enter play | PgUp/PgDn levels | Esc back":" - SPECIAL ART PREVIEW | PgUp/PgDn levels | Esc back");
                SDL_SetWindowTitle(window.get(),title.c_str());return true;
            };
            const auto progress_file=host_data_root/"rolo-progress.sav";
            auto save_progress=[&]{
                if(!enemy_preview||!smoke_path.empty())return;
                rolo::FrameTimingLog::EventScope diagnostic(timing,"SAVE_PROGRESS");
                const rolo::DemoProgressSave saved{campaign_flags,world_cursor.x,world_cursor.y,
                    campaign_score,campaign_awards.next_threshold,campaign_awards.table_offset,campaign_lives};
                const bool ok=rolo::valid_demo_progress(saved)&&rolo::write_demo_progress(progress_file,saved);
                SDL_SetWindowTitle(window.get(),ok?"Rolo native demo - map progress saved":"Rolo native demo - save failed");
            };
            auto load_progress=[&]{
                rolo::FrameTimingLog::EventScope diagnostic(timing,"LOAD_PROGRESS");
                const auto saved=rolo::read_demo_progress(progress_file);
                if(!saved){SDL_SetWindowTitle(window.get(),"Rolo native demo - no valid map save found");return;}
                campaign_flags=saved->flags;campaign_score=saved->score;campaign_lives=saved->lives;
                campaign_awards={saved->score,saved->next_threshold,saved->award_offset};
                world_cursor={saved->x,saved->y,saved->x,saved->y};
                menu_host.reset();world_actors=std::make_unique<rolo::WorldMapCursorWorld>(world_cursor,0x200);world_actors->step();
                initialize_world_routes();world_map_scene=true;world_map_dirty=true;paused=false;accumulator=0;jump_key_down=false;extracted_scene=false;
                music.play(16,true);
                SDL_SetWindowTitle(window.get(),"Rolo native demo - map progress loaded");
            };
            if(enemy_preview&&smoke_path.empty()&&!start_level&&std::filesystem::exists(progress_file))load_progress();
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> world_map_texture(nullptr,SDL_DestroyTexture);
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> menu_texture(nullptr,SDL_DestroyTexture),completed_texture(nullptr,SDL_DestroyTexture);
            if(enemy_preview){
                world_map_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,400,224));
                if(!world_map_texture||!SDL_SetTextureScaleMode(world_map_texture.get(),SDL_SCALEMODE_NEAREST))result=1;
                menu_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,400,224));
                completed_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,16,16));
                for(auto* texture:{menu_texture.get(),completed_texture.get()})if(!texture||!SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST)||!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND))result=1;
            }
            std::vector<std::uint8_t> terrain_low(400*224*4),terrain_high(terrain_low.size());
            std::vector<std::uint8_t> hud_pixels(56*16*4);
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> hud_texture(nullptr,SDL_DestroyTexture);
            std::vector<PreviewTexture> status_textures;
            std::vector<PreviewTexture> suction_textures;
            std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> terrain_low_texture(nullptr,SDL_DestroyTexture),terrain_high_texture(nullptr,SDL_DestroyTexture);
            if(enemy_preview){
                for(const auto& graphic:rolo::suction_particle_data::graphics){
                    auto* texture=SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,graphic.width,graphic.height);
                    if(!texture||!SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST)||!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND))result=1;
                    suction_textures.push_back({0,0,graphic.palette,graphic.width,graphic.height,{texture,SDL_DestroyTexture}});
                }
                hud_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,56,16));
                if(!hud_texture||!SDL_SetTextureBlendMode(hud_texture.get(),SDL_BLENDMODE_BLEND)||!SDL_SetTextureScaleMode(hud_texture.get(),SDL_SCALEMODE_NEAREST))result=1;
                for(unsigned n=0;n<5;++n){
                    auto* texture=SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,32,n==0?24:16);
                    if(!texture||!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND)||!SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST))result=1;
                    status_textures.push_back({0,0,n==4?3u:2u,32,n==0?24u:16u,{texture,SDL_DestroyTexture}});
                }
                terrain_low_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,400,224));
                terrain_high_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,400,224));
                for(auto* texture:{terrain_low_texture.get(),terrain_high_texture.get()})
                    if(!texture||!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND)||!SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST))result=1;
                running=result==0;
            }
            bool jump_button_held=false;
            auto update_jump_key=[&](const SDL_Event& event) {
                if(event.type==SDL_EVENT_KEY_DOWN&&event.key.scancode==SDL_SCANCODE_SPACE)jump_key_down=true;
                if(event.type==SDL_EVENT_KEY_UP&&event.key.scancode==SDL_SCANCODE_SPACE)jump_key_down=false;
                if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST)jump_key_down=false;
            };
            std::int32_t jump_start_y=player.y,jump_rise=0;
            float map_x=0,map_y=map_preview?std::min(480.0f,static_cast<float>(textures.empty()?160:textures[0].height)-160.0f):0;
            if(enemy_preview){camera=shared_world->camera;map_x=static_cast<float>(camera.foreground_x);map_y=static_cast<float>(camera.foreground_y);}
            auto previous=SDL_GetTicksNS();
            auto enter_level=[&](std::uint16_t selector,std::uint8_t entry_selector=0,bool lift_entry=false) {
                rolo::FrameTimingLog::EventScope diagnostic(timing,"ENTER_LEVEL");
                menu_host.reset();
                transport_host.reset();
                shared_world=std::make_unique<rolo::Level1EnemySlice>(&campaign_flags,campaign_score,campaign_lives,selector,nullptr,entry_selector,lift_entry);
                transport_host=std::make_unique<rolo::Level1TransportWorld>(*shared_world);
                shared_world->sound=0xff00;
                music.request(level_music.begin(selector,false,shared_world->visited_c553!=0,shared_world->progress.spawn_selector));
                shared_world->awards=campaign_awards;
                shared_world->completion.world_x=shared_world->completion.saved_x=world_cursor.x;
                shared_world->completion.world_y=shared_world->completion.saved_y=world_cursor.y;
                world_map_scene=false;paused=false;accumulator=0;jump_key_down=false;
                SDL_SetWindowTitle(window.get(),("Rolo native level "+std::to_string(selector)+" - gameplay partial | Enter companions | F6 levels").c_str());
                camera=shared_world->camera;map_x=static_cast<float>(camera.foreground_x);map_y=static_cast<float>(camera.foreground_y);
            };
            if(enemy_preview&&start_level){
                // Explicit development shortcut; ordinary campaign entry uses
                // the original revealed overworld node and its selector.
                campaign_flags[start_level]|=1;enter_level(start_level);
            }
            if(enemy_preview&&browse_level>=0&&!open_extracted(static_cast<unsigned>(browse_level)))result=1;
            auto return_to_world_map=[&] {
                campaign_flags=shared_world->progress.flags;campaign_score=shared_world->score;campaign_lives=shared_world->movement.c51d;
                campaign_awards=shared_world->awards;
                if(shared_world->boss_scene_f283){
                    ending=std::make_unique<rolo::EndingSequence>(campaign_flags,!host_debug_flight&&!shared_world->achievement_debug_used);
                    ending_texture.reset(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,320,224));
                    if(!ending_texture)throw std::runtime_error("Ending texture allocation failed");
                    SDL_SetTextureScaleMode(ending_texture.get(),SDL_SCALEMODE_NEAREST);world_map_scene=false;paused=false;accumulator=0;ending_start_held=true;music.play(16,true);save_progress();return;
                }
                rolo::apply_world_map_completion(static_cast<std::int16_t>(shared_world->completion.source_selector),campaign_flags,world_cursor);
                world_actors=std::make_unique<rolo::WorldMapCursorWorld>(world_cursor,0x200);world_actors->step();
                initialize_world_routes();
                world_map_scene=true;world_map_dirty=true;paused=false;accumulator=0;jump_key_down=false;
                music.play(16,true);
                save_progress(); // Optional native checkpoint after an earned map return.
            };
            auto new_campaign=[&]{
                achievements.lose_life();
                rolo::SceneControlState fresh;rolo::initialize_new_campaign(fresh);
                campaign_flags=fresh.flags;campaign_score=fresh.score.awards.total;
                campaign_lives=fresh.score.lives;campaign_awards=fresh.score.awards;
                world_cursor.x=fresh.origin_x;world_cursor.y=fresh.origin_y;
                menu_host.reset();transport_host.reset();
                world_actors=std::make_unique<rolo::WorldMapCursorWorld>(world_cursor,0x200);world_actors->step();
                initialize_world_routes();world_map_scene=true;world_map_dirty=true;
                paused=false;accumulator=0;jump_key_down=false;
                level_music={};music.play(16,true);
                SDL_SetWindowTitle(window.get(),"Rolo native demo - new game");
            };
            auto advance_player=[&](rolo::PlayerInput input) {
                timing.step();
                if(enemy_preview){
                    try{
                        if(world_map_scene)return;
                        if(shared_world->completion.requested){return_to_world_map();return;}
                        auto pressed=static_cast<std::uint8_t>((input.left?4:0)|(input.right?8:0)|(input.run?64:0)|(input.jump?16:0));
                        if(smoke_path.empty()){const auto keys=gamepad.keys();pressed|=static_cast<std::uint8_t>((keys[SDL_SCANCODE_UP]?1:0)|(keys[SDL_SCANCODE_DOWN]?2:0)|(keys[SDL_SCANCODE_Z]?32:0));}
                        music.request(level_music.step());
                        shared_world->debug_free_flight=host_debug_flight;
                        shared_world->step(pressed);
                        if(smoke_path.empty()&&!host_debug_flight){const auto before=achievements.unlocked;achievements.award_events(shared_world->take_achievement_events());if(shared_world->death_requested||shared_world->game_over_requested)achievements.lose_life();else if(shared_world->completion.requested&&shared_world->achievement_attempt.eligible&&!shared_world->achievement_attempt.life_lost)achievements.clean_completion(shared_world->progress.selector);presentation.notify_unlocks(achievements.unlocked&~before);if(achievements.dirty&&!achievements.save(achievement_file))timing.event("ACHIEVEMENT_SAVE_FAILED");}
                        if(shared_world->sound<91)music.effect(shared_world->sound);
                        shared_world->sound=0xff00;
                        if(shared_world->requested_state==0x1cee&&shared_world->level_transition_latch){
                            const auto selector=shared_world->next_level_selector;const auto entry=shared_world->next_entry_selector;
                            campaign_flags=shared_world->progress.flags;campaign_score=shared_world->score;campaign_lives=shared_world->movement.c51d;campaign_awards=shared_world->awards;
                            const bool lift=shared_world->lift_reload!=0;enter_level(selector,entry,lift);return;
                        }
                        camera=shared_world->camera;map_x=static_cast<float>(camera.foreground_x);map_y=static_cast<float>(camera.foreground_y);
                        jump_button_held=input.jump;
                        if(shared_world->game_over_requested){
                            music.play(21,false);
                            menu_host.reset();transport_host.reset();paused=true;
                            SDL_SetWindowTitle(window.get(),"Rolo native demo - game over | Enter new game | F9 saved map");
                        }else if(shared_world->death_requested){
                            menu_host.reset();transport_host.reset();
                            auto restarted=rolo::rebuild_after_player_death(*shared_world);
                            shared_world=std::move(restarted);shared_world->sound=0xff00;
                            music.request(level_music.begin(shared_world->progress.selector,false,shared_world->visited_c553!=0,shared_world->progress.spawn_selector));
                            transport_host=std::make_unique<rolo::Level1TransportWorld>(*shared_world);
                            camera=shared_world->camera;map_x=camera.foreground_x;map_y=camera.foreground_y;
                            jump_key_down=false;paused=false;
                        }
                        if(shared_world->completion.requested){
                            return_to_world_map();
                            const auto folder=std::filesystem::absolute(argv[0]).parent_path()/"demo-feedback";
                            std::filesystem::create_directories(folder);
                            std::ofstream completion_file(folder/"completion.json");
                            completion_file<<"{\"exit_reached\":true,\"world_map_initialized\":true,\"source_selector\":"<<shared_world->completion.source_selector<<",\"world_x\":"<<world_cursor.x<<",\"world_y\":"<<world_cursor.y<<",\"score\":"<<campaign_score<<"}\n";
                        }
                    }catch(const std::exception& error){std::fprintf(stderr,"Shared world stopped: %s\n",error.what());result=1;running=false;}
                    return;
                }
                const auto camera_input=[&](int previous_x) {
                    return rolo::CameraInput{static_cast<std::uint16_t>(player.pixel_x()),static_cast<std::uint16_t>(player.pixel_y()),static_cast<std::uint16_t>(previous_x),
                        rolo::player_data::width*16,rolo::player_data::height*16,false,false,rolo::camera_data::modes[1],0,static_cast<std::uint16_t>(player.tick)};
                };
                if(player.tick==0) {
                    jump_start_y=player.y;jump_rise=0;camera={};
                    // Default spawn callback $4012, then final level setup $1DD8.
                    // Allocator $294A initializes the previous player X word to zero.
                    rolo::initialize_camera(camera,camera_input(0));
                    rolo::initialize_camera(camera,camera_input(0));
                }
                const int previous_x=player.pixel_x();
                jump_button_held=input.jump;
                if(input.jump&&!player.jump_latched&&player.grounded) {jump_start_y=player.y;jump_rise=0;}
                rolo::update_player(player,input);
                if(player.jumping)jump_rise=std::max(jump_rise,jump_start_y-player.y);
                // $1CB8 calls the camera after the movement/collision subset.
                rolo::update_camera(camera,camera_input(previous_x));
                map_x=static_cast<float>(camera.foreground_x);map_y=static_cast<float>(camera.foreground_y);
                if(player.pixel_y()>rolo::player_data::height*16)paused=true;
            };
            auto advance=[&]() {
                const auto previous_phase=opening->phase;
                opening->step();state=opening->entrance;
                if(previous_phase!=opening->phase&&opening->phase==rolo::OpeningSequence::Phase::Entrance)music.play(2,true);

            };
            auto draw_layer=[&](std::uint32_t kind,float y) {
                for(const auto& texture:textures) if(texture.kind==kind) {
                    const SDL_FRect dst{0,y,static_cast<float>(texture.width),static_cast<float>(texture.height)};
                    if(!SDL_RenderTexture(renderer.get(),texture.texture.get(),nullptr,&dst)) {result=1;running=false;}
                }
            };
            unsigned game_width=320;
            unsigned world_map_draw_width=0;
            auto draw_status_hud=[&](const rolo::Level1StatusHud& status,std::span<const std::uint16_t> palette) {
                        const std::array<std::span<const std::uint8_t>,5> status_data{status.portrait,status.lives,status.score_left,status.score_right,status.rewards};
                        const std::array<std::array<float,2>,5> positions{{{16,12},{56,16},{240,200},{272,200},{272,16}}};
                        for(unsigned n=0;n<5;++n){
                            const auto& texture=status_textures[n];std::vector<std::uint8_t> rgba_pixels(texture.width*texture.height*4);
                            for(unsigned y=0;y<texture.height;++y)for(unsigned x=0;x<texture.width;++x){
                                const auto packed=status_data[n][((x/8)*(texture.height/8)+y/8)*32+(y&7)*4+(x&7)/2];
                                const auto nibble=static_cast<std::uint8_t>((packed>>((x&1)?0:4))&15);
                                const auto rgba=rolo::terrain_pixel_rgba({static_cast<std::uint8_t>(nibble?texture.palette*16+nibble:0),false,nibble!=0},palette);
                                std::copy(rgba.begin(),rgba.end(),rgba_pixels.begin()+(y*texture.width+x)*4);
                            }
                            const SDL_FRect rectangle{positions[n][0]+(n>=2?float(game_width-320):0),positions[n][1],static_cast<float>(texture.width),static_cast<float>(texture.height)};
                            if(!SDL_UpdateTexture(texture.texture.get(),nullptr,rgba_pixels.data(),texture.width*4)||!SDL_RenderTexture(renderer.get(),texture.texture.get(),nullptr,&rectangle)){result=1;running=false;}
                        }
            };
            const rolo::Level1EnemySlice* stationary_background_world=nullptr;
            std::optional<rolo::TerrainMappedDisplay> stationary_background;
            std::uint16_t stationary_background_x{},stationary_background_y{};
            auto draw=[&]() {
                presentation.debug_flight=host_debug_flight;
                if(!widescreen)stationary_background_world=nullptr;
                game_width=widescreen&&!extracted_scene?400:320;
                rolo::HostPresentation::Frame framed(presentation,game_width);
                const bool centred_room=enemy_preview&&!world_map_scene&&shared_world->level_assets.width==320&&game_width>320;
                if(centred_room)game_width=320;
                const int view_shift=enemy_preview?int(camera.x)-rolo::wide_camera_x(camera.x,shared_world->width,game_width):0;
                const int view_x=enemy_preview?int(camera.foreground_x)-view_shift:0;
                const int actor_view_x=enemy_preview?int(camera.x)-view_shift:0;
                const int bg_shift=view_shift; // Extend the frustum around the original view; retain its parallax phase.
                SDL_SetRenderDrawColor(renderer.get(),0,0,0,255);SDL_RenderClear(renderer.get());
                if(centred_room){const SDL_Rect viewport{40,0,320,224};SDL_SetRenderViewport(renderer.get(),&viewport);}
                if(ending){const auto pixels=ending->raster();SDL_UpdateTexture(ending_texture.get(),nullptr,pixels.data(),320*4);const SDL_FRect target{float((int(game_width)-320)/2),0,320,224};SDL_RenderTexture(renderer.get(),ending_texture.get(),nullptr,&target);return;}
                if(enemy_preview&&!world_map_scene&&shared_world->game_over_requested){
                    SDL_SetRenderDrawColor(renderer.get(),220,225,235,255);
                    SDL_RenderDebugText(renderer.get(),124,80,"GAME OVER");
                    SDL_RenderDebugTextFormat(renderer.get(),100,104,"Score %u",shared_world->score);
                    SDL_RenderDebugText(renderer.get(),72,136,"Enter: new game");
                    SDL_RenderDebugText(renderer.get(),72,152,"F9: saved jigsaw map");
                    SDL_RenderDebugText(renderer.get(),48,192,"Original screen pending");return;
                }
                if(extracted_scene){
                    const SDL_FRect source{extracted_x,extracted_y,std::min(320.0f,extracted_width),std::min(224.0f,extracted_height)};
                    const SDL_FRect destination{0,0,source.w,source.h};
                    if(!SDL_RenderTexture(renderer.get(),extracted_texture.get(),&source,&destination)){result=1;running=false;}
                    return;
                }
                if(world_map_scene){
                    const auto world_camera=rolo::world_camera_integer(world_camera_state);
                    const auto map_view_x=rolo::wide_camera_x(world_camera.x,1280,game_width);
                    if(world_map_dirty||world_map_draw_width!=game_width){
                        const auto pixels=rolo::raster_world_map(campaign_flags,map_view_x,world_camera.y,world_palette,game_width,world_animation_tick);
                        rolo::Level1ProgressState blank_rewards;
                        rolo::publish_level1_status_hud(world_status,campaign_lives,campaign_score,blank_rewards,[](auto){});
                        const SDL_Rect region{0,0,int(game_width),224};
                        if(!SDL_UpdateTexture(world_map_texture.get(),&region,pixels.data(),game_width*4)){result=1;running=false;}
                        world_map_dirty=false;world_map_draw_width=game_width;
                    }
                    const SDL_FRect dest{0,0,float(game_width),224};
                    if(!SDL_RenderTexture(renderer.get(),world_map_texture.get(),&dest,&dest)){result=1;running=false;}
                    std::array<std::uint8_t,16*16*4> marker_pixels{};
                    for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x){
                        const auto packed=rolo::world_map_data::completed_marker[((x/8)*2+y/8)*32+(y&7)*4+(x&7)/2];
                        const auto ink=static_cast<std::uint8_t>((packed>>((x&1)?0:4))&15);
                        const auto rgba=rolo::terrain_pixel_rgba({static_cast<std::uint8_t>(32+ink),false,ink!=0},world_palette);
                        std::copy(rgba.begin(),rgba.end(),marker_pixels.begin()+(y*16+x)*4);
                    }
                    SDL_UpdateTexture(completed_texture.get(),nullptr,marker_pixels.data(),16*4);
                    for(const auto node:rolo::completed_world_map_nodes(campaign_flags)){
                        const SDL_FRect marker{static_cast<float>(int(node[0])-map_view_x-5),static_cast<float>(int(node[1])-world_camera.y),16,16};
                        SDL_RenderTexture(renderer.get(),completed_texture.get(),nullptr,&marker);
                    }
                    for(auto* actor:{&world_actors->actor(),&world_actors->bunny()}){
                    const auto cursor=rolo::actor_sprite_view(*actor,std::uint16_t(map_view_x),world_camera.y);
                    const auto sprite_palette=static_cast<unsigned>(((actor->longword(4)==0x14ede?rolo::world_bunny_data::definition:rolo::world_cursor_data::definition).word(6)>>13)&3);
                    const auto found=std::find_if(player_textures.begin(),player_textures.end(),[&](const auto& t){return t.source==cursor.graphics&&t.width==cursor.width&&t.height==cursor.height&&t.palette==sprite_palette;});
                    if(found==player_textures.end()){result=1;running=false;}else{
                        const SDL_FRect target{static_cast<float>(cursor.x),static_cast<float>(cursor.y),static_cast<float>(cursor.width),static_cast<float>(cursor.height)};
                        SDL_RenderTextureRotated(renderer.get(),found->texture.get(),nullptr,&target,0,nullptr,cursor.flip_x?SDL_FLIP_HORIZONTAL:SDL_FLIP_NONE);
                    }
                    }
                    SDL_SetRenderDrawColor(renderer.get(),255,255,255,255);
                    draw_status_hud(world_status,world_palette);
                    SDL_RenderDebugText(renderer.get(),8,232,"WORLD MAP - F6 CHOOSE ANY LEVEL");
                    SDL_RenderDebugTextFormat(renderer.get(),8,246,"Score %u  Lives %u",campaign_score,static_cast<unsigned>(campaign_lives));
                    SDL_RenderDebugText(renderer.get(),8,260,world_route_state.pause?"MAP PAUSED: arrows move bunny":"Arrows: routes  Space: enter level");
                    if(world_level_pending)SDL_RenderDebugTextFormat(renderer.get(),8,274,"Level %u rebuild not bound",world_admission.current_f2f6);
                    else SDL_RenderDebugText(renderer.get(),8,274,"F5 save map  F9 load map; autosave on completion");return;
                }
                if(map_preview && !textures.empty()) {
                    if(enemy_preview&&map_background&&textures.size()==2){
                        const bool fixed_background=widescreen&&rolo::camera_data::modes[shared_world->level_assets.selector]!=6;
                        if(fixed_background&&stationary_background_world!=shared_world.get()){
                            stationary_background.emplace(shared_world->mapping);
                            stationary_background->names=shared_world->background_display.names;
                            stationary_background_x=std::uint16_t(camera.background_x-bg_shift);stationary_background_y=camera.background_y;
                            stationary_background_world=shared_world.get();
                        }
                        const auto bg_x=fixed_background?stationary_background_x:std::uint16_t(camera.background_x-bg_shift);
                        const auto bg_y=fixed_background?stationary_background_y:camera.background_y;
                        const auto& bg_display=fixed_background?*stationary_background:shared_world->background_display;
                        auto background_pixels=rolo::wide_forest_background(bg_x,shared_world->palette,game_width);
                        if(shared_world->level_assets.bank!=1||shared_world->progress.selector==6||shared_world->progress.selector==9||shared_world->progress.selector==10){
                            for(unsigned y=0;y<224;++y)for(unsigned x=0;x<game_width;++x){
                                auto pixel=rolo::terrain_plane_pixel(shared_world->patterns,bg_display,std::uint16_t(bg_x+x),bg_y+y);
                                auto rgba=rolo::terrain_pixel_rgba(pixel,shared_world->palette);rgba[3]=255;
                                std::copy(rgba.begin(),rgba.end(),background_pixels.begin()+(y*game_width+x)*4);
                            }
                        }
                        const SDL_Rect rectangle{0,0,int(game_width),224};const SDL_FRect viewport{0,0,float(game_width),224};
                        if(!SDL_UpdateTexture(textures[1].texture.get(),&rectangle,background_pixels.data(),game_width*4)||
                           !SDL_RenderTexture(renderer.get(),textures[1].texture.get(),&viewport,&viewport)){result=1;running=false;}
                    }else if(map_background && textures.size()==2) {
                        const int offset=(player_preview?camera.background_x:static_cast<int>(map_x)/2)%512;
                        const int first=std::min(320,512-offset);
                        const SDL_FRect bg_source{static_cast<float>(offset),0,static_cast<float>(first),static_cast<float>(artwork_height)},bg_dest{0,0,static_cast<float>(first),static_cast<float>(artwork_height)};
                        if(!SDL_RenderTexture(renderer.get(),textures[1].texture.get(),&bg_source,&bg_dest)) {result=1;running=false;}
                        if(first<320) {
                            const SDL_FRect wrap_source{0,0,static_cast<float>(320-first),static_cast<float>(artwork_height)},wrap_dest{static_cast<float>(first),0,static_cast<float>(320-first),static_cast<float>(artwork_height)};
                            if(!SDL_RenderTexture(renderer.get(),textures[1].texture.get(),&wrap_source,&wrap_dest)) {result=1;running=false;}
                        }
                    }
                    const SDL_FRect source{map_x,map_y,320,static_cast<float>(artwork_height)},dest{0,0,float(enemy_preview?game_width:320),static_cast<float>(artwork_height)};
                    if(enemy_preview){
                        std::optional<rolo::TerrainMappedDisplay> expanded_display;
                        if(game_width>320)expanded_display.emplace(rolo::wide_terrain_display(shared_world->backing,shared_world->mapping,std::uint16_t(view_x),camera.foreground_y,game_width,224));
                        rolo::raster_terrain_viewport(shared_world->patterns,expanded_display?*expanded_display:shared_world->display,shared_world->palette,
                            std::uint16_t(view_x),camera.foreground_y,game_width,224,std::span(terrain_low).first(game_width*224*4),std::span(terrain_high).first(game_width*224*4));
                        const SDL_Rect visible{0,0,int(game_width),224};const SDL_FRect visible_source{0,0,float(game_width),224};
                        if(!SDL_UpdateTexture(terrain_low_texture.get(),&visible,terrain_low.data(),game_width*4)||
                           !SDL_UpdateTexture(terrain_high_texture.get(),&visible,terrain_high.data(),game_width*4)||
                           !SDL_RenderTexture(renderer.get(),terrain_low_texture.get(),&visible_source,&dest)){result=1;running=false;}
                    }else if(!SDL_RenderTexture(renderer.get(),textures[0].texture.get(),&source,&dest)) {result=1;running=false;}
                    if(enemy_preview){
                        const auto sprite_order=rolo::native_actor_paint_order(shared_world->pool,shared_world->contact_root_word);
                        for(const auto i:sprite_order){
                            const auto& actor=shared_world->pool.actors[i];
                            if(rolo::signed_word(actor.word(0))<0||!actor.longword(28)||(actor.byte(125)&2))continue;
                            auto sprite=rolo::actor_sprite_view(actor,std::uint16_t(actor_view_x),camera.foreground_y);
                            if(rolo::dynamic_platform_data::is_definition(actor.longword(4)))sprite.graphics=0x5854524c;
                            const auto palette=(shared_world->definition(actor.longword(4)).word(6)>>13)&3;
                            if(sprite.graphics==0x5854524e){
                                for(unsigned y=0;y<16;++y)for(unsigned x=0;x<56;++x){
                                    const auto packed=shared_world->hud.pixels[((x/8)*2+y/8)*32+(y&7)*4+(x&7)/2];
                                    const auto nibble=static_cast<std::uint8_t>((packed>>((x&1)?0:4))&15);
                                    const auto rgba=rolo::terrain_pixel_rgba({static_cast<std::uint8_t>(nibble?palette*16+nibble:0),false,nibble!=0},shared_world->palette);
                                    std::copy(rgba.begin(),rgba.end(),hud_pixels.begin()+(y*56+x)*4);
                                }
                                const SDL_FRect rectangle{static_cast<float>(sprite.x),static_cast<float>(sprite.y),56,16};
                                if(!SDL_UpdateTexture(hud_texture.get(),nullptr,hud_pixels.data(),56*4)||!SDL_RenderTexture(renderer.get(),hud_texture.get(),nullptr,&rectangle)){result=1;running=false;}
                                continue;
                            }
                            auto found=std::find_if(player_textures.begin(),player_textures.end(),[&](const auto& t){return t.source==sprite.graphics&&t.palette==palette&&t.width==sprite.width&&t.height==sprite.height;});
                            if(found==player_textures.end()&&sprite.graphics==0x5854524c){
                                auto* texture=SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,sprite.width,sprite.height);
                                if(!texture||!SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST)||!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND)){if(texture)SDL_DestroyTexture(texture);result=1;running=false;continue;}
                                player_textures.push_back({0,sprite.graphics,static_cast<std::uint32_t>(palette),static_cast<std::uint32_t>(sprite.width),static_cast<std::uint32_t>(sprite.height),{texture,SDL_DestroyTexture}});found=std::prev(player_textures.end());
                            }
                            if(found==player_textures.end()){std::fprintf(stderr,"Missing shared actor texture %x\n",sprite.graphics);result=1;running=false;continue;}
                            const auto macro_key=sprite.graphics==0x5854524c?(std::uint64_t(shared_world->level_assets.bank)<<32)|actor.longword(46):0;
                            if(!found->pixels_current||found->cached_colours!=shared_world->palette||found->cached_macro!=macro_key){
                                std::vector<std::uint8_t> actor_pixels(std::size_t(sprite.width)*sprite.height*4);
                                if(sprite.graphics==0x5854524c)rolo::raster_dynamic_macro(shared_world->level_assets.terrain_bank(),actor.longword(46),palette,shared_world->palette,actor_pixels);
                                else rolo::raster_actor_frame(sprite.graphics,sprite.width,sprite.height,palette,shared_world->palette,actor_pixels);
                                if(!SDL_UpdateTexture(found->texture.get(),nullptr,actor_pixels.data(),sprite.width*4)){result=1;running=false;continue;}
                                found->cached_colours=shared_world->palette;found->cached_macro=macro_key;found->pixels_current=true;
                            }
                            const SDL_FRect rectangle{static_cast<float>(sprite.x),static_cast<float>(sprite.y),static_cast<float>(sprite.width),static_cast<float>(sprite.height)};
                            SDL_RenderTextureRotated(renderer.get(),found->texture.get(),nullptr,&rectangle,0,nullptr,static_cast<SDL_FlipMode>((sprite.flip_x?SDL_FLIP_HORIZONTAL:0)|(sprite.flip_y?SDL_FLIP_VERTICAL:0)));
                        }
                        for(const auto& particle:shared_world->suction_particles.sprites){
                            const auto& graphic=rolo::suction_particle_data::graphics[particle.graphic];
                            std::vector<std::uint8_t> pixels(graphic.width*graphic.height*4);
                            rolo::raster_actor_patterns(std::span<const std::uint8_t>(rolo::suction_particle_data::patterns).subspan(graphic.first+particle.phase*graphic.frame_size,graphic.frame_size),graphic.width,graphic.height,graphic.palette,shared_world->palette,pixels);
                            auto* texture=suction_textures[particle.graphic].texture.get();
                            if(!texture||!SDL_UpdateTexture(texture,nullptr,pixels.data(),graphic.width*4)){result=1;running=false;continue;}
                            const SDL_FRect rectangle{float(particle.x+view_shift),float(particle.y),float(graphic.width),float(graphic.height)};
                            if(!SDL_RenderTextureRotated(renderer.get(),texture,nullptr,&rectangle,0,nullptr,particle.flip?SDL_FLIP_HORIZONTAL:SDL_FLIP_NONE)){result=1;running=false;}
                        }
                        const SDL_FRect high_source{0,0,float(game_width),224};
                        if(!SDL_RenderTexture(renderer.get(),terrain_high_texture.get(),&high_source,&dest)){result=1;running=false;}
                        draw_status_hud(shared_world->status_hud,shared_world->palette);
                    }
                    else if(player_preview) {
                        for(const auto* animation:{&player.body,&player.head}) {
                            if(animation->current<0)continue;
                            const auto& frame=rolo::player_animation_data::frames[animation->current];
                            const auto selected=player.facing_left?frame.right_graphics:frame.left_graphics;
                            const auto graphics=selected?selected:(player.facing_left?frame.left_graphics:frame.right_graphics);
                            const auto found=std::find_if(player_textures.begin(),player_textures.end(),[&](const auto& t){return t.source==graphics&&t.width==frame.width&&t.height==frame.height;});
                            if(found==player_textures.end()) {result=1;running=false;continue;}
                            const SDL_FRect sprite{static_cast<float>(player.pixel_x()+(player.facing_left?-frame.offset_x:frame.offset_x)-frame.width/2)-map_x,
                                // $3344..$3348: ROM object Y + frame offset Y - frame height.
                                static_cast<float>(player.pixel_y()+frame.offset_y-frame.height)-map_y,static_cast<float>(frame.width),static_cast<float>(frame.height)};
                            if(!SDL_RenderTextureRotated(renderer.get(),found->texture.get(),nullptr,&sprite,0,nullptr,selected?SDL_FLIP_NONE:SDL_FLIP_HORIZONTAL)) {result=1;running=false;}
                        }
                    }
                }
                else if(static_preview) draw_layer(4,0);
                else {
                    const auto pixels=opening->raster();
                    const SDL_FRect opening_view{float((game_width-320)/2),0,320,224};
                    if(!SDL_UpdateTexture(opening_texture.get(),nullptr,pixels.data(),320*4)||!SDL_RenderTexture(renderer.get(),opening_texture.get(),nullptr,&opening_view)){result=1;running=false;}

                }
                SDL_SetRenderDrawColor(renderer.get(),220,225,235,255);
                if(map_preview) {
                    if(player_preview) {
                        if(enemy_preview)SDL_RenderDebugTextFormat(renderer.get(),8,232,"LEVEL %u NATIVE DEVELOPMENT DEMO",shared_world->progress.selector);
                        else SDL_RenderDebugText(renderer.get(),8,232,"ROM CAMERA; GAMEPLAY STILL PARTIAL");
                        if(enemy_preview)SDL_RenderDebugTextFormat(renderer.get(),8,246,"Score %u  Lives %u%s",shared_world->score,static_cast<unsigned>(shared_world->movement.c51d),paused?" (paused)":"");
                        else SDL_RenderDebugTextFormat(renderer.get(),8,246,"Space %s  Rise %.1f px%s",jump_button_held?"HELD":"released",jump_rise/65536.0,paused?" (paused)":"");
                        if(menu_host&&menu_host->active){
                            const auto original_menu=rolo::raster_companion_menu(menu_host->patterns,menu_host->menu.selector,shared_world->movement.c510,menu_host->portraits());
                            const auto image=rolo::wide_companion_menu(original_menu,game_width);
                            std::vector<std::uint8_t> pixels(game_width*224*4);auto palette=rolo::level1_terrain_data::palette_words;
                            for(unsigned n=0;n<32;++n)palette[n]=rolo::companion_menu_word(rolo::level1_companion_menu_data::palette,n*2);
                            if(!menu_host->palette_ready)for(unsigned n=1;n<32;++n)palette[n]=0x0eee;
                            for(unsigned n=0;n<image.size();++n){const auto rgba=rolo::terrain_pixel_rgba({image[n],false,true},palette);std::copy(rgba.begin(),rgba.end(),pixels.begin()+n*4);}
                            const SDL_Rect menu_region{0,0,int(game_width),224};SDL_UpdateTexture(menu_texture.get(),&menu_region,pixels.data(),game_width*4);
                            const SDL_FRect window{0,0,float(game_width),static_cast<float>(menu_host->menu.slide*8)},menu_destination{0,0,float(game_width),window.h};
                            SDL_RenderTexture(renderer.get(),menu_texture.get(),&window,&menu_destination);draw_status_hud(shared_world->status_hud,palette);
                            SDL_RenderDebugText(renderer.get(),8,260,"Arrows select  Space confirm");
                        }else SDL_RenderDebugText(renderer.get(),8,260,"Arrows move X run Space jump Enter menu");
                        SDL_RenderDebugText(renderer.get(),8,274,"R reset  P pause  Esc close");return;
                    }
                    SDL_RenderDebugText(renderer.get(),8,168,"MAP VIEWER; NO GAMEPLAY");
                    SDL_RenderDebugTextFormat(renderer.get(),8,182,"View %.0f,%.0f",static_cast<double>(map_x),static_cast<double>(map_y));
                    SDL_RenderDebugText(renderer.get(),8,196,"Arrow keys pan  R reset  Esc close");
                    SDL_RenderDebugText(renderer.get(),8,210,map_background?"Forest background; actors pending":"Full world map; unlocks pending");
                    return;
                }
                // Keep original title artwork clear of development diagnostics.
            };
            if(!smoke_path.empty()&&enemy_preview&&browse_level>=0){
                std::filesystem::create_directories(smoke_path);unsigned loaded=0;
                for(unsigned selector=0;selector<80&&running;++selector)for(bool background:{false,true}){
                    if(!open_extracted(selector,background)){result=1;running=false;break;}draw();SDL_RenderPresent(renderer.get());++loaded;
                    if(!background&&(selector==1||selector==30||selector==79)){
                        std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/("selector-"+std::to_string(selector)+".bmp")).string().c_str()))result=1;
                    }
                }
                std::ofstream report(std::filesystem::path(smoke_path)/"preview-load.json");report<<"{\"loaded_layers\":"<<loaded<<",\"status\":"<<result<<"}\n";running=false;
            }
            if(handoff_test&&enemy_preview){
                std::filesystem::create_directories(smoke_path);draw();
                std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/"handoff-map.bmp").string().c_str()))result=1;
                world_map_scene=false;menu_host=std::make_unique<rolo::Level1MenuWorld>(*shared_world);menu_host->begin();for(unsigned i=0;i<40;++i)menu_host->step(0);draw();
                capture.reset(SDL_RenderReadPixels(renderer.get(),nullptr));
                if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/"handoff-menu.bmp").string().c_str()))result=1;
                SDL_RenderPresent(renderer.get());running=false;
            }
            if(!smoke_path.empty()&&running&&enemy_preview&&smoke_path.find("all-levels")!=std::string::npos){
                std::filesystem::create_directories(smoke_path);std::array<bool,8> captured{};unsigned loaded=0;
                for(auto selector:rolo::all_native_level_data::selectors){
                    enter_level(selector);
                    for(unsigned tick=0;tick<60&&running&&!world_map_scene;++tick)advance_player({false,true,false,tick>=20&&tick<40});
                    if(!running)break;draw();if(!running)break;++loaded;
                    const auto bank=shared_world->level_assets.bank;
                    if(!captured.at(bank)){
                        captured[bank]=true;
                        std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/("bank-"+std::to_string(bank)+".bmp")).string().c_str())){result=1;break;}
                    }
                }
                if(loaded!=rolo::all_native_level_data::selectors.size())result=1;
                std::ofstream report(std::filesystem::path(smoke_path)/"result.json");report<<"{\"native_levels_loaded\":"<<loaded<<",\"status\":"<<result<<"}\n";
                running=false;
            }
            if(!smoke_path.empty()&&running&&enemy_preview&&smoke_path.find("life-cycle")!=std::string::npos){
                std::filesystem::create_directories(smoke_path);
                unsigned restarts=0;
                for(unsigned selector=1;selector<=13;++selector){
                campaign_lives=3;campaign_score=54321;campaign_awards.total=54321;
                campaign_awards.table_offset=4;campaign_awards.next_threshold=2000000;
                enter_level(static_cast<std::uint16_t>(selector));
                const auto checkpoint=shared_world->checkpoint;
                for(unsigned n=0;n<4;++n){
                    auto& actor=shared_world->pool.resolve(shared_world->movement.controlled);
                    actor.byte(124,actor.byte(124)|1);shared_world->movement.contact.hit_gate_c519=1;
                    advance_player({});draw();
                    if(n<3&&(world_map_scene||paused||shared_world->progress.selector!=selector||shared_world->movement.c51d!=2-n))throw std::logic_error("SDL automatic restart handoff failed");
                    if(n<3){
                        const auto& reborn=shared_world->pool.resolve(shared_world->movement.controlled);
                        if(reborn.word(12)!=checkpoint.x||reborn.word(16)!=checkpoint.y||shared_world->score!=54321||shared_world->awards.table_offset!=4||shared_world->awards.next_threshold!=2000000||shared_world->progress.key_c550||shared_world->progress.piece_c551)throw std::logic_error("SDL restart state retention failed");
                        ++restarts;
                    }
                    if(n==3&&(!shared_world->game_over_requested||!paused))throw std::logic_error("SDL game over handoff failed");
                    if(n==3){std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> image(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        if(!image||!SDL_SaveBMP(image.get(),(std::filesystem::path(smoke_path)/"game-over.bmp").string().c_str()))result=1;}
                }
                new_campaign();
                if(!world_map_scene||paused||campaign_lives!=3||campaign_score||campaign_flags[1]!=1||world_cursor.x!=280||world_cursor.y!=472)throw std::logic_error("SDL new campaign handoff failed");
                }
                draw();
                std::ofstream report(std::filesystem::path(smoke_path)/"result.json");
                report<<"{\"selectors\":13,\"restarts\":"<<restarts<<",\"game_over_handoffs\":13,\"new_campaigns\":13,\"status\":"<<result<<"}\n";
                std::printf("SDL life-cycle: %u restarts, 13 game-over/new-campaign handoffs, status %d\n",restarts,result);running=false;
            }
            if(!smoke_path.empty()&&running&&enemy_preview&&start_level>=3){
                std::filesystem::create_directories(smoke_path);
                if(start_level==35){
                    const rolo::PlayerCheckpoint cart_entry{1160,480};transport_host.reset();
                    shared_world=std::make_unique<rolo::Level1EnemySlice>(nullptr,0,3,35,&cart_entry);
                    transport_host=std::make_unique<rolo::Level1TransportWorld>(*shared_world);
                }
                for(unsigned tick=0;tick<180&&running;++tick){
                    if((start_level==8||start_level==23)&&(tick==0||tick==90||tick==179)){
                        auto&body=shared_world->pool.resolve(shared_world->movement.controlled);
                        const unsigned x=start_level==23?(tick==90?176:480):(tick==0?2400:tick==90?3136:3344),y=start_level==23?(tick==90?1376:1584):(tick==179?736:768);
                        body.longword(12,(x-16)<<16);body.longword(16,(y-8)<<16);
                        body.longword(58,0);body.longword(62,0);body.longword(98,0);
                        shared_world->movement.contact.hit_gate_c519=shared_world->movement.contact.hit_gate_c51a=0;
                        shared_world->death_requested=false;paused=false;
                        rolo::initialize_camera(shared_world->camera,shared_world->camera_input());
                        shared_world->stream(shared_world->camera.foreground_x,shared_world->camera.foreground_y);
                        if(start_level==23&&tick==90){
                            shared_world->list();shared_world->animate(); // Publish contact geometry for the newly streamed pickup.
                            std::uint32_t gas=0;for(auto&e:shared_world->spawn_events)if(e.marker==shared_world->map_identity+1124)gas=e.actor;
                            if(!gas)throw std::logic_error("Level23 smoke gas bottle marker absent");
                            const auto& pickup=shared_world->pool.resolve(gas);body.word(12,pickup.word(12));body.word(16,pickup.word(16));
                            shared_world->invoke_actor_callback(gas,0xb702);
                            if(shared_world->movement.c513!=255)throw std::logic_error("Level23 smoke gas bottle contact failed");
                        }
                    }
                    if(start_level==35)advance_player({false,tick>=120,false,tick==30});
                    else advance_player({false,tick<120,false,tick>=30&&tick<60});draw();
                    if(tick==0||tick==90||tick==179){
                        std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        const auto filename=(std::filesystem::path(smoke_path)/("level"+std::to_string(start_level)+"-"+std::to_string(tick)+".bmp")).string();
                        if(!capture||!SDL_SaveBMP(capture.get(),filename.c_str()))result=1;
                    }
                    SDL_RenderPresent(renderer.get());
                }
                running=false;
            }
            if(!smoke_path.empty() && running && enemy_preview){
                std::filesystem::create_directories(smoke_path);
                std::ofstream trace(std::filesystem::path(smoke_path)/"shared-world.csv");
                trace<<"tick,player_x,player_y,enemy_x,enemy_y,enemy_phase,contact,damage\n";
                for(unsigned tick=0;tick<(start_level==2?90u:200u)&&running;++tick){
                    advance_player({false,true,false,tick>=90&&tick<115});draw();
                    const auto& p=shared_world->pool.resolve(shared_world->movement.controlled);const auto& e=shared_world->pool.resolve(shared_world->enemy_key);
                    trace<<tick<<','<<p.word(12)<<','<<p.word(16)<<','<<e.word(12)<<','<<e.word(16)<<','<<unsigned(e.byte(46))<<','<<unsigned(e.byte(123))<<','<<unsigned(shared_world->movement.contact.hit_gate_c519)<<'\n';
                    if(tick==0||tick==89||tick==120||tick==199){
                        std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        const auto filename=(std::filesystem::path(smoke_path)/("shared-world-"+std::to_string(tick)+".bmp")).string();
                        if(!capture||!SDL_SaveBMP(capture.get(),filename.c_str()))result=1;
                    }
                    SDL_RenderPresent(renderer.get());
                }
                if(running&&start_level==2){
                    auto& base=shared_world->pool.resolve(shared_world->input.base_key);
                    base.byte(52,255);shared_world->input.action.c51c=3;
                    rolo::update_player_presentation(shared_world->pool,shared_world->movement.controlled,shared_world->input.base_key,shared_world->presentation,*shared_world);
                    shared_world->animate();
                    shared_world->suction_particles.step(base,shared_world->pool.resolve(base.longword(84)),3,0,0,0,camera.foreground_x,camera.foreground_y);
                    draw();std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> suction(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                    if(!suction||!SDL_SaveBMP(suction.get(),(std::filesystem::path(smoke_path)/"level2-suction.bmp").string().c_str()))result=1;
                    base.byte(52,0);shared_world->suction_particles.sprites.clear();
                    shared_world->stream(0,592);camera.foreground_x=0;camera.foreground_y=592;
                    draw();std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> image(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                    if(!image||!SDL_SaveBMP(image.get(),(std::filesystem::path(smoke_path)/"level2-waves.bmp").string().c_str()))result=1;
                }
                if(running&&start_level!=2){
                    transport_host.reset();
                    shared_world=std::make_unique<rolo::Level1EnemySlice>();
                    transport_host=std::make_unique<rolo::Level1TransportWorld>(*shared_world);
                    shared_world->stream(840,464);shared_world->list();shared_world->animate();
                    camera.foreground_x=840;camera.foreground_y=464;map_x=840;map_y=464;
                    draw();
                    std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                    const auto filename=(std::filesystem::path(smoke_path)/"cage-tree.bmp").string();
                    if(!capture||!SDL_SaveBMP(capture.get(),filename.c_str()))result=1;
                }
                if(running&&start_level!=2){
                    auto capture_scene=[&](const char* name){
                        draw();std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> image(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        if(!image||!SDL_SaveBMP(image.get(),(std::filesystem::path(smoke_path)/name).string().c_str()))result=1;
                    };
                    world_map_scene=true;world_map_dirty=true;capture_scene("world-map-before.bmp");
                    enter_level(1);
                    {
                        const auto original_palette=shared_world->palette;
                        rolo::NativePaletteEffects effects;effects.colours=original_palette;effects.begin_black();
                        for(unsigned n=0;n<8;++n){effects.interrupt_palette_step();effects.publish([&](auto words){std::copy(words.begin(),words.end(),shared_world->palette.begin());});}
                        if(!effects.complete_black())throw std::logic_error("Palette smoke black continuation incomplete");
                        capture_scene("palette-black.bmp");
                        effects.begin_level_palette(original_palette);effects.inhibited_c48d=0;
                        for(unsigned n=0;n<8;++n){effects.interrupt_palette_step();effects.publish([&](auto words){std::copy(words.begin(),words.end(),shared_world->palette.begin());});}
                        if(shared_world->palette!=original_palette)throw std::logic_error("Palette smoke restore differs");
                        capture_scene("palette-restored.bmp");
                    }
                    auto& world=*shared_world;auto& body=world.pool.resolve(world.movement.controlled);
                    const auto key=rolo::allocate_actor_chain(world.pool,{0x144a4,1200u<<16,752u<<16,0,0,0},world);
                    if(!key.success)throw std::logic_error("Smoke key allocation");
                    world.pool.resolve(key.head).word(70,48);world.invoke_actor_callback(key.head,0xb314);
                    for(unsigned n=0;n<100&&!world.pool.resolve(key.head).byte(116);++n)world.invoke_actor_callback(key.head,0xb386);
                    for(unsigned n=0;n<2;++n){
                        const auto bunny=rolo::allocate_actor_chain(world.pool,{0x13f54,body.longword(12),body.longword(16),0,0,0},world);
                        if(!bunny.success)throw std::logic_error("Smoke bunny allocation");
                        world.list();world.animate();world.invoke_actor_callback(bunny.head,0xa8bc);
                    }
                    auto piece=std::find_if(world.pool.actors.begin(),world.pool.actors.end(),[](const auto& a){return rolo::signed_word(a.word(0))>=0&&a.longword(4)==0x14482;});
                    if(piece==world.pool.actors.end())throw std::logic_error("Smoke earned piece missing");
                    for(unsigned n=0;n<100&&!piece->byte(116);++n)rolo::update_reward_curve(*piece,world);
                    menu_host=std::make_unique<rolo::Level1MenuWorld>(world);menu_host->begin();
                    for(unsigned n=0;n<29;++n)menu_host->step(0);
                    menu_host->menu.selector=2;capture_scene("start-menu-bunny.bmp");
                    menu_host->step(16);for(unsigned n=0;n<29;++n)menu_host->step(0);
                    if(menu_host->active||world.movement.controlled_type!=20||world.movement.controlled==world.input.base_key)throw std::logic_error("Menu bunny selection failed");
                    for(unsigned n=0;n<24;++n)advance_player({false,true,false,false});
                    capture_scene("controlled-bunny.bmp");
                    menu_host=std::make_unique<rolo::Level1MenuWorld>(world);menu_host->begin();
                    for(unsigned n=0;n<29;++n)menu_host->step(0);
                    menu_host->menu.selector=3;menu_host->step(16);for(unsigned n=0;n<29;++n)menu_host->step(0);
                    if(world.movement.controlled!=world.input.base_key||world.movement.c510)throw std::logic_error("Menu Rolo selection failed");
                    world.add_score(100);world.stream(1600,592);world.list();world.animate();
                    const auto exit=std::find_if(world.pool.actors.begin(),world.pool.actors.end(),[](const auto& a){return rolo::signed_word(a.word(0))>=0&&a.longword(4)==0x14e78;});
                    if(exit==world.pool.actors.end())throw std::logic_error("Smoke exit missing");
                    body.longword(12,exit->longword(12));body.longword(16,exit->longword(16)+0x100000);
                    rolo::update_level1_exit(*exit,world.progress,32,world);
                    if(world.requested_state!=0x1a6e)throw std::logic_error("Smoke exit did not request world map");
                    rolo::request_level1_world_handoff(world.completion,world.progress);advance_player({});
                    if(!world_map_scene||!(campaign_flags[2]&1)||campaign_score!=world.score||world_cursor.x!=280||world_cursor.y!=472)throw std::logic_error("Smoke campaign handoff mismatch");
                    capture_scene("world-map-after.bmp");
                    for(unsigned tick=0;tick<32;++tick){
                        rolo::update_world_route(world_actors->actor(),world_route_state,{255,0,0,0},*world_routes);
                        world_actors->update_bunny(false,{});
                        world_cursor.x=world_route_state.snapshot_x;world_cursor.y=world_route_state.snapshot_y;
                        rolo::update_world_camera(world_camera_state,world_cursor,1280,1280);world_actors->step();
                        const auto position=rolo::world_camera_integer(world_camera_state);world_routes->stream(position.x,position.y);
                    }
                    if(rolo::world_map_selector_at(world_cursor.x,world_cursor.y)!=2)throw std::logic_error("Earned map section route failed");
                    world_map_dirty=true;capture_scene("world-map-upper-node.bmp");
                    const auto stationary_x=world_cursor.x,stationary_y=world_cursor.y;
                    const auto bunny_start=world_actors->bunny().word(12);world_route_state.pause=1;
                    for(unsigned tick=0;tick<48;++tick){
                        rolo::update_world_route(world_actors->actor(),world_route_state,{0,0,0,255},*world_routes);
                        world_actors->update_bunny(true,{0,0,0,255});
                        rolo::WorldMapCursor target;target.x=world_actors->bunny().word(12);target.y=world_actors->bunny().word(16);
                        rolo::update_world_camera(world_camera_state,target,1280,1280);world_actors->step();
                        rolo::update_world_palette(world_palette_cycle,world_palette);++world_animation_tick;
                        const auto position=rolo::world_camera_integer(world_camera_state);world_routes->stream(position.x,position.y);
                    }
                    if(world_cursor.x!=stationary_x||world_cursor.y!=stationary_y||world_actors->bunny().word(12)<=bunny_start)throw std::logic_error("Paused map bunny control failed");
                    world_map_dirty=true;capture_scene("world-map-paused-bunny.bmp");
                    const auto saved_flags=campaign_flags;const auto saved_score=campaign_score;enter_level(1);
                    if(shared_world->score!=saved_score||shared_world->progress.flags[2]!=saved_flags[2])throw std::logic_error("Smoke reentry lost campaign progress");
                    std::ofstream report(std::filesystem::path(smoke_path)/"world-map-loop.json");
                    report<<"{\"map_to_level_to_map\":true,\"earned_selector\":2,\"cursor_retained\":true,\"upper_route_connected\":true,\"score_preserved\":true,\"reentry_preserved\":true,\"fixture_driven\":true}\n";
                    for(unsigned port=1;port<=2;++port){
                        enter_level(1);auto& scene=*shared_world;
                        if(port==2){
                            const auto& rolo_actor=scene.pool.resolve(scene.movement.controlled);
                            const auto bunny=rolo::allocate_actor_chain(scene.pool,{0x13f54,rolo_actor.longword(12),rolo_actor.longword(16),0,0,0},scene);
                            if(!bunny.success)throw std::logic_error("Transport bunny fixture allocation");
                            scene.list();scene.animate();scene.invoke_actor_callback(bunny.head,0xa8bc);
                            if(!scene.choose_companion(2)||scene.movement.controlled_type!=20)throw std::logic_error("Transport bunny selection");
                        }
                        auto& controlled=scene.pool.resolve(scene.movement.controlled);
                        controlled.longword(12,std::uint32_t(port==1?88:600)<<16);
                        controlled.longword(16,std::uint32_t(port==1?488:1304)<<16);
                        controlled.longword(58,0);controlled.longword(62,0);controlled.byte(121,0);controlled.byte(122,0);
                        rolo::initialize_camera(scene.camera,scene.camera_input());scene.stream(scene.camera.foreground_x,scene.camera.foreground_y);
                        camera=scene.camera;map_x=camera.foreground_x;map_y=camera.foreground_y;
                        capture_scene(port==1?"transporter-1-before.bmp":"transporter-2-before.bmp");
                        advance_player({});if(!transport_host->busy())throw std::logic_error("Transport contact did not activate");
                        const auto waiting_x=controlled.word(12),waiting_y=controlled.word(16);
                        for(unsigned n=0;n<7;++n){advance_player({});if(!transport_host->busy()||controlled.word(12)!=waiting_x||controlled.word(16)!=waiting_y)throw std::logic_error("Transport fade wait moved actor");}
                        advance_player({});
                        if(transport_host->busy()||transport_host->transports!=1||controlled.word(12)!=(port==1?296:136)||controlled.word(16)!=(port==1?1296:528))throw std::logic_error("Transport destination differs");
                        capture_scene(port==1?"transporter-1-black.bmp":"transporter-2-black.bmp");
                        for(unsigned n=0;n<8;++n)advance_player({});
                        if(scene.palette!=rolo::level1_terrain_data::palette_words)throw std::logic_error("Transport fade-in palette differs");
                        capture_scene(port==1?"transporter-1-restored.bmp":"transporter-2-restored.bmp");
                        std::fprintf(stderr,"Transport restored: type%u XY%u,%u camera%u,%u graphics%08x flags%u group%04x\n",scene.movement.controlled_type,controlled.word(12),controlled.word(16),camera.foreground_x,camera.foreground_y,controlled.longword(28),controlled.byte(125),controlled.word(0));
                    }
                    std::ofstream transport_report(std::filesystem::path(smoke_path)/"transporters.json");
                    transport_report<<"{\"rolo_first_port\":true,\"controlled_bunny_return_port\":true,\"eight_eligible_fade_ticks\":true,\"original_destinations\":true,\"fixture_driven\":true,\"full_original_reference_verified\":false}\n";
                }
                running=false;
            }
            if(!smoke_path.empty() && running && player_preview && start_level!=2) {
                std::filesystem::create_directories(smoke_path);
                std::ofstream jump_check(std::filesystem::path(smoke_path)/"jump-checks.csv");
                jump_check<<"input,rise_fixed,rise_pixels\n";
                for(bool held:{false,true}) {
                    player=rolo::PlayerState{};
                    for(int tick=0;tick<10;++tick)advance_player({});
                    SDL_Event input_event;
                    while(SDL_PollEvent(&input_event))update_jump_key(input_event);
                    input_event={};input_event.type=SDL_EVENT_KEY_DOWN;
                    input_event.key.scancode=SDL_SCANCODE_SPACE;
                    if(!SDL_PushEvent(&input_event))result=1;
                    for(int tick=0;tick<100;++tick) {
                        if(!held&&tick==1) {
                            input_event={};input_event.type=SDL_EVENT_KEY_UP;input_event.key.scancode=SDL_SCANCODE_SPACE;
                            if(!SDL_PushEvent(&input_event))result=1;
                        }
                        while(SDL_PollEvent(&input_event))update_jump_key(input_event);
                        advance_player({false,false,false,jump_key_down});
                        if(tick==(held?31:15)) {
                            draw();
                            std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                            const auto filename=(std::filesystem::path(smoke_path)/(held?"jump-held.bmp":"jump-tap.bmp")).string();
                            if(!capture||!SDL_SaveBMP(capture.get(),filename.c_str()))result=1;
                        }
                    }
                    jump_check<<(held?"held":"tap")<<','<<jump_rise<<','<<jump_rise/65536.0<<'\n';
                    if(jump_rise!=(held?6328832:3334144))result=1;
                }
                jump_key_down=false;
                player=rolo::PlayerState{};
                std::ofstream trace(std::filesystem::path(smoke_path)/"player.csv");
                trace<<"tick,x,y,speed_x,speed_y,direction_x,direction_y,grounded,selector,camera_y,screen_anchor_y,camera_x,camera_left,camera_right,camera_top,camera_bottom,background_x,background_y,body_frame,head_frame,facing_left\n";
                for(unsigned tick=0;tick<350&&running;++tick) {
                    advance_player({false,tick>=20&&tick<240,tick>=100&&tick<230,(tick>=60&&tick<66)||(tick>=170&&tick<185)});
                    draw();
                    trace<<player.tick<<','<<player.x<<','<<player.y<<','<<player.speed_x<<','<<player.speed_y<<','<<static_cast<int>(player.direction_x)<<','<<static_cast<int>(player.direction_y)<<','<<player.grounded<<','<<player.selector<<','<<map_y<<','<<player.pixel_y()-map_y<<','<<map_x<<','<<camera.left<<','<<camera.right<<','<<camera.top<<','<<camera.bottom<<','<<camera.background_x<<','<<camera.background_y<<','<<player.body.current<<','<<player.head.current<<','<<player.facing_left<<'\n';
                    if(player.tick==20||player.tick==65||player.tick==120||player.tick==200||player.tick==300) {
                        std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        const auto filename=(std::filesystem::path(smoke_path)/("player-"+std::to_string(player.tick)+".bmp")).string();
                        if(!capture||!SDL_SaveBMP(capture.get(),filename.c_str()))result=1;
                    }
                    SDL_RenderPresent(renderer.get());
                }
                running=false;
            }
            if(!smoke_path.empty() && running && map_preview) {
                std::filesystem::create_directories(smoke_path);draw();
                std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                const auto filename=(std::filesystem::path(smoke_path)/"map.bmp").string();
                if(!capture||!SDL_SaveBMP(capture.get(),filename.c_str())) result=1;
                if(map_background) {
                    map_x=std::min(900.0f,static_cast<float>(textures[0].width)-320);map_y=672;
                    draw();
                    std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> pan(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                    const auto pan_filename=(std::filesystem::path(smoke_path)/"map-pan.bmp").string();
                    if(!pan||!SDL_SaveBMP(pan.get(),pan_filename.c_str())) result=1;
                }
                SDL_RenderPresent(renderer.get());running=false;
            }
            if(!smoke_path.empty() && running && !static_preview&&!handoff_test) {
                std::filesystem::create_directories(smoke_path);
                constexpr std::array<unsigned,10> captures{1,72,150,300,410,500,700,1200,1450,1600};std::size_t capture=0;
                while(opening->ticks<1600 && running) {
                    advance();draw();
                    if(capture<captures.size() && opening->ticks==captures[capture]) {
                        std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> image(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                        const auto filename=(std::filesystem::path(smoke_path)/("opening-"+std::to_string(opening->ticks)+".bmp")).string();
                        if(!image||!SDL_SaveBMP(image.get(),filename.c_str())) {result=1;running=false;}
                        ++capture;
                    }
                    SDL_RenderPresent(renderer.get());
                }
                std::printf("SDL entrance smoke test: %u updates, %zu captures, status %d\n",opening->ticks,capture,result);
                running=false;
            }
            auto capture_issue=[&](const std::filesystem::path& folder){
                try{
                    rolo::IssueCaptureContext c{};c.map=world_map_scene;c.paused=paused;c.menu=menu_host&&menu_host->active;c.widescreen=widescreen;c.debug_flight=host_debug_flight;
                    c.camera_x=camera.foreground_x;c.camera_y=camera.foreground_y;
                    if(shared_world){auto&w=*shared_world;const auto&a=w.pool.resolve(w.movement.controlled);c.level=w.progress.selector;c.x=a.word(12);c.y=a.word(16);c.controlled=w.movement.controlled;c.definition=a.longword(4);c.animation=a.word(70);c.bank=w.level_assets.bank;c.actors=w.active.count;c.lives=w.movement.c51d;c.score=w.score;}
                    if(world_map_scene){c.x=world_cursor.x;c.y=world_cursor.y;const auto wc=rolo::world_camera_integer(world_camera_state);c.camera_x=wc.x;c.camera_y=wc.y;}
                    const auto saved=rolo::save_issue_capture(renderer.get(),folder,c);timing.event("F4_ISSUE_SAVED");std::printf("Issue report: %s\n",saved.string().c_str());presentation.notify_capture(true);return true;
                }catch(const std::exception&e){std::fprintf(stderr,"F4 issue capture failed: %s\n",e.what());presentation.notify_capture(false);return false;}
            };
            if(!smoke_path.empty()){
                std::filesystem::create_directories(smoke_path);
                presentation.options(2,host_fullscreen,widescreen,vsync_enabled,host_renderer);
                std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/"options.bmp").string().c_str()))result=1;
                // Use a separate preview state; smoke tests never alter earned unlocks.
                rolo::LocalAchievements preview;preview.observe(50,0);presentation.achievements(0,preview);
                capture.reset(SDL_RenderReadPixels(renderer.get(),nullptr));
                if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/"achievements.bmp").string().c_str()))result=1;
                presentation.achievements(8,preview);capture.reset(SDL_RenderReadPixels(renderer.get(),nullptr));if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/"achievements-page9.bmp").string().c_str()))result=1;
                draw();const auto popup_time=SDL_GetTicks();presentation.notifications.enqueue(1u,popup_time);presentation.draw_unlock(popup_time+300);
                capture.reset(SDL_RenderReadPixels(renderer.get(),nullptr));
                if(!capture||!SDL_SaveBMP(capture.get(),(std::filesystem::path(smoke_path)/"achievement-popup.bmp").string().c_str()))result=1;
                presentation.notifications={};
                if(enemy_preview&&shared_world){const auto original_flags=shared_world->progress.flags;const auto original_scene=shared_world->boss_scene_f283;
                    for(bool full:{false,true}){shared_world->progress.flags.fill(full?2:0);shared_world->boss_scene_f283=255;return_to_world_map();
                        for(unsigned i=0;i<700;++i)ending->step();const auto expected=rolo::achievement_bit(full?22:23);if(ending->take_events()!=expected)throw std::runtime_error("Ending smoke award branch");
                        for(unsigned i=0;i<450;++i)ending->step();draw();capture.reset(SDL_RenderReadPixels(renderer.get(),nullptr));const auto file=std::filesystem::path(smoke_path)/(full?"ending-good.bmp":"ending-bad.bmp");if(!capture||!SDL_SaveBMP(capture.get(),file.string().c_str()))result=1;
                        for(unsigned i=0;i<4000&&ending->phase!=rolo::EndingSequence::Phase::Title;++i)ending->step(true);if(ending->phase!=rolo::EndingSequence::Phase::Title)throw std::runtime_error("Ending title transition");
                    }ending.reset();shared_world->progress.flags=original_flags;shared_world->boss_scene_f283=original_scene;
                }
                draw();if(!capture_issue(std::filesystem::path(smoke_path)/"issue-reports"))result=1;
            }
            if(handoff_test&&!enemy_preview&&opening){
                draw();std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> ea(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                if(!ea||!SDL_SaveBMP(ea.get(),(std::filesystem::path(smoke_path)/"handoff-ea.bmp").string().c_str()))result=1;
                opening->phase=rolo::OpeningSequence::Phase::Title;
                SDL_SetWindowPosition(window.get(),137,89);SDL_SetWindowSize(window.get(),1100,760);SDL_SyncWindow(window.get());
                draw();std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> title(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                if(!title||!SDL_SaveBMP(title.get(),(std::filesystem::path(smoke_path)/"handoff-title.bmp").string().c_str()))result=1;
                SDL_Event start{};start.type=SDL_EVENT_KEY_DOWN;start.key.key=SDLK_RETURN;start.key.down=true;SDL_PushEvent(&start);
            }
            while(running) {
                timing.begin(SDL_GetTicksNS());
                SDL_Event event;
                while(SDL_PollEvent(&event)) {
                    if(event.type==SDL_EVENT_KEY_DOWN&&!event.key.repeat&&event.key.key==SDLK_F4){draw();capture_issue(std::filesystem::absolute(argv[0]).parent_path()/"issue-reports");previous=SDL_GetTicksNS();next_present=previous;continue;}
                    if(event.type==SDL_EVENT_KEY_DOWN&&!event.key.repeat&&event.key.key==SDLK_F2){host_debug_flight=!host_debug_flight;continue;}
                    bool options_clicked=false;
                    if(event.type==SDL_EVENT_MOUSE_BUTTON_DOWN&&event.button.button==SDL_BUTTON_LEFT){int ww=0,hh=0,rw=0,rh=0;SDL_GetWindowSize(window.get(),&ww,&hh);SDL_GetCurrentRenderOutputSize(renderer.get(),&rw,&rh);const SDL_FPoint p{event.button.x*rw/std::max(1,ww),event.button.y*rh/std::max(1,hh)};options_clicked=SDL_PointInRectFloat(&p,&presentation.options_button);}
                    if(options_clicked||(event.type==SDL_EVENT_KEY_DOWN&&!event.key.repeat&&(event.key.key==SDLK_F8||event.key.key==SDLK_F7))){
                        music.pause(true);bool opened=true,reset_confirmation=false,achievement_view=event.type==SDL_EVENT_KEY_DOWN&&event.key.key==SDLK_F7;int selected=0;unsigned achievement_page=0;
                        while(opened&&running){
                            if(achievement_view){presentation.achievements(achievement_page,achievements);if(reset_confirmation)presentation.confirm_achievement_reset();}else presentation.options(selected,host_fullscreen,widescreen,vsync_enabled,host_renderer);SDL_RenderPresent(renderer.get());
                            SDL_Event option_event;if(!SDL_WaitEventTimeout(&option_event,16))continue;
                            gamepad.event(option_event);
                            if(option_event.type==SDL_EVENT_QUIT){running=false;break;}
                            if(achievement_view){
                                const auto clicked=[&](const SDL_FRect& button){if(option_event.type!=SDL_EVENT_MOUSE_BUTTON_DOWN||option_event.button.button!=SDL_BUTTON_LEFT)return false;int ww=0,hh=0,rw=0,rh=0;SDL_GetWindowSize(window.get(),&ww,&hh);SDL_GetCurrentRenderOutputSize(renderer.get(),&rw,&rh);const SDL_FPoint p{option_event.button.x*rw/std::max(1,ww),option_event.button.y*rh/std::max(1,hh)};return SDL_PointInRectFloat(&p,&button);};
                                const bool keydown=option_event.type==SDL_EVENT_KEY_DOWN&&!option_event.key.repeat;
                                if(reset_confirmation){
                                    if((keydown&&option_event.key.key==SDLK_RETURN)||clicked(presentation.confirm_reset_button)){
                                        auto cleared=achievements;cleared.reset();
                                        if(cleared.save(achievement_file)){achievements=cleared;presentation.notifications={};}
                                        else SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR,"Achievements","Could not save the reset. Your achievements have been kept.",window.get());
                                        reset_confirmation=false;
                                    }else if((keydown&&(option_event.key.key==SDLK_ESCAPE||option_event.key.key==SDLK_BACKSPACE))||clicked(presentation.cancel_reset_button))reset_confirmation=false;
                                    continue;
                                }
                                if((keydown&&option_event.key.key==SDLK_R)||clicked(presentation.reset_achievements_button)){reset_confirmation=true;continue;}
                                if(option_event.type==SDL_EVENT_KEY_DOWN&&!option_event.key.repeat){const auto k=option_event.key.key;if(k==SDLK_ESCAPE||k==SDLK_BACKSPACE)achievement_view=false;if(k==SDLK_F8)opened=false;if(k==SDLK_RIGHT||k==SDLK_PAGEDOWN||k==SDLK_DOWN)achievement_page=(achievement_page+1)%rolo::achievement_pages;if(k==SDLK_LEFT||k==SDLK_PAGEUP||k==SDLK_UP)achievement_page=(achievement_page+rolo::achievement_pages-1)%rolo::achievement_pages;}
                                if(option_event.type==SDL_EVENT_MOUSE_WHEEL){if(option_event.wheel.y<0)achievement_page=(achievement_page+1)%rolo::achievement_pages;else if(option_event.wheel.y>0)achievement_page=(achievement_page+rolo::achievement_pages-1)%rolo::achievement_pages;}
                                continue;
                            }
                            SDL_Keycode key=0;
                            if(option_event.type==SDL_EVENT_MOUSE_BUTTON_DOWN&&option_event.button.button==SDL_BUTTON_LEFT){
                                int ww=0,hh=0,rw=0,rh=0;SDL_GetWindowSize(window.get(),&ww,&hh);SDL_GetCurrentRenderOutputSize(renderer.get(),&rw,&rh);
                                const float scale=std::max(0.5f,std::floor(std::min(rw/440.0f,rh/320.0f))),x=(rw/scale-400)/2,y=(rh/scale-290)/2;
                                const float mx=option_event.button.x*rw/std::max(1,ww)/scale,my=option_event.button.y*rh/std::max(1,hh)/scale;
                                if(mx>=x+16&&mx<x+384&&my>=y+54&&my<y+234){selected=int((my-y-54)/30);key=SDLK_RETURN;}
                            }else if(option_event.type==SDL_EVENT_KEY_DOWN&&!option_event.key.repeat)key=option_event.key.key;
                            if(!key)continue;
                            if(key==SDLK_ESCAPE||key==SDLK_F8){opened=false;continue;}
                            if(key==SDLK_UP)selected=(selected+5)%6;
                            if(key==SDLK_DOWN)selected=(selected+1)%6;
                            if(key==SDLK_RETURN||key==SDLK_LEFT||key==SDLK_RIGHT){
                                if(selected==0){host_fullscreen=!host_fullscreen;SDL_SetWindowFullscreen(window.get(),host_fullscreen);configure_vsync();}
                                if(selected==1)widescreen=!widescreen;
                                if(selected==2){vsync_requested=!vsync_requested;configure_vsync();}
                                if(selected==3){const char* names[]{"auto","direct3d11","direct3d12","vulkan"};int index=0;while(index<3&&host_renderer!=names[index])++index;host_renderer=names[(index+(key==SDLK_LEFT?3:1))%4];std::ofstream output(rolo::renderer_settings_path());output<<host_renderer<<'\n';}
                                if(selected==4)achievement_view=true;
                                if(selected==5)opened=false;
                            }
                        }
                        jump_key_down=false;previous=next_present=SDL_GetTicksNS();accumulator=0;continue;
                    }
                    gamepad.event(event);
                    update_jump_key(event);
                    if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST)timing.event("FOCUS_LOST");
                    if(event.type==SDL_EVENT_WINDOW_FOCUS_GAINED)timing.event("FOCUS_GAINED");
                    if(event.type==SDL_EVENT_WINDOW_MINIMIZED)timing.event("WINDOW_MINIMIZED");
                    if(event.type==SDL_EVENT_WINDOW_RESTORED)timing.event("WINDOW_RESTORED");
                    if(event.type==SDL_EVENT_WINDOW_RESTORED||event.type==SDL_EVENT_WINDOW_DISPLAY_CHANGED||event.type==SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED)configure_vsync();
                    if(event.type==SDL_EVENT_QUIT) running=false;
                    if(event.type==SDL_EVENT_KEY_DOWN && !event.key.repeat) {
                        if(ending&&event.key.key!=SDLK_F11&&event.key.key!=SDLK_F4)continue;
                        if(event.key.key==SDLK_F11){host_fullscreen=!(SDL_GetWindowFlags(window.get())&SDL_WINDOW_FULLSCREEN);SDL_SetWindowFullscreen(window.get(),host_fullscreen);configure_vsync();next_present=SDL_GetTicksNS();continue;}
                        if(event.key.key==SDLK_F10){widescreen=!widescreen;continue;}
                        if(extracted_scene){
                            if(event.key.key==SDLK_ESCAPE||event.key.key==SDLK_BACKSPACE||event.key.key==SDLK_F6){extracted_scene=false;accumulator=0;SDL_SetWindowTitle(window.get(),world_map_scene?"Rolo native demo - jigsaw map | F6 choose level":"Rolo native demo - gameplay partial | F6 choose level");continue;}
                            if(event.key.key==SDLK_PAGEUP)open_extracted((extracted_selector+79)%80,extracted_background);
                            if(event.key.key==SDLK_PAGEDOWN)open_extracted((extracted_selector+1)%80,extracted_background);
                            if(event.key.key==SDLK_B)open_extracted(extracted_selector,!extracted_background);
                            if(event.key.key==SDLK_RETURN&&rolo::native_level_connected(static_cast<std::uint16_t>(extracted_selector))){extracted_scene=false;enter_level(static_cast<std::uint16_t>(extracted_selector));}
                            if(event.key.key!=SDLK_F9)continue;
                        }
                        if(enemy_preview&&event.key.key==SDLK_F6){
                            if(!world_map_scene){campaign_flags=shared_world->progress.flags;campaign_score=shared_world->score;campaign_lives=shared_world->movement.c51d;campaign_awards=shared_world->awards;}
                            open_extracted(world_map_scene?rolo::world_map_selector_at(world_cursor.x,world_cursor.y):shared_world->progress.selector);continue;
                        }
                        if(enemy_preview&&event.key.key==SDLK_F5){
                            if(world_map_scene)save_progress();
                            else SDL_SetWindowTitle(window.get(),"Rolo native demo - return to jigsaw map to save (F5)");
                            continue;
                        }
                        if(enemy_preview&&event.key.key==SDLK_F9){load_progress();continue;}
                        if(enemy_preview&&!world_map_scene&&shared_world->game_over_requested){
                            if(event.key.key==SDLK_ESCAPE)running=false;
                            if(event.key.key==SDLK_RETURN){
                                new_campaign();
                            }
                            continue;
                        }
                        if(!map_preview&&event.key.key==SDLK_RETURN){
                            if(opening&&!opening->press_start()){
                                music.play(2,true);accumulator=0;
                                continue;
                            }
                            start_map="native-campaign";
                            running=false;
                            continue;
                        }
                        if(world_map_scene){
                            if(event.key.key==SDLK_SPACE)world_button_latch|=16;
                            if(event.key.key==SDLK_Z)world_button_latch|=32;
                            if(event.key.key==SDLK_X)world_button_latch|=64;
                            if(event.key.key==SDLK_RETURN)world_button_latch|=128;
                            if(event.key.key==SDLK_RETURN||event.key.key==SDLK_SPACE)continue;
                        }
                        if(enemy_preview&&!world_map_scene&&transport_host&&transport_host->busy()&&
                           (event.key.key==SDLK_RETURN||event.key.key==SDLK_P||event.key.key==SDLK_R))continue;
                        if(enemy_preview&&!world_map_scene&&event.key.key==SDLK_RETURN&&(!menu_host||!menu_host->active)){
                            menu_host=std::make_unique<rolo::Level1MenuWorld>(*shared_world);menu_host->begin();accumulator=0;continue;
                        }
                        if(event.key.key==SDLK_F3&&enemy_preview){
                            const auto folder=std::filesystem::absolute(argv[0]).parent_path()/"demo-feedback";
                            std::filesystem::create_directories(folder);
                            std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> capture(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
                            if(capture)SDL_SaveBMP(capture.get(),(folder/"frame.bmp").string().c_str());
                            std::ofstream state_file(folder/"state.csv");
                            const auto& body=shared_world->pool.resolve(shared_world->movement.controlled);
                            state_file<<"frame,camera_x,camera_y,player_x,player_y,score,key,piece\n"<<shared_world->frame<<','<<camera.foreground_x<<','<<camera.foreground_y<<','<<body.word(12)<<','<<body.word(16)<<','<<shared_world->score<<','<<unsigned(shared_world->progress.key_c550)<<','<<unsigned(shared_world->progress.piece_c551)<<'\n';
                        }
                        if(event.key.key==SDLK_ESCAPE) running=false;
                        if(event.key.key==SDLK_SPACE && !player_preview) {paused=!paused;accumulator=0;}
                        if(event.key.key==SDLK_P && player_preview) {paused=!paused;accumulator=0;}
                        if(event.key.key==SDLK_R) {state=rolo::EntranceState{};if(opening){opening->reset();music.stop();}paused=false;accumulator=0;}
                        if(event.key.key==SDLK_R && map_preview) {map_x=0;map_y=std::min(480.0f,static_cast<float>(textures[0].height)-160.0f);}
                        if(event.key.key==SDLK_R && player_preview) {player=rolo::PlayerState{};if(enemy_preview){enter_level(shared_world->progress.selector);}advance_player({});}
                        if(event.key.key==SDLK_RIGHT && paused && !static_preview) advance();
                    }
                }
                music.pause(paused&&!(enemy_preview&&shared_world&&shared_world->game_over_requested));
                if(smoke_path.empty()&&enemy_preview&&shared_world&&!host_debug_flight){
                    const auto previous_unlocks=achievements.unlocked;
                    achievements.observe(world_map_scene?campaign_lives:shared_world->movement.c51d,world_map_scene?campaign_score:shared_world->score);
                    presentation.notify_unlocks(achievements.unlocked&~previous_unlocks);
                    if(achievements.dirty&&!achievements.save(achievement_file))timing.event("ACHIEVEMENT_SAVE_FAILED");
                }
                timing.mark(rolo::FrameTimingLog::Simulation,SDL_GetTicksNS());
                const auto now=SDL_GetTicksNS();const double elapsed=static_cast<double>(now-previous)/1e9;previous=now;
                if(map_preview && !player_preview && !textures.empty()) {
                    const auto keys=gamepad.keys();
                    const float distance=static_cast<float>(std::min(elapsed,0.1)*240.0);
                    map_x=std::clamp(map_x+distance*(static_cast<int>(keys[SDL_SCANCODE_RIGHT])-static_cast<int>(keys[SDL_SCANCODE_LEFT])),0.0f,static_cast<float>(textures[0].width)-320);
                    map_y=std::clamp(map_y+distance*(static_cast<int>(keys[SDL_SCANCODE_DOWN])-static_cast<int>(keys[SDL_SCANCODE_UP])),0.0f,static_cast<float>(textures[0].height)-160);
                }
                if(ending){
                    accumulator+=elapsed;while(ending&&accumulator>=1.0/fps){timing.step();const auto keys=gamepad.keys();const bool held=keys[SDL_SCANCODE_RETURN]||keys[SDL_SCANCODE_SPACE];const bool fresh=held&&!ending_start_held;ending_start_held=held;
                        if(ending->phase==rolo::EndingSequence::Phase::Title&&fresh){ending.reset();new_campaign();break;}
                        ending->step(fresh);if(ending->sound<91){if(ending->sound==3||ending->sound==2)music.play(ending->sound,true);else music.effect(ending->sound);ending->sound=0xffff;}
                        if(smoke_path.empty()){const auto before=achievements.unlocked;achievements.award_events(ending->take_events());presentation.notify_unlocks(achievements.unlocked&~before);if(achievements.dirty&&!achievements.save(achievement_file))timing.event("ACHIEVEMENT_SAVE_FAILED");}
                        accumulator-=1.0/fps;}
                }else if(extracted_scene){
                    const auto keys=gamepad.keys();const auto distance=static_cast<float>(std::min(elapsed,0.1)*240);
                    extracted_x=std::clamp(extracted_x+distance*(int(keys[SDL_SCANCODE_RIGHT])-int(keys[SDL_SCANCODE_LEFT])),0.0f,std::max(0.0f,extracted_width-320));
                    extracted_y=std::clamp(extracted_y+distance*(int(keys[SDL_SCANCODE_DOWN])-int(keys[SDL_SCANCODE_UP])),0.0f,std::max(0.0f,extracted_height-224));
                }else if(enemy_preview&&world_map_scene){
                    accumulator+=elapsed;while(accumulator>=1.0/fps){
                        timing.step();
                        const auto keys=gamepad.keys();
                        rolo::map_player_input(world_buttons,static_cast<std::uint8_t>(world_button_latch|(keys[SDL_SCANCODE_UP]?1:0)|(keys[SDL_SCANCODE_DOWN]?2:0)|(keys[SDL_SCANCODE_LEFT]?4:0)|(keys[SDL_SCANCODE_RIGHT]?8:0)|(keys[SDL_SCANCODE_SPACE]?16:0)|(keys[SDL_SCANCODE_Z]?32:0)|(keys[SDL_SCANCODE_X]?64:0)|(keys[SDL_SCANCODE_RETURN]?128:0)));
                        world_button_latch=0;
                        rolo::update_world_route(world_actors->actor(),world_route_state,{world_buttons.mapped[0],world_buttons.mapped[1],world_buttons.mapped[2],world_buttons.mapped[3]},*world_routes);
                        world_actors->update_bunny(world_route_state.pause,{world_buttons.mapped[0],world_buttons.mapped[1],world_buttons.mapped[2],world_buttons.mapped[3]});
                        world_cursor.x=world_route_state.snapshot_x;world_cursor.y=world_route_state.snapshot_y;
                        auto camera_target=world_cursor;if(world_route_state.pause){camera_target.x=world_actors->bunny().word(12);camera_target.y=world_actors->bunny().word(16);}
                        rolo::update_world_camera(world_camera_state,camera_target,1280,1280);
                        world_actors->step();const auto position=rolo::world_camera_integer(world_camera_state);
                        rolo::update_world_palette(world_palette_cycle,world_palette);++world_animation_tick;
                        world_routes->stream(position.x,position.y);
                        world_map_dirty=true;accumulator-=1.0/fps;
                        if(rolo::finish_world_input(world_route_state,world_admission,world_buttons,[&]{return rolo::world_map_selector_at(world_cursor.x,world_cursor.y);})){ 
                            if(rolo::native_level_connected(world_admission.current_f2f6)){enter_level(world_admission.current_f2f6);break;}
                            world_level_pending=true;break; // Art browsing stays on F6; Space never enters a slideshow.
                        }
                    }
                }else if(enemy_preview&&menu_host&&menu_host->active){
                    accumulator+=elapsed;const auto keys=gamepad.keys();
                    const auto pressed=static_cast<std::uint8_t>((keys[SDL_SCANCODE_UP]?1:0)|(keys[SDL_SCANCODE_DOWN]?2:0)|(keys[SDL_SCANCODE_LEFT]?4:0)|(keys[SDL_SCANCODE_RIGHT]?8:0)|(keys[SDL_SCANCODE_SPACE]?16:0)|(keys[SDL_SCANCODE_Z]?32:0)|(keys[SDL_SCANCODE_X]?64:0)|(keys[SDL_SCANCODE_RETURN]?128:0));
                    while(accumulator>=1.0/fps&&menu_host->active){timing.step();menu_host->step(pressed);if(shared_world->sound<91)music.effect(shared_world->sound);shared_world->sound=0xff00;accumulator-=1.0/fps;}
                    if(menu_host->return_map&&shared_world->boss_scene_f283){menu_host->return_map=false;return_to_world_map();}
                    else if(menu_host->return_map){campaign_flags=shared_world->progress.flags;campaign_score=shared_world->score;campaign_lives=shared_world->movement.c51d;campaign_awards=shared_world->awards;world_map_scene=true;world_map_dirty=true;initialize_world_routes();music.play(16,true);menu_host->return_map=false;}
                    camera=shared_world->camera;map_x=camera.foreground_x;map_y=camera.foreground_y;
                }else if(player_preview && !paused && !world_map_scene) {
                    accumulator+=elapsed;
                    const auto keys=gamepad.keys();
                    while(accumulator>=1.0/fps && !paused&&running) {advance_player({keys[SDL_SCANCODE_LEFT],keys[SDL_SCANCODE_RIGHT],keys[SDL_SCANCODE_X],jump_key_down||bool(gamepad.buttons()&16)});accumulator-=1.0/fps;}
                }
                if(!paused && !static_preview) {
                    accumulator+=elapsed;
                    // Keep every simulation update; wall-clock delays only affect presentation.
                    while(accumulator>=1.0/fps && !paused && running) {advance();accumulator-=1.0/fps;}
                }
                timing.mark(rolo::FrameTimingLog::Draw,SDL_GetTicksNS());
                draw();
                timing.mark(rolo::FrameTimingLog::Present,SDL_GetTicksNS());
                if(presentation.take_unlock_start())music.unlock_chime();
                SDL_RenderPresent(renderer.get());
                timing.mark(rolo::FrameTimingLog::Wait,SDL_GetTicksNS());
                if(vsync_enabled){next_present=SDL_GetTicksNS();}
                else {
                    // Use one presentation clock: VSync, or the existing fixed-rate fallback.
                    const auto period=1000000000ull/static_cast<unsigned>(fps);next_present+=period;
                    const auto now_present=SDL_GetTicksNS();
                    if(next_present>now_present)SDL_DelayPrecise(next_present-now_present);
                    else if(now_present-next_present>period)next_present=now_present;
                }
                rolo::FrameTimingLog::Context diagnostic_context{};
                diagnostic_context.textures=static_cast<unsigned>(textures.size()+player_textures.size());
                diagnostic_context.map=world_map_scene;diagnostic_context.paused=paused;
                diagnostic_context.menu=menu_host&&menu_host->active;
                if(shared_world){diagnostic_context.level=shared_world->progress.selector;diagnostic_context.actors=shared_world->active.count;diagnostic_context.alloc_failures=shared_world->allocation_failures;const auto&a=shared_world->pool.resolve(shared_world->movement.controlled);diagnostic_context.x=a.word(12);diagnostic_context.y=a.word(16);}
                timing.set_context(diagnostic_context);timing.end(SDL_GetTicksNS());
            }
        }
    }
    if(result) std::fprintf(stderr,"Preview failed: %s\n",SDL_GetError());
    return result;
}
int main(int argc,char** argv){
    bool smoke=false;
    for(int i=1;i<argc;++i)if(std::string(argv[i])=="--smoke-test")smoke=true;
    try {
    const char* base_path=SDL_GetBasePath();
    if(!base_path)throw std::runtime_error("Cannot determine game directory");
    const auto app_root=std::filesystem::path(base_path);
    bool explicit_resource_root=false;
    for(int i=1;i<argc;++i){const std::string arg=argv[i];if(arg=="--resource-root"&&i+1<argc){host_data_root=std::filesystem::absolute(argv[++i]);explicit_resource_root=true;}}
    if(!explicit_resource_root)host_data_root=rolo::saved_resource_root(app_root);
    try {
        rolo::resources::initialize(host_data_root);
        rolo::check_external_asset_files(host_data_root);
    } catch(const std::exception&) {
        if(explicit_resource_root)throw;
        if(!rolo::prepare_external_resources(app_root,host_data_root))return 0;
        rolo::resources::initialize(host_data_root);
        rolo::check_external_asset_files(host_data_root);
    }
    host_renderer=rolo::load_renderer_choice();
    bool handoff_test=false;std::string smoke_folder,cadence="60";
    for(int i=1;i<argc;++i){const std::string arg=argv[i];if(arg=="--smoke-test"&&i+1<argc){smoke_folder=argv[i+1];}if(arg=="--handoff-test")handoff_test=true;if(arg=="--fps"&&i+1<argc)cadence=argv[i+1];}
    if(handoff_test&&!smoke)return 2;
    std::string start_map;
    HostDisplay display;
    const auto result=run_preview(argc,argv,start_map,display);
    if(result||start_map.empty())return result;
    // Scene assets change; the user's display stays on the same monitor.
    const auto window_id=SDL_GetWindowID(display.window.get());auto* renderer=display.renderer.get();
    int x=0,y=0,width=0,height=0;SDL_GetWindowPosition(display.window.get(),&x,&y);SDL_GetWindowSize(display.window.get(),&width,&height);
    const auto monitor=SDL_GetDisplayForWindow(display.window.get());const auto flags=SDL_GetWindowFlags(display.window.get());
    std::vector<std::string> args{argv[0]};
    if(start_map=="native-campaign")args.push_back("--campaign");
    else {args.push_back("--enemy-preview");args.push_back(start_map);}
    args.push_back("--fps");args.push_back(cadence);
    if(handoff_test){args.push_back("--smoke-test");args.push_back(smoke_folder);args.push_back("--handoff-test");}
    std::vector<char*> game_args;for(auto&arg:args)game_args.push_back(arg.data());
    std::string unused;
    const auto game_result=run_preview(static_cast<int>(game_args.size()),game_args.data(),unused,display);
    if(handoff_test){
        int xx=0,yy=0,ww=0,hh=0;SDL_GetWindowPosition(display.window.get(),&xx,&yy);SDL_GetWindowSize(display.window.get(),&ww,&hh);
        const bool same=window_id==SDL_GetWindowID(display.window.get())&&renderer==display.renderer.get()&&x==xx&&y==yy&&width==ww&&height==hh&&monitor==SDL_GetDisplayForWindow(display.window.get())&&((flags^SDL_GetWindowFlags(display.window.get()))&SDL_WINDOW_FULLSCREEN)==0;
        std::ofstream report(std::filesystem::path(smoke_folder)/"handoff-result.json");report<<"{\"same_window_renderer_monitor_geometry\":"<<(same?"true":"false")<<",\"window_id\":"<<window_id<<",\"x\":"<<xx<<",\"y\":"<<yy<<",\"width\":"<<ww<<",\"height\":"<<hh<<",\"map_status\":"<<game_result<<"}\n";
        if(!same)return 1;
    }
    return game_result;
    } catch(const std::exception& error) {
        std::fprintf(stderr,"Native preview error: %s\n",error.what());
        if(!smoke)SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR,"Rolo could not start",error.what(),nullptr);
        SDL_Quit();return 1;
    }
}











