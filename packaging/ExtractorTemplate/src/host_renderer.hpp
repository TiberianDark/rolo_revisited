#pragma once
#include <SDL3/SDL.h>
#include <filesystem>
#include <fstream>
#include <string>
namespace rolo {
inline bool valid_renderer(const std::string&name){return name=="auto"||name=="direct3d11"||name=="direct3d12"||name=="vulkan";}
inline std::filesystem::path renderer_settings_path(){
 char* raw=SDL_GetPrefPath("NativeRolo","RoloToTheRescue");if(!raw)return {};
 auto path=std::filesystem::u8path(raw)/"graphics.txt";SDL_free(raw);return path;
}
inline std::string load_renderer_choice(){std::ifstream input(renderer_settings_path());std::string name;input>>name;return valid_renderer(name)?name:"auto";}
inline void choose_renderer(SDL_Window*window){
 const SDL_MessageBoxButtonData buttons[]{
  {SDL_MESSAGEBOX_BUTTON_ESCAPEKEY_DEFAULT,0,"Cancel"},{0,1,"Automatic"},
  {0,2,"Direct3D 11"},{0,3,"Direct3D 12"},{0,4,"Vulkan"}};
 SDL_MessageBoxData dialog{};dialog.flags=SDL_MESSAGEBOX_INFORMATION;dialog.window=window;dialog.title="Graphics renderer";
 dialog.message="Choose a renderer for the next launch. Restart Rolo to apply it.\nVSync remains enabled. Driver support is required.";dialog.numbuttons=5;dialog.buttons=buttons;
 int choice=0;if(!SDL_ShowMessageBox(&dialog,&choice)||choice<=0||choice>4)return;
 const char* names[]{"auto","direct3d11","direct3d12","vulkan"};const auto path=renderer_settings_path();
 if(path.empty())return;
 std::ofstream output(path);output<<names[choice-1]<<'\n';output.close();
 SDL_ShowSimpleMessageBox(output?SDL_MESSAGEBOX_INFORMATION:SDL_MESSAGEBOX_ERROR,"Graphics renderer",output?"Renderer saved. Restart Rolo to apply it.":"Could not save the graphics setting.",window);
}
}
