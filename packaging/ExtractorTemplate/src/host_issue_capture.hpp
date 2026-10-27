#pragma once
#include <SDL3/SDL.h>
#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <memory>
#include <sstream>
#include <stdexcept>
namespace rolo {
struct IssueCaptureContext {
 unsigned level{},x{},y{},camera_x{},camera_y{},controlled{},definition{},animation{},bank{},actors{},lives{},score{};
 bool map{},paused{},menu{},widescreen{},debug_flight{};
};
// Capture the completed game render before Present; never read the desktop.
inline std::filesystem::path save_issue_capture(SDL_Renderer* renderer,const std::filesystem::path& root,const IssueCaptureContext& c){
 const auto now=std::chrono::system_clock::now();const auto seconds=std::chrono::system_clock::to_time_t(now);std::tm utc{};gmtime_s(&utc,&seconds);
 std::ostringstream stamp;stamp<<std::put_time(&utc,"%Y-%m-%dT%H-%M-%SZ");
 std::filesystem::create_directories(root);std::filesystem::path folder;
 for(unsigned n=1;;++n){folder=root/("issue-"+stamp.str()+"-"+std::to_string(n));if(std::filesystem::create_directory(folder))break;}
 try{
  std::unique_ptr<SDL_Surface,decltype(&SDL_DestroySurface)> image(SDL_RenderReadPixels(renderer,nullptr),SDL_DestroySurface);
  if(!image||!SDL_SavePNG(image.get(),(folder/"screenshot.png").string().c_str()))throw std::runtime_error(SDL_GetError());
  std::ofstream report(folder/"report.json");report.exceptions(std::ios::failbit|std::ios::badbit);
  report<<"{\n  \"format\": 1,\n  \"captured_utc\": \""<<stamp.str()<<"\",\n  \"build\": \""<<__DATE__<<" "<<__TIME__<<"\",\n";
  report<<"  \"level\": "<<c.level<<", \"x\": "<<c.x<<", \"y\": "<<c.y<<",\n  \"camera_x\": "<<c.camera_x<<", \"camera_y\": "<<c.camera_y<<",\n";
  report<<"  \"controlled_actor\": "<<c.controlled<<", \"definition\": "<<c.definition<<", \"animation_selector\": "<<c.animation<<",\n  \"bank\": "<<c.bank<<", \"actors\": "<<c.actors<<", \"lives\": "<<c.lives<<", \"score\": "<<c.score<<",\n";
  report<<std::boolalpha<<"  \"debug_flight\": "<<c.debug_flight<<",\n  \"world_map\": "<<c.map<<", \"paused\": "<<c.paused<<", \"companion_menu\": "<<c.menu<<", \"widescreen\": "<<c.widescreen<<",\n  \"image_width\": "<<image->w<<", \"image_height\": "<<image->h<<"\n}\n";report.close();
  std::ofstream notes(folder/"notes.txt");notes.exceptions(std::ios::failbit|std::ios::badbit);notes<<"What looks wrong?\n\nWhat happened just before it?\n\nExpected behaviour:\n\n";notes.close();
 }catch(...){std::ofstream failed(folder/"CAPTURE-INCOMPLETE.txt");failed<<"Capture failed. This folder is incomplete.\n";throw;}
 return folder;
}
}

