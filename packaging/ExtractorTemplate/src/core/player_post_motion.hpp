#pragma once
#include "core/terrain_display.hpp"
namespace rolo {
struct PlayerPostMotionServices:TerrainDisplayServices {
    virtual void post_motion_sound(std::uint16_t command)=0;
    virtual std::uint16_t mutation_table_word(std::uint16_t relative)=0; //8D8E-relative immutable data
    virtual std::uint16_t mutation_backing_word(std::uint16_t offset)=0;
    virtual void mutation_backing_word(std::uint16_t offset,std::uint16_t value)=0;
    virtual void mutation_map_word(std::int16_t relative,std::uint16_t value)=0; //F32C + signed metadata
};
// $8D4E writes unmodified mapped quad patterns, then replacement|oldflags to backing.
inline void post_motion_replace_cell(std::uint16_t x,std::uint16_t y,std::uint16_t replacement,
        std::uint16_t flags,PlayerPostMotionServices& services){
    const auto patterns=services.terrain_quad_patterns(replacement);
    const auto top=static_cast<std::uint16_t>(((x+y)*2)&0x0f7c);
    services.terrain_name_row(top,patterns[0],patterns[1]);
    services.terrain_name_row(static_cast<std::uint16_t>(top|128),patterns[2],patterns[3]);
    services.mutation_backing_word(static_cast<std::uint16_t>(x+y),static_cast<std::uint16_t>(replacement|flags));
}
// $8C88..$8D4E: controlled type8 only; latch consumed and sound issued even on table miss.
inline void player_post_motion_terrain(ActorState& actor,std::uint16_t controlled_type,
        const std::uint8_t& bank,PlayerPostMotionServices& services){
    if(controlled_type!=8||!actor.byte(53))return;
    actor.byte(53,0);services.post_motion_sound(12);
    const bool facing=(actor.byte(118)&8)!=0;
    const auto relative=services.mutation_table_word(static_cast<std::uint16_t>(bank*4+(facing?2:0)));
    if(signed_word(relative)<0)return;
    const auto x=static_cast<std::uint16_t>((static_cast<std::uint16_t>(actor.word(12)+(facing?-8:8))&0x3f0)>>3);
    auto y=static_cast<std::uint16_t>((static_cast<std::uint16_t>(actor.word(16)-8)&0x3f0)<<3);
    const auto original=services.mutation_backing_word(static_cast<std::uint16_t>(x+y));
    const auto count=services.mutation_table_word(relative);
    if(signed_word(count)<0)throw std::out_of_range("Unproved negative post-motion table count");
    for(unsigned i=0;i<=count;++i){
        const auto entry=static_cast<std::uint16_t>(relative+2+i*8);
        if(services.mutation_table_word(entry)!=(original&511))continue;
        const auto flags=static_cast<std::uint16_t>(original&0xfe00);
        post_motion_replace_cell(x,y,services.mutation_table_word(static_cast<std::uint16_t>(entry+2)),flags,services);
        y=static_cast<std::uint16_t>((y-128)&0x1f80);
        post_motion_replace_cell(x,y,services.mutation_table_word(static_cast<std::uint16_t>(entry+4)),flags,services);
        const auto metadata=services.mutation_backing_word(static_cast<std::uint16_t>(x+y+8192));
        services.mutation_map_word(signed_word(metadata),services.mutation_table_word(static_cast<std::uint16_t>(entry+6)));
        return;
    }
}
struct NativePostMotionStorageServices:PlayerPostMotionServices {
    std::span<const std::uint8_t> table;std::span<std::uint8_t> backing,map;
    const std::size_t& map_origin;TerrainDisplayServices& display;
    NativePostMotionStorageServices(std::span<const std::uint8_t> t,std::span<std::uint8_t> ring,
            std::span<std::uint8_t> data,const std::size_t& origin,TerrainDisplayServices& d)
        :table(t),backing(ring),map(data),map_origin(origin),display(d){}
    std::uint16_t mutation_table_word(std::uint16_t offset)override{
        if(static_cast<std::size_t>(offset)+2>table.size())throw std::out_of_range("Unproved mutation table extent");
        return static_cast<std::uint16_t>((table[offset]<<8)|table[offset+1]);
    }
    std::uint16_t mutation_backing_word(std::uint16_t offset)override{
        if(static_cast<std::size_t>(offset)+2>backing.size())throw std::out_of_range("Mutation backing read extent");
        return static_cast<std::uint16_t>((backing[offset]<<8)|backing[offset+1]);
    }
    void mutation_backing_word(std::uint16_t offset,std::uint16_t value)override{
        if(static_cast<std::size_t>(offset)+2>backing.size())throw std::out_of_range("Mutation backing write extent");
        backing[offset]=static_cast<std::uint8_t>(value>>8);backing[offset+1]=static_cast<std::uint8_t>(value);
    }
    void mutation_map_word(std::int16_t offset,std::uint16_t value)override{
        const auto target=static_cast<std::int64_t>(map_origin)+offset;
        if(target<0||static_cast<std::uint64_t>(target)+2>map.size())throw std::out_of_range("Mutation MAP write extent");
        map[static_cast<std::size_t>(target)]=static_cast<std::uint8_t>(value>>8);map[static_cast<std::size_t>(target)+1]=static_cast<std::uint8_t>(value);
    }
    std::array<std::uint16_t,4> terrain_quad_patterns(std::uint16_t index)override{return display.terrain_quad_patterns(index);}
    void terrain_name_row(std::uint16_t offset,std::uint16_t left,std::uint16_t right)override{display.terrain_name_row(offset,left,right);}
};
}
