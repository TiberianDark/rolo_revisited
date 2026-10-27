#pragma once
#include <SDL3/SDL.h>
#include "core/opening_data.hpp"
#include "core/local_achievements.hpp"
#include "core/achievement_notifications.hpp"
#include "core/level1_status_hud_data.hpp"
#include "core/level1_terrain_data.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <memory>
#include <vector>
#include <stdexcept>
#include <string>
namespace rolo {
// Separate host decoration from the unchanged original game framebuffer.
class HostPresentation {
 SDL_Renderer* renderer_;int height_,width_=320;
 std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> game_{nullptr,SDL_DestroyTexture},wood_{nullptr,SDL_DestroyTexture},logo_{nullptr,SDL_DestroyTexture};
 std::unique_ptr<SDL_Texture,decltype(&SDL_DestroyTexture)> mini_{nullptr,SDL_DestroyTexture},grey_mini_{nullptr,SDL_DestroyTexture};
public:
 bool debug_flight{};
 std::string capture_notice;std::uint64_t capture_notice_until{};
 void notify_capture(bool saved){capture_notice=saved?"F4 REPORT SAVED":"F4 SAVE FAILED - SEE LOG";capture_notice_until=SDL_GetTicks()+3000;}
 AchievementNotifications notifications;
 void notify_unlocks(AchievementBits bits){notifications.enqueue(bits,SDL_GetTicks());}
 bool take_unlock_start(){return notifications.take_started();}
 void draw_unlock(std::uint64_t now){
  const int i=notifications.current(now);if(i<0)return;const auto& a=local_achievement_list[unsigned(i)];
  int w=0,h=0;SDL_GetCurrentRenderOutputSize(renderer_,&w,&h);
  const float scale=std::max(0.5f,std::min((w-24)/500.0f,std::max(1.0f,std::floor(h/450.0f))));SDL_SetRenderScale(renderer_,scale,scale);
  const auto age=now-notifications.began;const float motion=age<220?1-float(age)/220:age>4780?float(age-4780)/220:0;
  const float x=(w/scale-500)/2,y=h/scale-88+motion*88;panel({x,y,500,76});
  SDL_FRect icon{x+20,y+14,64,48};SDL_RenderTexture(renderer_,mini_.get(),nullptr,&icon);
  SDL_SetRenderDrawColor(renderer_,162,224,103,255);const auto points=std::to_string(a.points)+"pts";SDL_RenderDebugText(renderer_,x+100,y+34,points.c_str());
  SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,x+164,y+34,a.title);SDL_SetRenderScale(renderer_,1,1);
 }
 SDL_FRect options_button{};
 SDL_FRect reset_achievements_button{},confirm_reset_button{},cancel_reset_button{};
 void confirm_achievement_reset(){
  int w=0,h=0;SDL_GetCurrentRenderOutputSize(renderer_,&w,&h);const float scale=std::max(0.5f,std::floor(std::min(w/480.0f,h/260.0f)));SDL_SetRenderScale(renderer_,scale,scale);
  const float x=(w/scale-440)/2,y=(h/scale-184)/2;panel({x,y,440,184});SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,x+24,y+28,"RESET ALL ACHIEVEMENTS?");SDL_SetRenderDrawColor(renderer_,221,211,183,255);SDL_RenderDebugText(renderer_,x+24,y+57,"Your level progress will be kept.");SDL_RenderDebugText(renderer_,x+24,y+75,"Earn the milestones again to unlock them.");
  confirm_reset_button={x+24,y+112,184,44};cancel_reset_button={x+232,y+112,184,44};panel(confirm_reset_button);panel(cancel_reset_button);SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,x+42,y+130,"Enter: RESET");SDL_RenderDebugText(renderer_,x+250,y+130,"Esc: CANCEL");
  for(auto* r:{&confirm_reset_button,&cancel_reset_button}){r->x*=scale;r->y*=scale;r->w*=scale;r->h*=scale;}SDL_SetRenderScale(renderer_,1,1);
 }
 void panel(SDL_FRect box){
  SDL_SetRenderDrawColor(renderer_,29,20,12,255);SDL_RenderFillRect(renderer_,&box);
  const float b=12;const float sx[]{0,12,308,320},sy[]{0,12,100,112};
  const float dx[]{box.x,box.x+b,box.x+box.w-b,box.x+box.w},dy[]{box.y,box.y+b,box.y+box.h-b,box.y+box.h};
  for(int y=0;y<3;++y)for(int x=0;x<3;++x){if(x==1&&y==1)continue;SDL_FRect s{sx[x],sy[y],sx[x+1]-sx[x],sy[y+1]-sy[y]},d{dx[x],dy[y],dx[x+1]-dx[x],dy[y+1]-dy[y]};SDL_RenderTexture(renderer_,wood_.get(),&s,&d);}
 }
 void options(int selected,bool fullscreen,bool wide,bool vsync,const std::string& backend){
  finish();int w=0,h=0;SDL_GetCurrentRenderOutputSize(renderer_,&w,&h);
  const float scale=std::max(0.5f,std::floor(std::min(w/440.0f,h/320.0f)));SDL_SetRenderScale(renderer_,scale,scale);
  const float x=(w/scale-400)/2,y=(h/scale-290)/2;panel({x,y,400,290});
  SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,x+160,y+24,"OPTIONS");
  const std::string label=backend=="auto"?"Automatic":backend=="direct3d11"?"Direct3D 11":backend=="direct3d12"?"Direct3D 12":"Vulkan";
  const std::string rows[]{std::string("Fullscreen: ")+(fullscreen?"ON":"OFF"),std::string("Game view: ")+(wide?"WIDE":"ORIGINAL"),std::string("VSync: ")+(vsync?"ON":"OFF / unavailable"),"Renderer: "+label,"Achievements","Back to game"};
  for(int i=0;i<6;++i){SDL_SetRenderDrawColor(renderer_,i==selected?255:204,i==selected?232:194,i==selected?98:164,255);SDL_RenderDebugText(renderer_,x+24,y+60+i*30,(std::string(i==selected?"> ":"  ")+rows[i]).c_str());}
  SDL_SetRenderDrawColor(renderer_,204,194,164,255);SDL_RenderDebugText(renderer_,x+24,y+248,"Arrows / Enter   Esc: back");SDL_RenderDebugText(renderer_,x+24,y+264,"Renderer applies on next launch");SDL_SetRenderScale(renderer_,1,1);
 }
 void achievements(unsigned page,const LocalAchievements& state){
  finish();int w=0,h=0;SDL_GetCurrentRenderOutputSize(renderer_,&w,&h);const float scale=std::max(0.5f,std::floor(std::min(w/580.0f,h/430.0f)));SDL_SetRenderScale(renderer_,scale,scale);
  const float x=(w/scale-560)/2,y=(h/scale-410)/2;panel({x,y,560,410});
  SDL_SetRenderDrawColor(renderer_,255,222,127,255);const auto title="ACHIEVEMENTS  "+std::to_string(state.count())+" / 50";SDL_RenderDebugText(renderer_,x+24,y+24,title.c_str());
  reset_achievements_button={x+440,y+16,96,28};panel(reset_achievements_button);SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,x+452,y+27,"R: RESET");reset_achievements_button.x*=scale;reset_achievements_button.y*=scale;reset_achievements_button.w*=scale;reset_achievements_button.h*=scale;
  for(unsigned row=0;row<6;++row){const auto i=page*6+row;if(i>=local_achievement_list.size())break;const auto& a=local_achievement_list[i];const bool earned=state.earned(i);const float yy=y+58+row*49;
   SDL_FRect icon{x+22,yy+4,32,24};SDL_RenderTexture(renderer_,earned?mini_.get():grey_mini_.get(),nullptr,&icon);
   SDL_SetRenderDrawColor(renderer_,earned?255:130,earned?222:130,earned?127:130,255);SDL_RenderDebugText(renderer_,x+64,yy,a.title);SDL_RenderDebugText(renderer_,x+64,yy+13,a.description);
   SDL_SetRenderDrawColor(renderer_,earned?162:110,earned?224:110,earned?103:110,255);SDL_RenderDebugText(renderer_,x+64,yy+26,earned?"UNLOCKED":a.detectable?"LOCKED":"LOCKED - detection pending");SDL_RenderDebugTextFormat(renderer_,x+474,yy+26,"%upt",a.points);
  }
  SDL_SetRenderDrawColor(renderer_,204,194,164,255);const auto footer="Page "+std::to_string(page+1)+" / 9   Left / Right: browse";SDL_RenderDebugText(renderer_,x+24,y+360,footer.c_str());SDL_RenderDebugText(renderer_,x+24,y+376,(std::to_string(state.points())+" / 1000 points   Esc: back").c_str());SDL_SetRenderScale(renderer_,1,1);
 }
 HostPresentation(SDL_Renderer*r,int height):renderer_(r),height_(height){
  game_.reset(SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,320,height));
  wood_.reset(SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,320,112));
  logo_.reset(SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,320,48));
  if(!game_||!wood_||!logo_)return;
  SDL_SetTextureScaleMode(game_.get(),SDL_SCALEMODE_NEAREST);SDL_SetTextureScaleMode(wood_.get(),SDL_SCALEMODE_NEAREST);
  std::vector<std::uint8_t> pixels(320*112*4);
  for(unsigned i=0;i<320*112;++i){
   const auto f=opening_data::front[i];const auto c=opening_data::colour[(f&15)?f:opening_data::back[i]];
   pixels[i*4]=std::uint8_t(((c>>1)&7)*255/7);pixels[i*4+1]=std::uint8_t(((c>>5)&7)*255/7);pixels[i*4+2]=std::uint8_t(((c>>9)&7)*255/7);pixels[i*4+3]=255;
  }SDL_UpdateTexture(wood_.get(),nullptr,pixels.data(),320*4);
  pixels.resize(320*48*4);
  std::array<bool,320*48> transparent{};std::vector<unsigned> pending;
  const auto admit=[&](unsigned i){const auto ink=opening_data::logo[i];if(!transparent[i]&&(!(ink&15)||opening_data::colour[ink]==0)){transparent[i]=true;pending.push_back(i);}};
  for(unsigned x=0;x<320;++x){admit(x);admit(47*320+x);}for(unsigned y=0;y<48;++y){admit(y*320);admit(y*320+319);}
  while(!pending.empty()){const auto i=pending.back();pending.pop_back();if(i%320)admit(i-1);if(i%320<319)admit(i+1);if(i>=320)admit(i-320);if(i<47*320)admit(i+320);}
  for(unsigned i=0;i<320*48;++i){const auto index=opening_data::logo[i];const auto c=opening_data::colour[index];
   pixels[i*4]=std::uint8_t(((c>>1)&7)*255/7);pixels[i*4+1]=std::uint8_t(((c>>5)&7)*255/7);pixels[i*4+2]=std::uint8_t(((c>>9)&7)*255/7);pixels[i*4+3]=transparent[i]?0:255;
  }SDL_UpdateTexture(logo_.get(),nullptr,pixels.data(),320*4);SDL_SetTextureScaleMode(logo_.get(),SDL_SCALEMODE_NEAREST);SDL_SetTextureBlendMode(logo_.get(),SDL_BLENDMODE_BLEND);
  mini_.reset(SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,32,24));grey_mini_.reset(SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,32,24));
  if(!mini_||!grey_mini_)return;
  pixels.resize(32*24*4);for(unsigned y=0;y<24;++y)for(unsigned x=0;x<32;++x){const auto packed=level1_status_hud_data::portrait[((x/8)*3+y/8)*32+(y&7)*4+(x&7)/2];const auto nibble=(packed>>((x&1)?0:4))&15;const auto c=level1_terrain_data::palette_words[32+nibble];const auto at=(y*32+x)*4;pixels[at]=((c>>1)&7)*255/7;pixels[at+1]=((c>>5)&7)*255/7;pixels[at+2]=((c>>9)&7)*255/7;pixels[at+3]=nibble?255:0;}
  SDL_UpdateTexture(mini_.get(),nullptr,pixels.data(),32*4);for(unsigned i=0;i<32*24;++i){const auto grey=std::uint8_t((pixels[i*4]*3+pixels[i*4+1]*6+pixels[i*4+2])/20);pixels[i*4]=pixels[i*4+1]=pixels[i*4+2]=grey;}SDL_UpdateTexture(grey_mini_.get(),nullptr,pixels.data(),32*4);
  for(auto*t:{mini_.get(),grey_mini_.get()}){SDL_SetTextureScaleMode(t,SDL_SCALEMODE_NEAREST);SDL_SetTextureBlendMode(t,SDL_BLENDMODE_BLEND);}
 }
 void select_width(int width){if(width==width_)return;game_.reset(SDL_CreateTexture(renderer_,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,width,height_));if(!game_)throw std::runtime_error("Game viewport allocation failed");width_=width;SDL_SetTextureScaleMode(game_.get(),SDL_SCALEMODE_NEAREST);}
 bool valid()const{return game_&&wood_&&logo_&&mini_&&grey_mini_;}
 void finish(){
  SDL_SetRenderTarget(renderer_,nullptr);SDL_SetRenderLogicalPresentation(renderer_,0,0,SDL_LOGICAL_PRESENTATION_DISABLED);
  int w=0,h=0;SDL_GetCurrentRenderOutputSize(renderer_,&w,&h);
  SDL_SetRenderDrawColor(renderer_,0,0,0,255);SDL_RenderClear(renderer_);
  const float spacing=std::max(32.0f,float(std::min(w,h))/11);
  SDL_SetRenderDrawColor(renderer_,57,57,57,255);
  for(float x=float(w)/2-spacing/2;x<w;x+=spacing)SDL_RenderLine(renderer_,x,0,x,float(h));
  for(float x=float(w)/2-spacing*1.5f;x>=0;x-=spacing)SDL_RenderLine(renderer_,x,0,x,float(h));
  for(float y=float(h)/2-spacing/2;y<h;y+=spacing)SDL_RenderLine(renderer_,0,y,float(w),y);
  for(float y=float(h)/2-spacing*1.5f;y>=0;y-=spacing)SDL_RenderLine(renderer_,0,y,float(w),y);
  float scale=std::min(float(w-48)/(width_+24),float(h-48)/(height_+88));
  if(scale>=1)scale=std::floor(scale);scale=std::max(0.1f,scale);
  const float border=12*scale,ow=(width_+24)*scale,oh=(height_+24)*scale,left=(w-ow)/2,top=(h-oh-64*scale)/2+64*scale;
  const SDL_FRect view{left+border,top+border,width_*scale,height_*scale};SDL_RenderTexture(renderer_,game_.get(),nullptr,&view);
  const SDL_FRect logo_view{(w-320*scale)/2,top-64*scale,320*scale,48*scale};SDL_RenderTexture(renderer_,logo_.get(),nullptr,&logo_view);
  const std::array<float,4> sx{0,12,308,320},sy{0,12,100,112};
  const std::array<float,4> dx{left,left+border,left+ow-border,left+ow},dy{top,top+border,top+oh-border,top+oh};
  for(unsigned y=0;y<3;++y)for(unsigned x=0;x<3;++x){if(x==1&&y==1)continue;
   const SDL_FRect source{sx[x],sy[y],sx[x+1]-sx[x],sy[y+1]-sy[y]},target{dx[x],dy[y],dx[x+1]-dx[x],dy[y+1]-dy[y]};
   SDL_RenderTexture(renderer_,wood_.get(),&source,&target);
  }
  const float bs=std::max(1.0f,std::floor(std::min(w,h)/600.0f));SDL_SetRenderScale(renderer_,bs,bs);
  options_button={float(w)/bs-124,12,112,32};panel(options_button);SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,options_button.x+16,options_button.y+12,"OPTIONS F8");
  options_button.x*=bs;options_button.y*=bs;options_button.w*=bs;options_button.h*=bs;SDL_SetRenderScale(renderer_,1,1);
  draw_unlock(SDL_GetTicks());
  if(debug_flight){const SDL_FRect box{16,12,328,36};panel(box);SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,28,26,"DEBUG F2: INVINCIBLE + FREE FLIGHT");}
  if(SDL_GetTicks()<capture_notice_until){const SDL_FRect box{16,float(h)-52,248,36};panel(box);SDL_SetRenderDrawColor(renderer_,255,222,127,255);SDL_RenderDebugText(renderer_,box.x+12,box.y+14,capture_notice.c_str());}
 }
 struct Frame {
  HostPresentation& host;
  explicit Frame(HostPresentation&h,int width=320):host(h){host.select_width(width);SDL_SetRenderTarget(host.renderer_,host.game_.get());SDL_SetRenderViewport(host.renderer_,nullptr);}
  ~Frame(){host.finish();}Frame(const Frame&)=delete;
 };
};
}
