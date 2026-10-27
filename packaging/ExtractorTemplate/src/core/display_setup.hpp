#pragma once
#include "core/plane_scroll.hpp"
namespace rolo {
struct GraphicsTransferRequest {std::uint32_t source{},destination{},control{};std::uint16_t words{};bool operator==(const GraphicsTransferRequest&)const=default;};
struct GraphicsFillRequest {std::uint32_t destination{},control{};std::uint16_t count{};std::uint8_t value{};bool operator==(const GraphicsFillRequest&)const=default;};
struct DisplaySetupServices {
    virtual ~DisplaySetupServices()=default;
    virtual void graphics_transfer(GraphicsTransferRequest)=0; //2466/2468 typed DMA request.
    virtual void graphics_fill(GraphicsFillRequest)=0; //26BC typed fill request.
    virtual void prepare_name_increment_two()=0;
    virtual void name_destination_command(std::uint32_t)=0;
    virtual void name_data_word(std::uint16_t)=0;
};
// $2694: destination/control encoding and signed predecrement gate.
inline void fill_name_table_words(std::uint16_t value,std::uint32_t destination,
        std::uint16_t count,std::uint32_t control,DisplaySetupServices& services){
    services.prepare_name_increment_two();const auto low=static_cast<std::uint16_t>(destination);
    const auto command=(std::uint32_t(low&0x3fff)<<16)|((low>>14)&3)|control;
    services.name_destination_command(command);
    auto remaining=static_cast<std::uint16_t>(count-1);if(signed_word(remaining)<0)return;
    do{services.name_data_word(value);remaining=static_cast<std::uint16_t>(remaining-1);}while(remaining!=0xffff);
}
// $684E/$6864: byte fill requests, device completion remains a service.
inline void clear_foreground_names(DisplaySetupServices& s){s.graphics_fill({0xc000,0x40000080,0x1000,0});}
inline void clear_background_names(DisplaySetupServices& s){s.graphics_fill({0xe000,0x40000080,0x1000,0});}
// $687A/$6894: even the zero-count path publishes increment/destination.
inline void initialize_menu_names(DisplaySetupServices&s){fill_name_table_words(0xe000,0xd000,0x700,0x40000000,s);}
inline void prepare_empty_menu_names(DisplaySetupServices&s){fill_name_table_words(0xe000,0xd000,0,0x40000000,s);}
// $68AE clears exactly first eight native SAT bytes before requesting4 words.
inline void clear_sprite_table(std::span<std::uint8_t> sat,DisplaySetupServices&s){
    if(sat.size()<8)throw std::out_of_range("Native SAT clear extent");
    for(unsigned i=0;i<8;++i)sat[i]=0;s.graphics_transfer({0xffffc9bc,0xf400,0x40000080,4});
}
inline void publish_resident_graphics(DisplaySetupServices&s){s.graphics_transfer({0x27040,0xf680,0x40000000,0x480});} //31B8
inline void publish_palette_transfer(std::uint32_t source,std::uint32_t destination,DisplaySetupServices&s){s.graphics_transfer({source,destination,0xc0000000,15});} //2FE8
struct NativePublicationQueue {std::span<std::uint8_t> bytes;std::uint32_t cursor{};};
inline void reset_publication_queue(NativePublicationQueue&q,std::uint32_t base){
    if(q.bytes.size()<4)throw std::out_of_range("Native display queue extent");
    for(unsigned i=0;i<4;++i)q.bytes[i]=0;q.cursor=base;
}
inline void reset_pattern_publication_queue(NativePublicationQueue&q){reset_publication_queue(q,0xffffeb56);} //2674
inline void reset_secondary_publication_queue(NativePublicationQueue&q){reset_publication_queue(q,0xffffe448);} //2684
// $6AC6 really calls6960 twice; the second call is not vertical publication.
inline void reset_plane_scroll(std::uint8_t& mode,std::uint16_t& fx,std::uint16_t& bx,
        std::uint16_t& fy,std::uint16_t& by,PlaneScrollServices& services){
    mode=0;fx=0;bx=0;publish_horizontal_scroll(mode,{fx,bx,fy,by},services);
    fy=0;by=0;publish_horizontal_scroll(mode,{fx,bx,fy,by},services);
}
}
