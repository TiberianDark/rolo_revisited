#pragma once
#include <stdexcept>
#include "core/ending_animation_data.hpp"
#include "core/ending_data.hpp"
#include "core/actor_animation.hpp"
#include "core/actor_phase_ending.hpp"
#include "core/campaign_percentage.hpp"
#include "core/local_achievements.hpp"
#include "core/opening_sequence.hpp"
#include <string>
#include <cctype>
namespace rolo {
// Native terminal scene: original actor walk, palette gates, ending choice and text.
struct EndingSequence final:ActorAnimationSound,EndingCompletionServices {
 enum class Phase{Intro,Good,Bad,Title};Phase phase=Phase::Intro;
 std::array<ActorState,4> actors{};std::array<std::uint16_t,64> palette=opening_data::colour;
 std::array<PaletteEffect,4> effects{};AnimationRandom random{3};std::array<std::uint8_t,80> flags{};
 unsigned ticks=0,text_ticks=0;std::uint16_t timer=500,sound=0xffff;bool fade_started=false,eligible=true,award_sent=false;
 std::uint32_t native_state=0x9be2;AchievementBits events=0;
 explicit EndingSequence(const std::array<std::uint8_t,80>& f,bool admitted=true):flags(f),eligible(admitted){
  constexpr unsigned definitions[]{0x1575e,0x15780,0x13ecc,0x13eee};
  for(unsigned i=0;i<4;++i){auto&a=actors[i];a.longword(4,definitions[i]);a.word(12,i<2?250:478);a.word(16,241);a.word(70,i<2?0:4);a.word(72,65535);a.byte(118,i<2?0:255);}
  animate();
 }
 void actor_animation_sound(std::uint16_t v)override{sound=v;}
 std::uint16_t completion_percent()override{return campaign_completion_percentage(flags);}
 void fade_black()override{}
 void animate(){for(auto&a:actors){const auto status=update_actor_animation_from_definition(a,a.longword(4),ending_animation_data::data,this,&random);if(status!=AnimationResult::Ok&&status!=AnimationResult::Retired)throw std::runtime_error("Ending actor animation data");}}
 void begin_effect(unsigned bank,std::span<const std::uint16_t> target){initialize_palette_effect(effects[bank],std::span<const std::uint16_t>(palette).subspan(bank*16,16),target,0);}
 void select_ending(){ending_completion_state(native_state,*this);phase=native_state==0x9a88?Phase::Good:Phase::Bad;text_ticks=0;
  if(phase==Phase::Good){palette=opening_data::photo;sound=3;}else{palette=opening_data::colour;begin_effect(1,ending_data::bad_palette);}
  if(eligible&&!award_sent){events|=achievement_bit(phase==Phase::Good?22:23);award_sent=true;}
 }
 AchievementBits take_events(){const auto e=events;events=0;return e;}
 std::span<const std::uint8_t> text_data()const{return phase==Phase::Good?std::span<const std::uint8_t>(ending_data::good_text):std::span<const std::uint8_t>(ending_data::bad_text);}
 unsigned line_count()const{unsigned n=0;for(auto c:text_data())if(c==1)++n;return n;}
 unsigned text_duration()const{return (line_count()*16+224)*4;}
 void step(bool start=false){++ticks;for(unsigned b=0;b<4;++b)advance_palette_effect(effects[b],std::span<std::uint16_t>(palette).subspan(b*16,16));
  if(phase==Phase::Title)return;
  if(phase==Phase::Intro){auto&body=actors[2];const auto x=body.word(12);body.word(12,x>322?x-1:322);body.word(70,x>323?4:92);if(body.word(12)==322)actors[1].byte(46,255);actors[3].word(12,body.word(12));actors[3].word(70,body.word(70));animate();
   if(timer){--timer;return;}if(!fade_started){for(unsigned b=0;b<4;++b)begin_effect(b,b==2?std::span<const std::uint16_t>(ending_data::black):std::span<const std::uint16_t>(ending_data::white));fade_started=true;return;}if(!effects[3].active)select_ending();return;}
  ++text_ticks;if(phase==Phase::Bad)animate();
  // Both stories are shown completely; Start confirms the final page.
  if(text_ticks>=text_duration()&&(start||phase==Phase::Bad)){phase=Phase::Title;native_state=0x165e;sound=2;}
 }
 std::vector<std::uint8_t> raster()const{
  if(phase==Phase::Title){OpeningSequence title;title.phase=OpeningSequence::Phase::Title;title.phase_ticks=60;title.colours.colours=opening_data::photo;return title.raster();}
  std::vector<std::uint8_t> out(320*224*4);for(unsigned i=0;i<320*224;++i)out[i*4+3]=255;
  auto layer=[&](const auto&image,int base_y,bool transparent){for(unsigned i=0;i<image.size();++i){const int at=int(i)+base_y*320;if(at>=0&&at<320*224&&(!transparent||(image[i]&15)))OpeningSequence::put_colour(out,at,palette[image[i]]);}};
  layer(opening_data::back,48,false);
  for(unsigned i:{0u,1u,2u,3u}){const auto&a=actors[i];if(a.byte(125)&2)continue;const bool face=a.byte(118)&8;const int x=int(a.word(12))-100+(face?-signed_word(a.word(32)):signed_word(a.word(32)))-a.word(36)/2,y=int(a.word(16))-100+signed_word(a.word(34))-a.word(38);
   for(const auto&s:ending_data::sprites)if(s.source==a.longword(28)&&s.width==a.word(36)&&s.height==a.word(38)){for(unsigned py=0;py<s.height;++py)for(unsigned px=0;px<s.width;++px){const int dx=x+px,dy=y+py;const auto ink=ending_data::pixels[s.offset+py*s.width+((a.byte(119)&8)?s.width-1-px:px)];if(ink&&dx>=0&&dx<320&&dy>=48&&dy<160)OpeningSequence::put_colour(out,dy*320+dx,(phase==Phase::Good?opening_data::colour[32+ink]:palette[32+ink]));}break;}}
  layer(opening_data::front,48,true);layer(opening_data::logo,0,true);
  if(phase==Phase::Good||phase==Phase::Bad){std::string line;unsigned number=0;const int scroll=int(text_ticks/4);for(auto c:text_data()){if(c==0||c==2)break;if(c==1){const int y=224+int(number++)*16-scroll;if(y>=164&&y<216)OpeningSequence::text(out,line.c_str(),(320-int(line.size())*8)/2,y,phase==Phase::Good?0x0e0:0xeee);line.clear();}else line+=char(std::toupper(c));}
   if(phase==Phase::Good&&text_ticks>=text_duration())OpeningSequence::text(out,"PRESS START",116,208,0x0e0);
  }return out;
 }
};
}




